"""Reject executable/index directives before a no-resolution dependency audit."""

import argparse
import re
from pathlib import Path

MAX_BYTES = 262144
PACKAGE = re.compile(r"([A-Za-z0-9][A-Za-z0-9._-]*)==([0-9][A-Za-z0-9.!+_-]*)")
HASH = re.compile(r"--hash=sha256:[0-9a-f]{64}")


def validate_lock(path: Path) -> list[tuple[str, str]]:
    if path.is_symlink() or not path.is_file():
        raise ValueError("lock must be a regular non-symlink file")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("lock exceeds size limit")
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ValueError("lock must be UTF-8") from exc
    pending = ""
    packages = []
    seen = set()
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            if pending:
                raise ValueError("interrupted continuation")
            continue
        continued = line.endswith(chr(92))
        pending += " " + (line[:-1].rstrip() if continued else line)
        if continued:
            continue
        tokens = pending.split()
        pending = ""
        match = PACKAGE.fullmatch(tokens[0]) if tokens else None
        if not match or len(tokens) < 2 or not all(HASH.fullmatch(t) for t in tokens[1:]):
            raise ValueError("expected exact package version and SHA-256 hashes only")
        name, version = match.groups()
        normalized = re.sub(r"[-_.]+", "-", name).lower()
        if normalized in seen:
            raise ValueError("duplicate package")
        seen.add(normalized)
        packages.append((name, version))
    if pending or not packages:
        raise ValueError("empty or incomplete lock")
    return packages


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lock", type=Path)
    args = parser.parse_args()
    try:
        packages = validate_lock(args.lock)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Validated {len(packages)} exact hashed requirements")
