"""Keep published release metadata consistent across packaging and documentation."""

import re
import sys
from datetime import date
from pathlib import Path

from resilint import __version__

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

ROOT = Path(__file__).resolve().parents[1]


def _read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def _project_version():
    return tomllib.loads(_read("pyproject.toml"))["project"]["version"]


def test_package_version_matches_runtime():
    assert _project_version() == __version__, (
        "pyproject.toml [project].version and resilint.__version__ must match"
    )


def test_changelog_release_matches_package():
    entries = re.findall(
        r"^## \[([^\]]+)\](?: - ([^\n]+))?$", _read("CHANGELOG.md"), re.MULTILINE
    )
    assert entries, "CHANGELOG.md must have release headings"
    assert entries[0][0] in ("Unreleased", _project_version()), (
        "Start CHANGELOG.md with [Unreleased] or the current package version"
    )
    releases = [(version, released) for version, released in entries if version != "Unreleased"]
    assert releases, "CHANGELOG.md must retain the latest published release"
    version, released = releases[0]
    assert version == _project_version(), (
        "The latest released CHANGELOG heading must match the package version"
    )
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", released), (
        "Released headings require YYYY-MM-DD; use [Unreleased] for development changes"
    )
    date.fromisoformat(released)


def test_readme_release_references_are_current():
    readme = _read("README.md")
    patterns = (
        r"chriswayneh/resilint(?:\.git)?@v([\w.+-]+)",
        r"chriswayneh/resilint/releases/tag/v([\w.+-]+)",
        r"git clone --branch v(\S+)[^\n]*github\.com/chriswayneh/resilint",
        r"\bv([\w.+-]+)\s+released\b",
        r"\bresilint\s+(\d[\w.+-]*)",
        r"[Pp]ublished\s+`v([\w.+-]+)`",
    )
    versions = {version for pattern in patterns for version in re.findall(pattern, readme)}
    allowed = {_project_version()}
    if re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+-rc[1-9][0-9]*", _project_version()):
        # A candidate source tree still documents its latest published stable demo.
        # Permit only the newest stable entry, not arbitrary historical versions.
        stable = re.findall(r"^## \[([0-9]+\.[0-9]+\.[0-9]+)\] - \d{4}-\d{2}-\d{2}$",
                            _read("CHANGELOG.md"), re.MULTILINE)
        assert stable, "Candidate changelog must retain the latest stable release"
        allowed.add(stable[0])
    assert not versions - allowed, (
        f"README release references {sorted(versions)} must be in {sorted(allowed)}"
    )


def test_readme_release_badge_is_dynamic():
    readme = _read("README.md")
    assert re.search(
        r"!\[[^\]]*\]\(https://img\.shields\.io/github/v/release/chriswayneh/resilint\)",
        readme,
    ), "Use the dynamic latest-release badge rather than a fixed version"
    assert "https://github.com/chriswayneh/resilint/releases/latest" in readme
