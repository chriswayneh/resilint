"""Release identity must fail closed before the OIDC publishing jobs."""

import runpy
from pathlib import Path

import pytest

metadata = runpy.run_path(str(Path(__file__).resolve().parents[1]
                             / "scripts/release_metadata.py"))["metadata"]


def release_tree(root, version="1.0.0"):
    (root / "pyproject.toml").write_text(f'[project]\nversion = "{version}"\n')
    (root / "src/resilint").mkdir(parents=True)
    (root / "src/resilint/__init__.py").write_text(f'__version__ = "{version}"\n')
    (root / "CHANGELOG.md").write_text(f'## [{version}] - 2026-11-02\n')


@pytest.mark.parametrize("version,expected", [
    ("1.0.0", ("1.0.0", True)), ("1.0.0-rc1", ("1.0.0rc1", False)),
])
def test_valid_release_identity(tmp_path, version, expected):
    release_tree(tmp_path, version)
    assert metadata(tmp_path, f"v{version}") == expected


@pytest.mark.parametrize("tag", ["v1", "v1.0.1", "v1.0.0\n", "v1.0.0-rc0", "v1.0.0;echo x"])
def test_refuse_invalid_or_mismatched_tag(tmp_path, tag):
    release_tree(tmp_path)
    with pytest.raises(ValueError):
        metadata(tmp_path, tag)


@pytest.mark.parametrize("file,text", [
    ("src/resilint/__init__.py", '__version__ = "0.4.0"\n'),
    ("CHANGELOG.md", "## [1.0.0] - Unreleased\n"),
])
def test_refuse_unsynced_release_files(tmp_path, file, text):
    release_tree(tmp_path)
    (tmp_path / file).write_text(text)
    with pytest.raises(ValueError):
        metadata(tmp_path, "v1.0.0")
