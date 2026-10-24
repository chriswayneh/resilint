"""Command-line entry point."""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date

from . import __version__
from .drills import KINDS, RESULTS, _entry, apply, dump_log, load_log
from .loader import InputError, load
from .report import FORMATS
from .roi import export
from .rules import SEVERITIES, at_or_above, check


def _within(path: str, root: str) -> bool:
    real, base = os.path.realpath(path), os.path.realpath(root)
    return os.path.commonpath([real, base]) == base


def check_target(path: str, input_file: str | None = None) -> str | None:
    """Validate an output path (root, not the input, not a symlink). Error message or None."""
    root = os.environ.get("RESILINT_OUTPUT_ROOT")
    try:
        if root and not _within(path, root):
            return f"output path {path} resolves outside {root}"
        if input_file and os.path.exists(path) and os.path.samefile(path, input_file):
            return "--output must not be the input file"
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
        register = load(args.file)
    except InputError as e:
        print(f"resilint: error: {e}", file=sys.stderr)
        return 2
    out = os.path.normpath(args.out_dir)
    if os.path.islink(out) or not os.path.isdir(out):
        print("resilint: error: --out-dir must be an existing directory, not a symlink",
              file=sys.stderr)
        return 2
    root = os.environ.get("RESILINT_OUTPUT_ROOT")
    if root and not _within(out, root):
        print(f"resilint: error: --out-dir resolves outside {root}", file=sys.stderr)
        return 2
    files = export(register)
    if not args.force:
        existing = [n for n in files if os.path.lexists(os.path.join(out, n))]
        if existing:
            print(f"resilint: error: {', '.join(existing)} already exist in {out}; "
                  "use --force to overwrite", file=sys.stderr)
            return 2
    for name in files:  # validate every target before writing any
        err = check_target(os.path.join(out, name), args.file)
        if err:
            print(f"resilint: error: {err}", file=sys.stderr)
            return 2
    for name, content in files.items():
        err = write_file(os.path.join(out, name), content, args.file,
                         exclusive=not args.force)
        if err:
            print(f"resilint: error: {err}", file=sys.stderr)
            return 2
    print(f"wrote draft RoI export to {out} (draft mapping, not legal advice)")
    return 0


def _drill(args) -> int:
    log = args.log or os.path.join(os.path.dirname(args.file) or ".", "drills.yaml")
    try:
        register = load(args.file)
        drills = load_log(log, missing_ok=True)
        new = _entry({"vendor": args.vendor, "date": args.date, "kind": args.kind,
                      "result": args.result, "notes": args.notes}, "drill",
                     {v["id"] for v in register["vendors"]})
    except InputError as e:
        print(f"resilint: error: {e}", file=sys.stderr)
        return 2
    err = write_file(log, dump_log(drills + [new]), args.file)
    if err:
        print(f"resilint: error: {err}", file=sys.stderr)
        return 2
    note = " (last-tested date updated)" if new["result"] != "fail" else ""
    print(f"recorded {new['kind']} {new['result']} for {new['vendor']} on "
          f"{new['date'].isoformat()} in {log}{note}")
    return 0


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"resilint: error: {message}", file=sys.stderr)
        sys.exit(2)


def main(argv=None) -> int:
    ap = _Parser(prog="resilint", description="Offline vendor resilience checks.")
    ap.add_argument("--version", action="version", version=f"resilint {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="check a vendor register (YAML or CSV)")
    c.add_argument("file")
    c.add_argument("--format", choices=sorted(FORMATS), default="text")
    c.add_argument("--fail-on", choices=SEVERITIES, default="high")
    c.add_argument("--stale-days", type=int, default=365)
    c.add_argument("--max-critical", type=int, default=3,
                   help="concentration threshold: critical processes per vendor")
    c.add_argument("--contact-days", type=int, default=180,
                   help="max age in days of a vendor's contacts_verified date")
    c.add_argument("--output", metavar="FILE", help="write the report to FILE instead of stdout")
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
    args = ap.parse_args(argv)
    if args.cmd == "drill":
        return _drill(args)
    if args.cmd == "export-roi":
        return _export(args)
    if args.stale_days < 0 or args.max_critical < 0 or args.contact_days < 0:
        print("resilint: error: thresholds must be non-negative", file=sys.stderr)
        return 2
    try:
        register = load(args.file)
        if args.drills:
            apply(register, load_log(args.drills))
    except InputError as e:
        print(f"resilint: error: {e}", file=sys.stderr)
        return 2
    findings = check(register, stale_days=args.stale_days, max_critical=args.max_critical,
                     contact_days=args.contact_days)
    report = FORMATS[args.format](findings, register)
    if args.output:
        err = write_file(args.output, report + "\n", args.file)
        if err:
            print(f"resilint: error: {err}", file=sys.stderr)
            return 2
    else:
        print(report)
    return 1 if at_or_above(findings, args.fail_on) else 0


if __name__ == "__main__":
    sys.exit(main())
