"""Command-line entry point."""

from __future__ import annotations

import argparse
import errno
import os
import sys
import tempfile
import time
from datetime import date

from . import __version__
from .baseline import dump_baseline, load_baseline, new_findings
from .config import apply_ignores, load_config
from .drills import KINDS, RESULTS, _entry, apply, dump_log, load_log
from .loader import InputError, load
from .report import FORMATS
from .roi import export
from .rules import SEVERITIES, at_or_above, check


def _diagnostic_text(value: object) -> str:
    return "".join(c if c.isprintable() else f"\\x{ord(c):02x}" for c in str(value))


def _error(message: object, file: str = "<cli>", line: int = 0) -> int:
    """Emit one stable diagnostic; zero denotes an unavailable source line."""
    if isinstance(message, InputError):
        file = message.path or file
        line = message.line
    text = str(message)
    if text.startswith(file + ": "):
        text = text[len(file) + 2:]
    print(f"resilint: error: {_diagnostic_text(file)}:{line}: {_diagnostic_text(text)}",
          file=sys.stderr)
    return 2


def _within(path: str, root: str) -> bool:
    real, base = os.path.realpath(path), os.path.realpath(root)
    return os.path.commonpath([real, base]) == base


def check_target(path: str, input_file: str | None = None,
                 option: str = "--output") -> str | None:
    """Validate an output path (root, not the input, not a symlink). Error message or None."""
    root = os.environ.get("RESILINT_OUTPUT_ROOT")
    try:
        if root and not _within(path, root):
            return f"output path {path} resolves outside {root}"
        if input_file and os.path.exists(path) and os.path.samefile(path, input_file):
            return f"{option} must not be the input file"
        if os.path.islink(path):
            return f"output path {path} must not be a symlink"
    except (OSError, ValueError) as e:
        return f"cannot write {path} ({getattr(e, 'strerror', None) or e})"
    return None


def write_file(path: str, content: str, input_file: str | None = None,
               exclusive: bool = False) -> str | None:
    """Write without following symlinks. Returns an error message, or None on success."""
    err = check_target(path, input_file)
    if err:
        return err
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
        if exclusive:
            flags |= os.O_EXCL
        fd = os.open(path, flags, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
    except (OSError, ValueError) as e:
        return f"cannot write {path} ({getattr(e, 'strerror', None) or e})"
    return None


def _export(args) -> int:
    try:
        register = load(args.file, csv_delimiter=args.csv_delimiter)
    except InputError as e:
        return _error(e, args.file)
    out = os.path.normpath(args.out_dir)
    if os.path.islink(out) or not os.path.isdir(out):
        return _error("--out-dir must be an existing directory, not a symlink", out)
    root = os.environ.get("RESILINT_OUTPUT_ROOT")
    if root and not _within(out, root):
        return _error(f"--out-dir resolves outside {root}", out)
    files = export(register)
    if not args.force:
        existing = [n for n in files if os.path.lexists(os.path.join(out, n))]
        if existing:
            return _error(f"{', '.join(existing)} already exist in {out}; "
                          "use --force to overwrite", out)
    for name in files:  # validate every target before writing any
        err = check_target(os.path.join(out, name), args.file)
        if err:
            return _error(err, os.path.join(out, name))
    for name, content in files.items():
        err = write_file(os.path.join(out, name), content, args.file,
                         exclusive=not args.force)
        if err:
            return _error(err, os.path.join(out, name))
    print(f"wrote draft RoI export to {out} (draft mapping, not legal advice)")
    return 0


def _try_lock(fd: int) -> None:
    if sys.platform == "win32":
        import msvcrt
        # Every writer locks byte zero, even when the sidecar is empty.
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)


def _lock(path: str) -> int | str:
    """Exclusive non-blocking lock on a sidecar file; waits up to ~2 s. fd or error string."""
    flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o644)
    except OSError as e:
        return f"cannot open lock {path} ({e.strerror})"
    for _ in range(20):
        try:
            _try_lock(fd)
            return fd
        except OSError as e:
            if e.errno not in (errno.EACCES, errno.EAGAIN, errno.EDEADLK):
                os.close(fd)
                return f"cannot lock {path} ({e.strerror})"
            time.sleep(0.1)
    os.close(fd)
    return f"drill log is locked by another process ({path})"


def _replace(path: str, content: str) -> str | None:
    """Write to a temp file in the same directory, then atomically replace path."""
    d = os.path.dirname(os.path.abspath(path))
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(prefix=".drills-", suffix=".tmp", dir=d)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
        tmp = None
    except OSError as e:
        return f"cannot write {path} ({e.strerror})"
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)
    return None


def _drill(args) -> int:
    log = args.log or os.path.join(os.path.dirname(args.file) or ".", "drills.yaml")
    lock_path = log + ".lock"
    for path in (log, lock_path):
        err = check_target(path, args.file, "--log")
        if err:
            return _error(err, path)
    lock = _lock(lock_path)
    if isinstance(lock, str):
        return _error(lock, lock_path)
    try:
        try:
            register = load(args.file, csv_delimiter=args.csv_delimiter)
            ids = {v["id"] for v in register["vendors"]}
            drills = load_log(log, missing_ok=True, vendor_ids=ids)
            new = _entry({"vendor": args.vendor, "date": args.date, "kind": args.kind,
                          "result": args.result, "notes": args.notes}, "drill", ids)
        except InputError as e:
            return _error(e, log)
        err = check_target(log, args.file, "--log") or _replace(log, dump_log(drills + [new]))
        if err:
            return _error(err, log)
    finally:
        os.close(lock)
    note = " (last-tested date updated)" if new["result"] != "fail" else ""
    print(f"recorded {new['kind']} {new['result']} for {new['vendor']} on "
          f"{new['date'].isoformat()} in {log}{note}")
    return 0


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        sys.exit(_error(message))


