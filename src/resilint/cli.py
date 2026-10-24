"""Command-line entry point."""

from __future__ import annotations

import argparse
import os
import sys

from . import __version__
from .loader import InputError, load
from .report import FORMATS
from .rules import SEVERITIES, at_or_above, check


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
        try:
            if os.path.exists(args.output) and os.path.samefile(args.output, args.file):
                print("resilint: error: --output must not be the input file", file=sys.stderr)
                return 2
            with open(args.output, "w", encoding="utf-8") as fh:
                fh.write(report + "\n")
        except OSError as e:
            print(f"resilint: error: cannot write {args.output} ({e.strerror})", file=sys.stderr)
            return 2
    else:
        print(report)
    return 1 if at_or_above(findings, args.fail_on) else 0


if __name__ == "__main__":
    sys.exit(main())
