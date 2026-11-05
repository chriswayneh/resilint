"""Synthetic wheel/control tests; actual index installs are a separate hosted gate."""

import base64
import csv
import hashlib
import io
import os
import runpy
import stat
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HELPER = runpy.run_path(str(ROOT / "scripts/check_index_install.py"))
VERIFY = HELPER["verify_wheel"]
VERSION = "1.0.0rc1"


def release_tree(root):
    (root / "pyproject.toml").write_text('[project]\nversion = "1.0.0-rc1"\n', encoding="utf-8")
    (root / "src/resilint").mkdir(parents=True)
    (root / "src/resilint/__init__.py").write_text(
        '__version__ = "1.0.0-rc1"\n', encoding="utf-8")
    (root / "CHANGELOG.md").write_text("## [1.0.0-rc1] - 2026-11-04\n", encoding="utf-8")


def wheel_fixture(tmp_path, mutation=""):
    info = f"resilint-{VERSION}.dist-info/"
    expected = {
        "resilint/__init__.py": b'__version__ = "1.0.0-rc1"\n',
        "resilint/cli.py": b"# Fictional executable fixture, never imported.\n",
        "resilint/templates/vendors.yaml": b"vendors: []\n",
        info + "licenses/LICENSE": b"MIT fixture\n",
    }
    files = dict(expected)
    files.update({
        info + "METADATA": f"Metadata-Version: 2.4\nName: resilint\nVersion: {VERSION}\n".encode(),
        info + "WHEEL": b"Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        info + "entry_points.txt": b"[console_scripts]\nresilint = resilint.cli:main\n",
        info + "top_level.txt": b"resilint\n",
    })
    if mutation == "tamper-code":
        files["resilint/cli.py"] = b"# Altered code with an internally consistent RECORD.\n"
    elif mutation == "extra-pth":
        files["surprise.pth"] = b"# Installer hook fixture; never executed.\n"
    elif mutation == "extra-script":
        files[f"resilint-{VERSION}.data/scripts/surprise"] = b"# unexpected script\n"
    elif mutation == "path-traversal":
        files["../../escape.py"] = b"# path fixture\n"
    elif mutation == "wrong-version":
        files[info + "METADATA"] = b"Name: resilint\nVersion: 2.0.0\n"
    elif mutation == "wrong-entrypoint":
        files[info + "entry_points.txt"] = b"[console_scripts]\nresilint = other:main\n"
    elif mutation == "missing-file":
        del files["resilint/templates/vendors.yaml"]
    elif mutation == "oversize":
        files["resilint/cli.py"] = b"x" * (HELPER["MAX_FILE"] + 1)
    rows = []
    for name, body in files.items():
        digest = "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(body).digest()).decode().rstrip("=")
        rows.append([name, digest, str(len(body))])
    rows.append([info + "RECORD", "", ""])
    if mutation == "record-hash":
        rows[0][1] = "sha256=invalid"
    elif mutation == "record-duplicate":
        rows.append(rows[0])
    output = io.StringIO()
    csv.writer(output, lineterminator="\n").writerows(rows)
    files[info + "RECORD"] = output.getvalue().encode()
    wheel = tmp_path / f"resilint-{VERSION}-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, body in files.items():
            if mutation == "symlink" and name == "resilint/cli.py":
                member = zipfile.ZipInfo(name)
                member.create_system = 3
                member.external_attr = (stat.S_IFLNK | 0o777) << 16
                archive.writestr(member, body)
            else:
                archive.writestr(name, body)
        if mutation == "duplicate":
            with pytest.warns(UserWarning, match="Duplicate name"):
                archive.writestr("resilint/cli.py", files["resilint/cli.py"])
    return wheel, expected


def test_exact_synthetic_wheel_is_accepted(tmp_path):
    wheel, expected = wheel_fixture(tmp_path)
    VERIFY(wheel, VERSION, expected)


@pytest.mark.parametrize("mutation", [
    "tamper-code", "extra-pth", "extra-script", "path-traversal", "duplicate", "symlink",
    "wrong-version", "wrong-entrypoint", "record-hash", "record-duplicate", "missing-file",
    "oversize",
])
def test_untrusted_wheel_rejected_before_install(tmp_path, mutation):
    wheel, expected = wheel_fixture(tmp_path, mutation)
    with pytest.raises(ValueError):
        VERIFY(wheel, VERSION, expected)


@pytest.mark.parametrize("requested", [
    "v1.0.0", "1.0.0rc0", "1.0.1", "1.0.0;echo fixture", "1.0.0rc1\n",
])
def test_invalid_version_fails_before_subprocess(tmp_path, monkeypatch, requested):
    release_tree(tmp_path)

    def forbidden(*args, **kwargs):
        raise AssertionError("installer must not run for invalid version")

    monkeypatch.setitem(HELPER["smoke"].__globals__, "run", forbidden)
    with pytest.raises(ValueError, match="requested version"):
        HELPER["smoke"](tmp_path, requested)


def test_version_is_bound_to_project_runtime_and_changelog(tmp_path):
    release_tree(tmp_path)
    assert HELPER["selected_version"](tmp_path, VERSION) == (VERSION, "1.0.0-rc1")
    (tmp_path / "src/resilint/__init__.py").write_text(
        '__version__ = "2.0.0"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="runtime"):
        HELPER["selected_version"](tmp_path, VERSION)


def test_inherited_installer_overrides_are_not_used(monkeypatch):
    monkeypatch.setenv("PIP_EXTRA_INDEX_URL", "https://invalid.example.test/simple")
    monkeypatch.setenv("PIP_FIND_LINKS", "fixture")
    monkeypatch.setenv("PYTHONPATH", "fixture")
    monkeypatch.setenv("PYTHONINSPECT", "1")
    env = HELPER["clean_environment"]()
    assert env["PIP_CONFIG_FILE"] == os.devnull
    assert not {"PIP_EXTRA_INDEX_URL", "PIP_FIND_LINKS", "PYTHONPATH", "PYTHONINSPECT"} & env.keys()


def test_bad_wheel_never_reaches_project_install_or_cli(tmp_path, monkeypatch):
    release_tree(tmp_path)
    wheel, expected = wheel_fixture(tmp_path, "extra-pth")
    calls = []
    namespace = HELPER["smoke"].__globals__
    monkeypatch.setitem(namespace, "source_files", lambda *args: expected)
    monkeypatch.setitem(namespace, "download_wheel", lambda *args: wheel)
    monkeypatch.setitem(namespace, "run", lambda args, *rest, **kw: calls.append(args) or "")
    with pytest.raises(ValueError, match="installer hooks"):
        HELPER["smoke"](tmp_path, VERSION)
    assert calls and not any("--find-links" in args for args in calls)
    assert not any("--version" in args or "init" in args for args in calls)


def test_source_identity_uses_canonical_tracked_blobs():
    current, raw = HELPER["selected_version"](ROOT, "")
    expected = HELPER["source_files"](ROOT, current)
    assert f'__version__ = "{raw}"'.encode() in expected["resilint/__init__.py"]
    assert "resilint/templates/vendors.yaml" in expected
