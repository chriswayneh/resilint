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


def _run_check(tmp_path, fmt, fail_on="high"):
    step = next(step for step in _action()["runs"]["steps"]
                if "RL_FORMAT" in step.get("env", {}))
    assert step["shell"] == "bash"
    output = tmp_path / "report.txt"
    env = {**os.environ,
           "PATH": sysconfig.get_path("scripts") + os.pathsep + os.environ["PATH"],
           "RL_FILE": "examples/vendors.yaml", "RL_FORMAT": fmt,
           "RL_FAIL_ON": fail_on, "RL_OUTPUT": str(output), "RL_DRILLS": "",
           "RESILINT_OUTPUT_ROOT": str(tmp_path)}
    result = subprocess.run([_bash(), "--noprofile", "--norc", "-eo", "pipefail", "-c",
                             step["run"]], check=False, cwd=ROOT, env=env, capture_output=True,
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


def test_action_regmap_writes_report(tmp_path):
    result, output = _run_check(tmp_path, "regmap")
    assert result.returncode == 1, result.stderr  # Example register has high findings.
    assert output.read_text(encoding="utf-8").startswith("# Regulation mapping report")
