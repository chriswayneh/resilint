"""Supported command paths remain usable without deprecation warnings."""

import pytest

from resilint.cli import main


@pytest.mark.parametrize("command", ["check", "init", "explain", "export-roi", "drill"])
def test_frozen_command_paths_are_warning_free(command, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    register = tmp_path / "empty.yaml"
    register.write_text("vendors: []\n")
    output = tmp_path / "export"
    output.mkdir()
    args = {
        "check": ["check", str(register)],
        "init": ["init"],
        "explain": ["explain", "RL004"],
        "export-roi": ["export-roi", str(register), "--out-dir", str(output)],
        "drill": ["drill", "record", "vendor.yaml", "--vendor", "example-vendor",
                  "--kind", "test", "--result", "pass", "--date", "2026-01-01"],
    }
    (tmp_path / "vendor.yaml").write_text(
        "vendors:\n  - id: example-vendor\n    criticality: high\n")
    assert main(args[command]) == 0
    assert capsys.readouterr().err == ""
