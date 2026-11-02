"""Stable diagnostics for input, arguments and output failures."""

import pytest

from resilint import cli
from resilint.loader import InputError, load


def _diagnostic(capsys, file, line, message):
    captured = capsys.readouterr()
    errors = [s for s in captured.err.splitlines() if s.startswith("resilint: error:")]
    assert len(errors) == 1
    assert errors[0].startswith(f"resilint: error: {file}:{line}: ")
    assert message in errors[0]
    assert captured.out == ""


@pytest.mark.parametrize("command", ["check", "export-roi", "drill"])
def test_missing_input_names_register(tmp_path, capsys, command):
    path = tmp_path / "missing.yaml"
    if command == "export-roi":
        args = [command, str(path), "--out-dir", str(tmp_path)]
    elif command == "drill":
        args = [command, "record", str(path), "--vendor", "v1", "--kind", "test",
                "--result", "pass"]
    else:
        args = [command, str(path)]
    assert cli.main(args) == 2
    _diagnostic(capsys, path, 0, "file not found")


@pytest.mark.parametrize("suffix,text,line", [
    ("csv", "id,criticality\nv1,urgent\n", 2),
    ("yaml", "vendors:\n  - id: [\n", 3),
    ("yaml", "a: &a 1\nvendors: [*a]\n", 2),
])
def test_known_input_line_is_retained(tmp_path, capsys, suffix, text, line):
    path = tmp_path / f"bad.{suffix}"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(InputError) as error:
        load(path)
    assert error.value.path == str(path)
    assert error.value.line == line
    assert cli.main(["check", str(path)]) == 2
    _diagnostic(capsys, path, line, str(error.value).removeprefix(f"{path}: "))


def test_argument_and_threshold_errors(capsys):
    with pytest.raises(SystemExit) as error:
        cli.main(["check", "unused", "--format", "invalid"])
    assert error.value.code == 2
    _diagnostic(capsys, "<cli>", 0, "invalid choice")
    assert cli.main(["check", "unused", "--stale-days", "-1"]) == 2
    _diagnostic(capsys, "<cli>", 0, "thresholds must be non-negative")


@pytest.mark.parametrize("command", ["check", "drill"])
def test_bad_log_names_log(tmp_path, capsys, command):
    register = tmp_path / "register.yaml"
    register.write_text("vendors: [{id: v1, criticality: low}]")
    log = tmp_path / "drills.yaml"
    log.write_text("drills: [\n")
    if command == "check":
        args = [command, str(register), "--drills", str(log)]
    else:
        args = [command, "record", str(register), "--log", str(log), "--vendor", "v1",
                "--kind", "test", "--result", "pass"]
    assert cli.main(args) == 2
    _diagnostic(capsys, log, 2, "invalid YAML")


@pytest.mark.parametrize("failure", ["output", "export-dir", "export-existing",
                                    "export-target", "export-write", "drill-target",
                                    "drill-lock", "drill-record", "drill-write"])
def test_output_failures_identify_destination(tmp_path, capsys, monkeypatch, failure):
    register = tmp_path / "register.yaml"
    register.write_text("vendors: [{id: v1, criticality: low}]")
    out = tmp_path / "output"
    out.mkdir()
    log = out / "drills.yaml"
    target = log
    message = "simulated failure"
    if failure == "output":
        target = out / "missing" / "report.json"
        args = ["check", str(register), "--output", str(target)]
        message = "cannot write"
    elif failure.startswith("export"):
        args = ["export-roi", str(register), "--out-dir", str(out)]
        target = out
        if failure == "export-dir":
            out.rmdir()
            message = "existing directory"
        elif failure == "export-existing":
            (out / "b_05_01_providers.csv").write_text("existing")
            message = "already exist"
        else:
            target = out / "b_05_01_providers.csv"
            function = "check_target" if failure == "export-target" else "write_file"
            monkeypatch.setattr(cli, function, lambda *a, **kw: "simulated failure")
    else:
        args = ["drill", "record", str(register), "--log", str(log), "--vendor", "v1",
                "--kind", "test", "--result", "pass"]
        if failure == "drill-target":
            monkeypatch.setattr(cli, "check_target", lambda *a, **kw: "simulated failure")
        elif failure == "drill-lock":
            target = str(log) + ".lock"
            monkeypatch.setattr(cli, "_lock", lambda *a: "simulated failure")
        elif failure == "drill-record":
            args[args.index("--vendor") + 1] = "unknown"
            message = "unknown vendor"
        else:
            monkeypatch.setattr(cli, "_replace", lambda *a: "simulated failure")
    assert cli.main(args) == 2
    _diagnostic(capsys, target, 0, message)


def test_diagnostic_cannot_inject_additional_lines(capsys):
    assert cli._error("bad\nresilint: error: forged\x1b[31m", "file\nname", 2) == 2
    captured = capsys.readouterr()
    assert len(captured.err.splitlines()) == 1
    assert "file\\x0aname:2:" in captured.err
    assert "\\x1b[31m" in captured.err
