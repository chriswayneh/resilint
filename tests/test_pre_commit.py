"""Verify multi-register hook behavior and filenames that resemble options."""

import json

import yaml

from resilint.pre_commit import run
from tests.helpers import good_vendor


def test_hook_checks_all_files_and_prioritizes_errors(tmp_path, capsys):
    first = tmp_path / "first.yaml"
    first.write_text("vendors: []\n")
    bad = tmp_path / "invalid.yaml"
    bad.write_text("vendors: [\n")
    last = tmp_path / "last.yaml"
    last.write_text("vendors: []\n")
    assert run([str(first), str(bad), str(last)]) == 2
    out = capsys.readouterr()
    assert out.out.count("0 findings.") == 2
    assert str(bad) in out.err
    assert first.read_text() == last.read_text() == "vendors: []\n"


def test_hook_threshold_and_option_like_filename(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    path = tmp_path / "--version.yaml"
    path.write_text(yaml.safe_dump({"vendors": [good_vendor(exit_plan=False)]}))
    before = path.read_bytes()
    assert run([path.name]) == 1
    assert "RL004" in capsys.readouterr().out
    assert path.read_bytes() == before
    (tmp_path / ".resilint.yaml").write_text(json.dumps({"fail_on": "critical"}))
    assert run([path.name]) == 0


def test_hook_no_paths():
    assert run([]) == 0
