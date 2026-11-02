"""Internal GitHub Action adapter; the public CLI remains resilint.cli."""

from __future__ import annotations

import os
import sys

from .cli import _error, main


def run(argv=None) -> int:
    summary: dict[str, str] = {}
    try:
        code = main(argv, _summary=summary)
    except SystemExit as error:
        code = error.code if isinstance(error.code, int) else 2
    path = os.environ.get("GITHUB_OUTPUT", "")
    try:
        # This path is supplied by the runner. Values are computed counts/enums,
        # never register text or command-line input interpolated into commands.
        with open(path, "a", encoding="utf-8", newline="") as output:
            output.write(f"findings={summary.get('findings', '')}\n"
                         f"highest-severity={summary.get('highest_severity', '')}\n"
                         f"exit-code={code}\n")
    except (OSError, ValueError):
        return _error("cannot write Action outputs", path or "<GITHUB_OUTPUT>")
    return code


if __name__ == "__main__":
    sys.exit(run())
