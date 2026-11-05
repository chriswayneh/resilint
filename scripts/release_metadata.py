"""Refuse mismatched release tags before any package can be published."""

import argparse
import re
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def metadata(root: Path, tag: str) -> tuple[str, bool]:
    if not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+(?:-rc[1-9][0-9]*)?", tag):
        raise ValueError("expected vX.Y.Z or vX.Y.Z-rcN tag")
    version = tag[1:]
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    if project["project"]["version"] != version:
        raise ValueError("tag and project version differ")
    runtime = (root / "src/resilint/__init__.py").read_text(encoding="utf-8")
    if not re.search(rf'^__version__ = "{re.escape(version)}"$', runtime, re.MULTILINE):
        raise ValueError("runtime and project version differ")
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    if not re.search(rf"^## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}$",
                     changelog, re.MULTILINE):
        raise ValueError("dated changelog entry missing")
    return version.replace("-rc", "rc"), "-rc" not in version


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tag")
    args = parser.parse_args()
    try:
        version, stable = metadata(Path(__file__).resolve().parents[1], args.tag)
    except ValueError as exc:
        parser.error(str(exc))
    print(f"version={version}")
    print(f"stable={str(stable).lower()}")
