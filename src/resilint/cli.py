"""Command-line entry point."""

from __future__ import annotations

import argparse
import os
import sys

from . import __version__
from .loader import InputError, load
from .report import FORMATS
from .rules import SEVERITIES, at_or_above, check


def _within(path: str, root: str) -> bool:
    real, base = os.path.realpath(path), os.path.realpath(root)
    return os.path.commonpath([real, base]) == base


def write_file(path: str, content: str, input_file: str | None = None) -> str | None:
    """Write without following symlinks. Returns an error message, or None on success."""
    root = os.environ.get("RESILINT_OUTPUT_ROOT")
    try:
        if root and not _within(path, root):
            return f"output path {path} resolves outside {root}"
        if input_file and os.path.exists(path) and os.path.samefile(path, input_file):
            return "--output must not be the input file"
        if os.path.islink(path):
            return f"output path {path} must not be a symlink"
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(path, flags, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(content)
    except (OSError, ValueError) as e:
        return f"cannot write {path} ({getattr(e, 'strerror', None) or e})"
    return None


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
    args = ap.parse_args(argv)
    if args.stale_days < 0 or args.max_critical < 0 or args.contact_days < 0:
        print("resilint: error: thresholds must be non-negative", file=sys.stderr)
        return 2
    try:
        register = load(args.file)
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
