"""Command-line entry point."""

from __future__ import annotations

import argparse
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
    args = ap.parse_args(argv)
    if args.stale_days < 0 or args.max_critical < 0:
        print("resilint: error: thresholds must be non-negative", file=sys.stderr)
        return 2
    try:
        register = load(args.file)
    except InputError as e:
        print(f"resilint: error: {e}", file=sys.stderr)
        return 2
    findings = check(register, stale_days=args.stale_days, max_critical=args.max_critical)
    print(FORMATS[args.format](findings, register))
    return 1 if at_or_above(findings, args.fail_on) else 0


if __name__ == "__main__":
    sys.exit(main())
