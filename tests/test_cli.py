"""Tests for resilint cli."""

from pathlib import Path

import pytest

from resilint.cli import main
from tests.helpers import _write


def test_exit_codes(tmp_path, capsys):
    assert main(["check", "examples/vendors.yaml"]) == 1
    assert main(["check", "examples/vendors.yaml", "--fail-on", "critical"]) == 0
    assert main(["check", str(tmp_path / "missing.yaml")]) == 2
    with pytest.raises(SystemExit) as e:
        main(["check", "x", "--fail-on", "bogus"])
    assert e.value.code == 2
    clean = tmp_path / "c.yaml"
    clean.write_text("vendors: [{id: a, criticality: low}]")
    assert main(["check", str(clean)]) == 0


def test_alias_message_reaches_user(tmp_path, capsys):
    p = _write(tmp_path, "alias.yaml", "a: &x 1\nvendors: [*x]\n")
    assert main(["check", str(p)]) == 2
    err = capsys.readouterr().err
    assert "YAML anchors/aliases are not allowed (line 2)" in err


def test_output_file(tmp_path, capsys):
    out = tmp_path / "r.sarif"
    assert main(["check", "examples/vendors.yaml", "--format", "sarif",
                 "--output", str(out)]) == 1
    assert capsys.readouterr().out == ""
    assert '"2.1.0"' in out.read_text()
    assert main(["check", "examples/vendors.yaml", "--output",
                 str(tmp_path / "nope" / "r.txt")]) == 2


def test_negative_contact_days_rejected():
    assert main(["check", "examples/vendors.yaml", "--contact-days", "-1"]) == 2


def test_output_refuses_input_file(tmp_path):
    src = _write(tmp_path, "v.yaml", "vendors: [{id: a, criticality: low}]\n")
    assert main(["check", str(src), "--output", str(src)]) == 2
    assert "criticality: low" in src.read_text()


def test_output_refuses_symlinks(tmp_path, symlink_supported):
    target = _write(tmp_path, "keep.txt", "original")
    link = tmp_path / "link.sarif"
    link.symlink_to(target)
    assert main(["check", "examples/vendors.yaml", "--output", str(link)]) == 2
    assert target.read_text() == "original"
    missing = tmp_path / "never.txt"
    dangling = tmp_path / "dangling.sarif"
    dangling.symlink_to(missing)
    assert main(["check", "examples/vendors.yaml", "--output", str(dangling)]) == 2
    assert not missing.exists()


def test_output_root_enforced(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    monkeypatch.setenv("RESILINT_OUTPUT_ROOT", str(ws))
    outside = tmp_path / "out.txt"
    assert main(["check", "examples/vendors.yaml", "--output", str(outside)]) == 2
    assert not outside.exists()
    escape = ws / ".." / "esc.txt"
    assert main(["check", "examples/vendors.yaml", "--output", str(escape)]) == 2
    assert not (tmp_path / "esc.txt").exists()
    inside = ws / "r.txt"
    assert main(["check", "examples/vendors.yaml", "--output", str(inside)]) == 1
    assert inside.read_text()


def test_output_root_empty_relative_missing(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RESILINT_OUTPUT_ROOT", "")
    assert main(["check", "/dev/null.yaml", "--output", "x"]) == 2  # bad input, not root
    src = str(Path(__file__).resolve().parent.parent / "examples" / "vendors.yaml")
    assert main(["check", src, "--output", str(tmp_path / "free.txt")]) == 1
    monkeypatch.setenv("RESILINT_OUTPUT_ROOT", "ws")
    assert main(["check", src, "--output", "ws/in.txt"]) == 1
    assert main(["check", src, "--output", "out.txt"]) == 2
    monkeypatch.setenv("RESILINT_OUTPUT_ROOT", str(tmp_path / "nope"))
    assert main(["check", src, "--output", str(tmp_path / "nope" / "a.txt")]) == 2
    assert main(["check", src, "--output", str(tmp_path / "b.txt")]) == 2
    assert not (tmp_path / "out.txt").exists() and not (tmp_path / "b.txt").exists()
