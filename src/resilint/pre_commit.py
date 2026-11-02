"""Internal pre-commit adapter: check every selected register once."""

from __future__ import annotations

import sys

from .cli import main


def run(paths: list[str]) -> int:
    status = 0
    for path in paths:
        status = max(status, main(["check", "--", path]))
    return status


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