def main(argv=None, *, _summary: dict[str, str] | None = None) -> int:
    ap = _Parser(prog="resilint", description="Offline vendor resilience checks.")
    ap.add_argument("--version", action="version", version=f"resilint {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="check a vendor register (YAML or CSV)")
    c.add_argument("file")
    c.add_argument("--format", choices=sorted(FORMATS), default="text")
    c.add_argument("--fail-on", choices=SEVERITIES)
    c.add_argument("--stale-days", type=int)
    c.add_argument("--max-critical", type=int,
                   help="concentration threshold: critical processes per vendor")
    c.add_argument("--contact-days", type=int,
                   help="max age in days of a vendor's contacts_verified date")
    c.add_argument("--output", metavar="FILE", help="write the report to FILE instead of stdout")
    c.add_argument("--config", metavar="FILE", help="rule settings (default: cwd/.resilint.yaml)")
    baseline = c.add_mutually_exclusive_group()
    baseline.add_argument("--baseline", metavar="FILE", help="report only findings absent from FILE")
    baseline.add_argument("--write-baseline", metavar="FILE", help="save current finding identities")
    e = sub.add_parser("export-roi", help="draft export toward DORA register-of-information templates")
    e.add_argument("file")
    e.add_argument("--out-dir", required=True, help="existing directory to write CSV files into")
    c.add_argument("--drills", metavar="LOG", help="drill log to apply (from `drill record`)")
    d = sub.add_parser("drill", help="drill records")
    dsub = d.add_subparsers(dest="drill_cmd", required=True)
    r = dsub.add_parser("record", help="record a tabletop or test result for a vendor")
    r.add_argument("file", help="vendor register (used to validate the vendor id)")
    r.add_argument("--vendor", required=True)
    r.add_argument("--date", default=date.today().isoformat(), help="ISO date (default today)")
    r.add_argument("--kind", choices=KINDS, required=True)
    r.add_argument("--result", choices=RESULTS, required=True)
    r.add_argument("--notes", default=None)
    r.add_argument("--log", help="drill log file (default drills.yaml next to the register)")
    e.add_argument("--force", action="store_true", help="overwrite existing export files")
    for parser in (c, e, r):
        parser.add_argument("--csv-delimiter", choices=(",", ";"), default=",",
                            help="CSV field separator (default: comma; ignored for YAML)")
    args = ap.parse_args(argv)
    if args.cmd == "drill":
        return _drill(args)
    if args.cmd == "export-roi":
        return _export(args)
    if args.baseline == "" or args.write_baseline == "":
        return _error("baseline path must not be empty")
    try:
        settings = load_config(args.config)
    except InputError as error:
        return _error(error)
    for key in ("fail_on", "stale_days", "contact_days", "max_critical"):
        if getattr(args, key) is None:
            setattr(args, key, getattr(settings, key))
    if args.stale_days < 0 or args.max_critical < 0 or args.contact_days < 0:
        return _error("thresholds must be non-negative")
    try:
        register = load(args.file, csv_delimiter=args.csv_delimiter)
        if args.drills:
            apply(register, load_log(args.drills))
    except InputError as e:
        return _error(e, args.file)
    findings = check(register, stale_days=args.stale_days, max_critical=args.max_critical,
                     contact_days=args.contact_days)
    findings = apply_ignores(findings, settings)
    if args.baseline:
        try:
            findings = new_findings(findings, load_baseline(args.baseline))
        except InputError as error:
            return _error(error)
    report = FORMATS[args.format](findings, register)
    inputs = [p for p in (args.file, settings.source, args.drills, args.baseline) if p]
    outputs = [p for p in (args.output, args.write_baseline) if p]
    for output in outputs:
        for source in inputs:
            err = check_target(output, source)
            if err:
                return _error(err, output)
    if args.output and args.write_baseline:
        try:
            same = (os.path.normcase(os.path.realpath(args.output)) ==
                    os.path.normcase(os.path.realpath(args.write_baseline)))
            if os.path.exists(args.output) and os.path.exists(args.write_baseline):
                same = same or os.path.samefile(args.output, args.write_baseline)
        except (OSError, ValueError) as error:
            return _error(f"cannot compare output paths ({error.__class__.__name__})", args.output)
        if same:
            return _error("report and baseline destinations must differ", args.output)
    if args.write_baseline:
        try:
            snapshot = dump_baseline(findings)
        except InputError as error:
            return _error(error, args.write_baseline)
        err = write_file(args.write_baseline, snapshot, args.file)
        if err:
            return _error(err, args.write_baseline)
    if args.output:
        err = write_file(args.output, report + "\n", args.file)
        if err:
            return _error(err, args.output)
    else:
        print(report)
    if _summary is not None:
        _summary.update(findings=str(len(findings)), highest_severity=max(
            (f.severity for f in findings), key=SEVERITIES.index, default="none"))
    return 0 if args.write_baseline else (1 if at_or_above(findings, args.fail_on) else 0)


if __name__ == "__main__":
    sys.exit(main())
