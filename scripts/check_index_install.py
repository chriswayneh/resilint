"""Validate an exact TestPyPI wheel before running its installed quick start."""

from __future__ import annotations

import base64
import configparser
import csv
import hashlib
import io
import json
import os
import re
import runpy
import stat
import subprocess
import sys
import tempfile
import time
import zipfile
from email.parser import BytesParser
from pathlib import Path

metadata = runpy.run_path(str(Path(__file__).with_name("release_metadata.py")))["metadata"]
MAX_FILE = 5_000_000
MAX_TOTAL = 20_000_000


def selected_version(root: Path, requested: str) -> tuple[str, str]:
    project = (root / "pyproject.toml").read_text(encoding="utf-8")
    raw = re.search(r'^version = "([^"]+)"$', project, re.MULTILINE)
    if raw is None:
        raise ValueError("project version missing")
    normalized, _ = metadata(root, "v" + raw[1])
    if requested and (not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:rc[1-9][0-9]*)?", requested)
                      or requested != normalized):
        raise ValueError("requested version must exactly match checked-out release metadata")
    return normalized, raw[1]


def clean_environment() -> dict[str, str]:
    env = {k: v for k, v in os.environ.items()
           if not k.upper().startswith(("PIP_", "PYTHON")) and k.upper() != "VIRTUAL_ENV"}
    env.update(PIP_CONFIG_FILE=os.devnull, PIP_DISABLE_PIP_VERSION_CHECK="1",
               PYTHONNOUSERSITE="1", PYTHONUTF8="1")
    return env


def run(args: list[str], cwd: Path, *, timeout: int = 120) -> str:
    result = subprocess.run(args, cwd=cwd, env=clean_environment(), capture_output=True,
                            text=True, encoding="utf-8", timeout=timeout, check=False)
    if result.returncode:
        raise ValueError(f"validation subprocess failed with exit {result.returncode}")
    return result.stdout


def source_files(root: Path, version: str) -> dict[str, bytes]:
    names = subprocess.check_output(["git", "ls-files", "-z", "--", "src/resilint"], cwd=root)
    expected = {}
    for name in names.decode("utf-8").split("\0"):
        if name:
            if not name.startswith("src/resilint/") or not name.endswith((".py", ".yaml")):
                raise ValueError("unexpected tracked package file")
            expected[name[4:]] = subprocess.check_output(["git", "show", "HEAD:" + name], cwd=root)
    if "resilint/cli.py" not in expected or "resilint/templates/vendors.yaml" not in expected:
        raise ValueError("reviewed source package is incomplete")
    expected[f"resilint-{version}.dist-info/licenses/LICENSE"] = subprocess.check_output(
        ["git", "show", "HEAD:LICENSE"], cwd=root)
    return expected


def _single_header(data: bytes, key: str, expected: str) -> None:
    if BytesParser().parsebytes(data).get_all(key) != [expected]:
        raise ValueError(f"wheel {key} differs from reviewed release")


def verify_wheel(wheel: Path, version: str, expected: dict[str, bytes]) -> None:
    info_root = f"resilint-{version}.dist-info/"
    if wheel.name != f"resilint-{version}-py3-none-any.whl" or wheel.stat().st_size > 50_000_000:
        raise ValueError("unexpected wheel name or size")
    metadata_names = {info_root + name for name in (
        "METADATA", "WHEEL", "RECORD", "entry_points.txt", "top_level.txt",
    )}
    allowed = set(expected) | metadata_names
    with zipfile.ZipFile(wheel) as archive:
        members = archive.infolist()
        if len(members) > 512 or len(members) != len({m.filename for m in members}):
            raise ValueError("duplicate or excessive wheel members")
        if {m.filename for m in members} != allowed:
            raise ValueError("wheel has missing/extra files or installer hooks")
        if sum(m.file_size for m in members) > MAX_TOTAL:
            raise ValueError("wheel contents too large")
        contents = {}
        for member in members:
            if (member.is_dir() or member.file_size > MAX_FILE
                    or stat.S_IFMT(member.external_attr >> 16) == stat.S_IFLNK):
                raise ValueError("unsafe wheel member")
            with archive.open(member) as stream:
                body = stream.read(MAX_FILE + 1)
            if len(body) != member.file_size or len(body) > MAX_FILE:
                raise ValueError("wheel member size mismatch")
            contents[member.filename] = body
    if any(contents[name] != body for name, body in expected.items()):
        raise ValueError("wheel code/resource/license bytes differ from reviewed Git source")
    _single_header(contents[info_root + "METADATA"], "Name", "resilint")
    _single_header(contents[info_root + "METADATA"], "Version", version)
    for key, value in (("Wheel-Version", "1.0"), ("Root-Is-Purelib", "true"),
                       ("Tag", "py3-none-any")):
        _single_header(contents[info_root + "WHEEL"], key, value)
    config = configparser.ConfigParser(interpolation=None)
    config.optionxform = str
    config.read_string(contents[info_root + "entry_points.txt"].decode("utf-8"))
    if (config.defaults() or config.sections() != ["console_scripts"]
            or dict(config["console_scripts"]) != {"resilint": "resilint.cli:main"}
            or contents[info_root + "top_level.txt"].strip() != b"resilint"):
        raise ValueError("unexpected wheel entry points")
    rows = list(csv.reader(io.StringIO(contents[info_root + "RECORD"].decode("utf-8"))))
    if any(len(row) != 3 for row in rows) or len(rows) != len(contents):
        raise ValueError("invalid wheel RECORD")
    seen = set()
    for name, digest, size in rows:
        if name in seen or name not in contents:
            raise ValueError("duplicate/unknown RECORD member")
        seen.add(name)
        if name == info_root + "RECORD":
            if digest or size:
                raise ValueError("RECORD must omit its own hash/size")
        else:
            expected_digest = "sha256=" + base64.urlsafe_b64encode(
                hashlib.sha256(contents[name]).digest()).decode("ascii").rstrip("=")
            if digest != expected_digest or size != str(len(contents[name])):
                raise ValueError("wheel RECORD hash/size mismatch")


