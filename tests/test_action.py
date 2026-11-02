"""Exercise the composite Action's actual check script with the installed CLI."""

import os
import re
import shutil
import subprocess
import sys
import sysconfig
from pathlib import Path

import pytest
import yaml

from resilint.report import FORMATS

ROOT = Path(__file__).resolve().parents[1]


def _action():
    return yaml.safe_load((ROOT / "action.yml").read_text(encoding="utf-8"))


def _bash():
    if sys.platform == "win32":
        # Prefer Git Bash to the Windows bash.exe shim, which invokes WSL.
        git = shutil.which("git")
        assert git, "Action self-tests need Git for Windows"
        for parent in Path(git).resolve().parents:
            candidate = parent / "bin" / "bash.exe"
            if candidate.is_file():
                return str(candidate)
        pytest.fail("Action self-tests need Git Bash")
    bash = shutil.which("bash")
    assert bash, "Action self-tests need Bash"
    return bash


def _run_check(tmp_path, fmt, fail_on="high", cwd=ROOT):
    step = next(step for step in _action()["runs"]["steps"]
                if "RL_FORMAT" in step.get("env", {}))
    assert step["shell"] == "bash"
    output = tmp_path / "report.txt"
    env = {**os.environ,
           "PATH": sysconfig.get_path("scripts") + os.pathsep + os.environ["PATH"],
           "RL_FILE": str(ROOT / "examples/vendors.yaml"), "RL_FORMAT": fmt,
           "RL_FAIL_ON": fail_on, "RL_OUTPUT": str(output), "RL_DRILLS": "",
           "GITHUB_OUTPUT": str(tmp_path / "action-outputs"),
           "RESILINT_OUTPUT_ROOT": str(tmp_path)}
    result = subprocess.run([_bash(), "--noprofile", "--norc", "-eo", "pipefail", "-c",
                             step["run"]], check=False, cwd=cwd, env=env, capture_output=True,
                            text=True, timeout=30)
    return result, output


def test_action_format_description_matches_cli():
    description = _action()["inputs"]["format"]["description"]
    choices = re.search(r"Output format \(([^)]+)\)", description)
    assert choices, "Action format description must list its choices"
    assert {value.strip() for value in choices[1].split(",")} == set(FORMATS)


@pytest.mark.parametrize("fmt,fail_on", [("unknown", "high"), ("text", "urgent")])
def test_action_invalid_input_exits_two(tmp_path, fmt, fail_on):
    result, output = _run_check(tmp_path, fmt, fail_on)
    assert result.returncode == 2, result.stderr
    assert "invalid choice" in result.stderr
    assert not output.exists()
    assert (tmp_path / "action-outputs").read_text() == (
        "findings=\nhighest-severity=\nexit-code=2\n")


@pytest.mark.parametrize("fmt", sorted(FORMATS))
def test_action_writes_report_and_outputs(tmp_path, fmt):
    result, output = _run_check(tmp_path, fmt)
    assert result.returncode == 1, result.stderr  # Example register has high findings.
    assert output.read_text(encoding="utf-8")
    values = dict(line.split("=", 1) for line in
                  (tmp_path / "action-outputs").read_text().splitlines())
    assert int(values["findings"]) > 0
    assert values["highest-severity"] == "high"
    assert values["exit-code"] == "1"


def test_action_empty_register_and_append(tmp_path, monkeypatch, capsys):
    from resilint.action import run
    register = tmp_path / "empty.yaml"
    register.write_text("vendors: []\nprocesses: []\n")
    output = tmp_path / "github-output"
    output.write_text("existing=value\n")
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    assert run(["check", str(register)]) == 0
    assert output.read_text() == (
        "existing=value\nfindings=0\nhighest-severity=none\nexit-code=0\n")
    assert "error" not in capsys.readouterr().err


def test_action_output_write_failure(tmp_path, monkeypatch, capsys):
    from resilint.action import run
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path))
    assert run(["check", "missing.yaml"]) == 2
    assert "cannot write Action outputs" in capsys.readouterr().err


def test_action_counts_match_report(tmp_path):
    import json
    result, report = _run_check(tmp_path, "json", fail_on="critical")
    values = dict(line.split("=", 1) for line in
                  (tmp_path / "action-outputs").read_text().splitlines())
    findings = json.loads(report.read_text(encoding="utf-8"))["findings"]
    assert result.returncode == 0, result.stderr
    assert int(values["findings"]) == len(findings)
    assert values["highest-severity"] == "high"
    assert values["exit-code"] == "0"


def test_action_does_not_import_checkout_modules(tmp_path):
    shadow = tmp_path / "resilint"
    shadow.mkdir()
    (shadow / "__init__.py").write_text("raise RuntimeError('checkout module executed')\n")
    result, report = _run_check(tmp_path, "json", cwd=tmp_path)
    assert result.returncode == 1, result.stderr
    assert report.is_file()
    assert "checkout module executed" not in result.stderr
