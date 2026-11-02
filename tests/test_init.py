"""Starter registers are usable, commented and never overwrite existing files."""

import json

from resilint.cli import main


def test_init_default_and_expected_findings(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["init"]) == 0
    path = tmp_path / "vendors.yaml"
    before = path.read_bytes()
    assert b"# FICTIONAL STARTER DATA" in before
    assert b"# YYYY-MM-DD" in before
    capsys.readouterr()
    assert main(["check", str(path), "--format", "json"]) == 1
    findings = json.loads(capsys.readouterr().out)["findings"]
    assert {f["rule_id"] for f in findings} == {"RL004", "RL005", "RL008"}
    assert path.read_bytes() == before
    assert main(["init"]) == 2
    assert path.read_bytes() == before
    assert "resilint: error: vendors.yaml:0:" in capsys.readouterr().err


def test_init_custom_path_and_output_root(tmp_path, monkeypatch, capsys):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    monkeypatch.setenv("RESILINT_OUTPUT_ROOT", str(allowed))
    assert main(["init", str(tmp_path / "outside.yaml")]) == 2
    assert not (tmp_path / "outside.yaml").exists()
    assert "outside" in capsys.readouterr().err
    assert main(["init", str(allowed / "starter.yaml")]) == 0
    assert (allowed / "starter.yaml").is_file()


def test_init_refuses_symlink(tmp_path, symlink_supported, capsys):
    target = tmp_path / "target.yaml"
    target.write_text("keep me")
    link = tmp_path / "vendors.yaml"
    link.symlink_to(target)
    assert main(["init", str(link)]) == 2
    assert target.read_text() == "keep me"
    assert "symlink" in capsys.readouterr().err
