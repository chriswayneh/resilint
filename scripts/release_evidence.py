"""Prepare a minimal runtime SBOM and verify exact release artifact bytes."""

import argparse
import hashlib
import json
import re
import runpy
from pathlib import Path

validate_lock = runpy.run_path(str(Path(__file__).with_name("check_security_lock.py")))[
    "validate_lock"
]


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def runtime_sbom(raw: dict, version: str, locked: list[tuple[str, str]]) -> dict:
    root = raw["metadata"]["component"]
    if root["name"] != "resilint" or root["version"].replace("-rc", "rc") != version:
        raise ValueError("SBOM project identity differs from release")
    wanted = {normalize(name): (name, ver) for name, ver in locked}
    components = []
    references = {root["bom-ref"]: "root-component"}
    seen = set()
    for item in raw.get("components", []):
        key = normalize(item["name"])
        if key not in wanted:
            if key not in {"pip", "setuptools"}:
                raise ValueError("unexpected package in runtime inventory")
            continue  # Omit only bootstrap installers, not runtime dependencies.
        name, ver = wanted[key]
        if key in seen or item["version"] != ver:
            raise ValueError("SBOM runtime identity differs from lock")
        seen.add(key)
        ref = f"pkg:pypi/{key}@{ver}"
        if item["bom-ref"] in references:
            raise ValueError("duplicate SBOM reference")
        references[item["bom-ref"]] = ref
        components.append({"type": "library", "name": name, "version": ver,
                           "bom-ref": ref, "purl": ref})
    if seen != set(wanted):
        raise ValueError("SBOM is missing locked runtime components")
    graph = {}
    for node in raw.get("dependencies", []):
        if node["ref"] in references:
            ref = references[node["ref"]]
            if ref in graph:
                raise ValueError("duplicate SBOM dependency node")
            dependencies = node.get("dependsOn", [])
            if any(item not in references for item in dependencies):
                raise ValueError("SBOM runtime graph contains an unlocked dependency")
            graph[ref] = sorted({references[item] for item in dependencies})
    if set(graph) != set(references.values()):
        raise ValueError("SBOM dependency graph is incomplete")
    reachable = set()
    pending = ["root-component"]
    while pending:
        ref = pending.pop()
        if ref not in reachable:
            reachable.add(ref)
            pending.extend(graph[ref])
    if reachable != set(graph):
        raise ValueError("SBOM contains disconnected runtime components")
    return {
        "$schema": "http://cyclonedx.org/schema/bom-1.6.schema.json",
        "bomFormat": "CycloneDX", "specVersion": "1.6", "version": 1,
        "metadata": {"component": {"type": "application", "name": "resilint",
                                   "version": version, "bom-ref": "root-component"}},
        "components": sorted(components, key=lambda item: item["name"].lower()),
        "dependencies": [{"ref": ref, "dependsOn": deps}
                         for ref, deps in sorted(graph.items())],
    }


def digest(path: Path) -> str:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 50_000_000:
        raise ValueError("release artifact is not a bounded regular file")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expected_names(version: str) -> set[str]:
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:rc[1-9][0-9]*)?", version):
        raise ValueError("invalid normalized release version")
    return {f"resilint-{version}-py3-none-any.whl", f"resilint-{version}.tar.gz",
            "resilint.cdx.json", "release-notes.md"}


def prepare(raw_path: Path, dist: Path, output: Path, version: str, lock: Path) -> None:
    names = expected_names(version)
    distributions = names - {"resilint.cdx.json", "release-notes.md"}
    if {p.name for p in dist.iterdir()} != distributions:
        raise ValueError("unexpected or missing distributions")
    if raw_path.is_symlink() or raw_path.stat().st_size > 2_000_000:
        raise ValueError("raw SBOM is not a bounded regular input")
    sbom = runtime_sbom(json.loads(raw_path.read_text(encoding="utf-8")),
                        version, validate_lock(lock))
    (output / "resilint.cdx.json").write_text(
        json.dumps(sbom, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if {p.name for p in output.iterdir()} != {"resilint.cdx.json", "release-notes.md"}:
        raise ValueError("unexpected or missing release evidence")
    rows = []
    for name in sorted(names):
        path = dist / name if name in distributions else output / name
        rows.append(f"{digest(path)}  {name}\n")
    (output / "SHA256SUMS").write_text("".join(rows), encoding="utf-8")


def verify(directory: Path, version: str) -> None:
    names = expected_names(version)
    if {p.name for p in directory.iterdir()} != names | {"SHA256SUMS"}:
        raise ValueError("unexpected or missing downloaded artifacts")
    manifest = directory / "SHA256SUMS"
    if manifest.is_symlink() or manifest.stat().st_size > 8192:
        raise ValueError("invalid release manifest")
    seen = set()
    for row in manifest.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_.-]+)", row)
        if not match or match[2] not in names or match[2] in seen:
            raise ValueError("invalid release manifest entry")
        seen.add(match[2])
        if digest(directory / match[2]) != match[1]:
            raise ValueError("release artifact checksum mismatch")
    if seen != names:
        raise ValueError("incomplete release manifest")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("prepare")
    create.add_argument("raw", type=Path)
    create.add_argument("dist", type=Path)
    create.add_argument("output", type=Path)
    create.add_argument("version")
    create.add_argument("--lock", type=Path, default=Path("requirements-lock.txt"))
    check = sub.add_parser("verify")
    check.add_argument("directory", type=Path)
    check.add_argument("version")
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            prepare(args.raw, args.dist, args.output, args.version, args.lock)
        else:
            verify(args.directory, args.version)
    except (ValueError, OSError, KeyError, TypeError, RecursionError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
