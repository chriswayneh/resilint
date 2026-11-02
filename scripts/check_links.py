"""Check repository Markdown file/heading links without network access."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit


def prose(text: str) -> str:
    lines = []
    fence = ""
    for line in text.splitlines():
        marker = re.match(r"\s*(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if not fence:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = ""
        elif not fence:
            lines.append(line)
    return "\n".join(lines)


def anchors(text: str) -> set[str]:
    result: set[str] = set()
    counts: dict[str, int] = {}
    for title in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", prose(text), re.MULTILINE):
        slug = re.sub(r"[^\w\s-]", "", title.lower()).replace(" ", "-")
        number = counts.get(slug, 0)
        counts[slug] = number + 1
        result.add(f"{slug}-{number}" if number else slug)
    return result


def check(root: Path, paths: list[Path]) -> list[str]:
    errors = []
    for source in paths:
        text = prose(source.read_text(encoding="utf-8"))
        for destination in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", text):
            destination = destination.strip().strip("<>")
            url = urlsplit(destination)
            if url.scheme or url.netloc:
                continue
            target = (source.parent / unquote(url.path)).resolve() if url.path else source.resolve()
            if not target.is_relative_to(root) or not target.exists():
                errors.append(f"{source.relative_to(root)}: missing/local-outside-root {destination}")
            elif (url.fragment and target.suffix.lower() == ".md"
                  and unquote(url.fragment) not in anchors(target.read_text(encoding="utf-8"))):
                errors.append(f"{source.relative_to(root)}: missing heading {destination}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    names = subprocess.check_output(["git", "ls-files", "-z", "--", "*.md"], cwd=root)
    paths = [root / name for name in names.decode("utf-8").split("\0") if name]
    errors = check(root, paths)
    for error in errors:
        print(error)
    print(f"Checked relative Markdown links in {len(paths)} files; {len(errors)} errors.")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
