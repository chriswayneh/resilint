"""POSIX output privacy regressions using only fictional input."""

import json
import os
import stat
from contextlib import contextmanager
from pathlib import Path

import pytest
import yaml

from resilint.cli import main
from tests.helpers import good_vendor

pytestmark = pytest.mark.skipif(os.name != "posix", reason="POSIX modes do not verify Windows ACLs")


@contextmanager
def _umask(mask):
    previous = os.umask(mask)
    try:
        yield
    finally:
        os.umask(previous)


def _mode(path):
    return stat.S_IMODE(path.stat().st_mode)


@pytest.fixture
def register(tmp_path):
    path = tmp_path / "vendors.yaml"
    path.write_text(yaml.safe_dump({
        "vendors": [good_vendor()],
        "processes": [{"id": "p1", "rto_hours": 4}],
    }), encoding="utf-8")
    original = path.read_bytes()
    yield path
    assert path.read_bytes() == original


@pytest.mark.parametrize("command", ["check", "export", "init"])
def test_new_cli_outputs_are_private_with_permissive_umask(register, tmp_path, command):
    with _umask(0o022):
        if command == "check":
            report, baseline = tmp_path / "report.json", tmp_path / "baseline.json"
            assert main(["check", str(register), "--format", "json", "--fail-on", "critical",
                         "--output", str(report), "--write-baseline", str(baseline)]) == 0
            assert json.loads(report.read_text(encoding="utf-8"))["tool"] == "resilint"
            outputs = [report, baseline]
        elif command == "export":
            directory = tmp_path / "roi"
            directory.mkdir()
            assert main(["export-roi", str(register), "--out-dir", str(directory)]) == 0
            outputs = list(directory.iterdir())
            assert {p.name for p in outputs} == {
                "b_05_01_providers.csv", "b_06_01_functions.csv", "b_02_02_links.csv", "README.txt",
            }
        else:
            starter = tmp_path / "starter.yaml"
            assert main(["init", str(starter)]) == 0
            assert yaml.safe_load(starter.read_text(encoding="utf-8"))["vendors"]
            outputs = [starter]
        assert all(path.stat().st_size and _mode(path) == 0o600 for path in outputs)


@pytest.mark.parametrize("private", [False, True])
def test_report_overwrite_preserves_operator_permissions(register, tmp_path, private):
    report = tmp_path / "existing.json"
    with _umask(0o022):
        report.write_text("old contents", encoding="utf-8")
        if private:
            report.chmod(0o600)
        before = _mode(report)
        assert main(["check", str(register), "--format", "json", "--fail-on", "critical",
                     "--output", str(report)]) == 0
    assert _mode(report) == before
    assert json.loads(report.read_text(encoding="utf-8"))["tool"] == "resilint"


@pytest.mark.parametrize("creation_mask", [0o022, 0o077])
@pytest.mark.parametrize("existing", ["new", "private", "shared"])
def test_drill_replacement_and_sidecar_are_private(register, tmp_path, creation_mask, existing):
    log = tmp_path / "drills.yaml"
    if existing != "new":
        with _umask(0o022):
            log.write_text("drills: []\n", encoding="utf-8")
        if existing == "private":
            log.chmod(0o600)
    with _umask(creation_mask):
        assert main(["drill", "record", str(register), "--vendor", "v1", "--log", str(log),
                     "--kind", "tabletop", "--result", "pass", "--date", "2000-01-01",
                     "--notes", "Fictional failover exercise"]) == 0
    assert _mode(log) == 0o600
    sidecar = Path(str(log) + ".lock")
    assert _mode(sidecar) == 0o600
    assert sidecar.read_bytes() == b""
    assert yaml.safe_load(log.read_text(encoding="utf-8"))["drills"][0]["notes"] == (
        "Fictional failover exercise"
    )