def download_wheel(python: Path, scratch: Path, version: str) -> Path:
    for attempt in range(5):
        destination = scratch / f"download-{attempt}"
        destination.mkdir()
        try:
            run([str(python), "-I", "-m", "pip", "--no-cache-dir", "--timeout", "20",
                 "--retries", "0", "download", "--only-binary=:all:", "--no-deps",
                 "--index-url", "https://test.pypi.org/simple/", "--dest", str(destination),
                 "resilint==" + version], scratch)
        except (ValueError, subprocess.TimeoutExpired):
            if attempt == 4:
                raise ValueError("exact TestPyPI wheel unavailable after bounded retries") from None
            print(f"Waiting for exact TestPyPI wheel (attempt {attempt + 1}/5)")
            time.sleep(10)
            continue
        wheels = list(destination.iterdir())
        if len(wheels) != 1:
            raise ValueError("expected one downloaded wheel")
        return wheels[0]
    raise AssertionError("unreachable")


def smoke(root: Path, requested: str = "") -> None:
    version, raw = selected_version(root, requested)  # validate before any installer process
    expected = source_files(root, version)
    with tempfile.TemporaryDirectory(prefix="resilint-index-") as directory:
        scratch = Path(directory)
        run([sys.executable, "-I", "-m", "venv", str(scratch / "venv")], scratch)
        bindir = scratch / "venv" / ("Scripts" if os.name == "nt" else "bin")
        python = bindir / ("python.exe" if os.name == "nt" else "python")
        run([str(python), "-I", "-m", "pip", "--no-cache-dir", "--timeout", "20", "--retries", "0",
             "install", "--only-binary=:all:", "--no-deps", "--require-hashes",
             "--index-url", "https://pypi.org/simple/", "-r", str(root / "requirements-lock.txt")],
            scratch)
        wheel = download_wheel(python, scratch, version)
        verify_wheel(wheel, version, expected)  # no wheel code executes before source verification
        digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
        locked = scratch / "verified-wheel.txt"
        locked.write_text(f"resilint=={version} --hash=sha256:{digest}\n", encoding="utf-8")
        run([str(python), "-I", "-m", "pip", "--no-cache-dir", "install", "--no-index",
             "--no-deps", "--require-hashes", "--find-links", str(wheel.parent), "-r", str(locked)],
            scratch)
        installed = run([str(python), "-I", "-c",
                         "import sysconfig; print(sysconfig.get_paths()['purelib'])"], scratch).strip()
        for name, body in expected.items():
            if (Path(installed) / name).read_bytes() != body:
                raise ValueError("installed source/resource/license identity mismatch")
        installed_version = run([str(python), "-I", "-c",
                                 "from importlib.metadata import version; print(version('resilint'))"],
                                scratch).strip()
        if installed_version != version:
            raise ValueError("installed distribution version mismatch")
        working = scratch / "quick-start"
        working.mkdir()
        cli = str(bindir / ("resilint.exe" if os.name == "nt" else "resilint"))
        if run([cli, "--version"], working).strip() != "resilint " + raw:
            raise ValueError("installed CLI version mismatch")
        run([cli, "init", "vendors.yaml"], working)
        starter = (working / "vendors.yaml").read_bytes()
        report = json.loads(run([cli, "check", "vendors.yaml", "--format", "json",
                                 "--fail-on", "critical"], working))
        if ({f["rule_id"] for f in report["findings"]} != {"RL004", "RL005", "RL008"}
                or len(report["findings"]) != 3 or report["version"] != raw):
            raise ValueError("installed starter findings mismatch")
        explanation = run([cli, "explain", "RL004"], working)
        if "RL004" not in explanation or (working / "vendors.yaml").read_bytes() != starter:
            raise ValueError("installed quick start failed or mutated input")
    print(f"TestPyPI {version}: verified wheel identity and installed quick start passed")


if __name__ == "__main__":
    try:
        smoke(Path(__file__).resolve().parents[1], os.environ.get("REQUESTED_VERSION", ""))
    except (ValueError, OSError, subprocess.SubprocessError, zipfile.BadZipFile,
            configparser.Error, UnicodeError, csv.Error) as exc:
        sys.exit(f"Index install validation failed: {type(exc).__name__}: {exc}")
