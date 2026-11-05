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


def test_release_workflow_preserves_publication_gates():
    import yaml

    workflow = yaml.safe_load((Path(__file__).resolve().parents[1]
                               / ".github/workflows/release.yml").read_text())
    jobs = workflow["jobs"]
    assert workflow["permissions"] == {"contents": "read"}
    assert jobs["testpypi"]["needs"] == "build"
    assert jobs["verify-testpypi"]["needs"] == ["build", "testpypi"]
    assert jobs["pypi"]["needs"] == ["build", "verify-testpypi"]
    assert jobs["pypi"]["if"] == "needs.build.outputs.stable == 'true'"
    for name in ("testpypi", "pypi"):
        assert jobs[name]["permissions"] == {"id-token": "write"}
        assert jobs[name]["environment"] == name
        steps = jobs[name]["steps"]
        assert len(steps) == 2  # download existing build, then publish; no rebuild
        assert steps[0]["with"]["name"] == "distributions"
    for name in ("build", "verify-testpypi"):
        assert "id-token" not in jobs[name].get("permissions", {})
    verification = jobs["verify-testpypi"]["steps"][-1]["run"]
    assert "--no-deps --index-url https://test.pypi.org/simple/" in verification
    assert "--extra-index-url" not in verification
    assert 'importlib.metadata.version("resilint") == os.environ["RELEASE_VERSION"]' in verification


def test_release_ancestry_rejects_unmerged_commit(tmp_path):
    import subprocess

    def git(*args, check=True):
        return subprocess.run(["git", *args], cwd=tmp_path, check=check,
                              capture_output=True, text=True)

    git("init", "-b", "main")
    git("config", "user.name", "Synthetic Test")
    git("config", "user.email", "test@example.test")
    git("commit", "--allow-empty", "-m", "merged base")
    git("update-ref", "refs/remotes/origin/main", "HEAD")
    workflow = (Path(__file__).resolve().parents[1]
                / ".github/workflows/release.yml").read_text()
    assert "git merge-base --is-ancestor HEAD origin/main" in workflow
    assert git("merge-base", "--is-ancestor", "HEAD", "origin/main").returncode == 0
    git("switch", "-c", "unmerged")
    git("commit", "--allow-empty", "-m", "unmerged candidate")
    assert git("merge-base", "--is-ancestor", "HEAD", "origin/main", check=False).returncode == 1
