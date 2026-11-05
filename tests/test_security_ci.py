"""Reject dangerous audit inputs and verify the scanner job trust boundary."""

import os
import re
import runpy
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
validate = runpy.run_path(str(ROOT / "scripts/check_security_lock.py"))["validate_lock"]
DIGEST = " --hash=sha256:" + "a" * 64


def test_existing_runtime_and_tool_locks():
    assert validate(ROOT / "requirements-lock.txt") == [("PyYAML", "6.0.3")]
    assert ("pip-audit", "2.10.1") in validate(ROOT / "requirements-security-lock.txt")


@pytest.mark.parametrize("text", [
    "-r other.txt", "-c constraints.txt", "--index-url https://example.test/",
    "--extra-index-url https://example.test/", "-e .", ".", "../package",
    "pkg @ https://example.test/pkg.whl", "git+https://example.test/repo",
    "pkg>=1" + DIGEST, "pkg==1.*" + DIGEST, "pkg==1", "pkg==1 --hash=md5:" + "a" * 32,
    "pkg==1 --hash=sha256:abc", "pkg==1; python_version > '3'" + DIGEST,
    "pkg==1" + DIGEST + " --config-settings=evil", "pkg==1" + DIGEST + "\nPKG==2" + DIGEST,
    "pkg==1 " + chr(92), "", "pkg==1 " + chr(92) + "\n# interrupted\n" + DIGEST,
])
def test_reject_hostile_or_incomplete_lock(tmp_path, text):
    lock = tmp_path / "input.txt"
    lock.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        validate(lock)


def test_lock_size_and_encoding_limits(tmp_path):
    lock = tmp_path / "input.txt"
    for content in (b"x" * 262145, bytes([255])):
        lock.write_bytes(content)
        with pytest.raises(ValueError):
            validate(lock)


def test_security_workflow_is_read_only_and_has_no_uploads():
    text = (ROOT / ".github/workflows/security.yml").read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    assert workflow["on"] == {
        "push": {"branches": ["main"]},
        "pull_request": {"branches": ["main"],
                         "types": ["opened", "synchronize", "reopened", "ready_for_review"]},
    }
    assert workflow["permissions"] == {"contents": "read"}
    assert set(workflow["jobs"]) == {"secrets", "dependencies", "scanner-controls"}
    for name, job in workflow["jobs"].items():
        assert "permissions" not in job and "environment" not in job
        assert job["timeout-minutes"] == ("15" if name == "scanner-controls" else "10")
        for step in job["steps"]:
            if "uses" in step:
                assert re.fullmatch(r"actions/(checkout|setup-python)@[0-9a-f]{40}", step["uses"])
                if "checkout@" in step["uses"]:
                    assert step["with"]["persist-credentials"] == "false"
    for forbidden in ("security-events", "id-token", "secrets.", "upload-artifact", "codeql",
                      "pull_request_target", "workflow_run", "${{", "pip install -e"):
        assert forbidden not in text
    assert "--require-hashes --disable-pip --no-deps" in text
    assert "--redact=100" in text and "--ignore-gitleaks-allow" in text
    assert "--gitleaks-ignore-path" in text and "useDefault = true" in text
    assert text.index("sha256sum --check --strict") < text.index("tar -xzf")
    assert "--only-binary=:all: --require-hashes" in text


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def test_real_gitleaks_history_redaction_and_ignore_resistance(tmp_path):
    executable = os.environ.get("RESILINT_TEST_GITLEAKS")
    if not executable:
        pytest.skip("verified scanner path not supplied; run separately before approval")
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-b", "main")
    git(repo, "config", "user.name", "Synthetic Test")
    git(repo, "config", "user.email", "test@example.test")
    (repo / "safe.txt").write_text("fictional data only\n")
    git(repo, "add", "safe.txt")
    git(repo, "commit", "-m", "clean fixture")
    config = tmp_path / "defaults.toml"
    config.write_text("[extend]\nuseDefault = true\n")
    ignore = tmp_path / "empty-ignore"
    ignore.write_text("")
    args = [executable, "git", "--config", str(config), "--gitleaks-ignore-path", str(ignore),
            "--ignore-gitleaks-allow", "--redact=100", "--no-banner", "--log-opts=--all", "."]
    clean = subprocess.run(args, check=False, cwd=repo, capture_output=True, text=True, encoding="utf-8")
    assert clean.returncode == 0, clean.stderr
    # Generated fictional detector fixture, never an actual credential.
    token = "gh" + "p_" + "Ab3Cd4Ef5Gh6Ij7Kl8Mn9Op0Qr1St2Uv3Wx4"
    (repo / "synthetic.txt").write_text("token=" + token + " # gitleaks:allow\n")
    (repo / ".gitleaks.toml").write_text('[allowlist]\npaths = [".*"]\n')
    git(repo, "add", "synthetic.txt", ".gitleaks.toml")
    git(repo, "commit", "-m", "synthetic detector fixture")
    git(repo, "rm", "synthetic.txt")
    git(repo, "commit", "-m", "remove synthetic fixture from working tree")
    result = subprocess.run(args, check=False, cwd=repo, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 1, result.stderr
    assert token not in result.stdout + result.stderr
    assert "leaks found" in result.stderr.lower()


@pytest.mark.parametrize("mode,expected", [("clean", 0), ("vulnerable", 1),
                                         ("missing", 1), ("outage", 1)])
def test_real_audit_cli_with_mocked_advisories(tmp_path, mode, expected):
    executable = os.environ.get("RESILINT_TEST_AUDIT_PYTHON")
    if not executable:
        pytest.skip("verified scanner environment not supplied")
    script = tmp_path / "mock_advisory.py"
    script.write_text("""import sys
from unittest.mock import Mock, patch
import requests
from pip_audit._cli import audit
mode, lock = sys.argv[1:]
response = Mock()
response.status_code = 404 if mode == 'missing' else 200
if mode == 'missing':
    response.raise_for_status.side_effect = requests.HTTPError('synthetic 404')
response.json.return_value = {'vulnerabilities': ([{
    'id': 'PYSEC-2099-0001', 'fixed_in': ['99.0'], 'aliases': [],
    'details': 'Fictional advisory fixture'}] if mode == 'vulnerable' else [])}
session = Mock()
session.get.return_value = response
if mode == 'outage':
    session.get.side_effect = requests.ConnectTimeout('synthetic outage')
sys.argv = ['pip-audit', '--strict', '--require-hashes', '--disable-pip', '--no-deps',
            '--vulnerability-service', 'pypi', '-r', lock]
with patch('pip_audit._service.pypi.caching_session', return_value=session), \
     patch('subprocess.Popen', side_effect=AssertionError('unexpected package subprocess')):
    audit()
""", encoding="utf-8")
    result = subprocess.run([executable, "-I", str(script), mode,
                             str(ROOT / "requirements-lock.txt")],
                            check=False, capture_output=True, text=True)
    assert result.returncode == expected, result.stdout + result.stderr
    assert "unexpected package subprocess" not in result.stderr
    if mode == "clean":
        assert "No known vulnerabilities found" in result.stderr
    elif mode == "vulnerable":
        assert "PYSEC-2099-0001" in result.stdout
    else:
        assert "ERROR" in result.stderr


def test_checksum_failure_prevents_acceptance(tmp_path):
    executable = os.environ.get("RESILINT_TEST_BASH")
    if not executable:
        pytest.skip("Bash/sha256sum verification environment not supplied")
    import hashlib

    fixture = tmp_path / "archive.fixture"
    fixture.write_bytes(b"synthetic archive bytes")
    digest = hashlib.sha256(fixture.read_bytes()).hexdigest()
    command = 'printf "%s  %s\\n" "$1" "$2" | sha256sum --check --strict'
    for value, expected in [(digest, 0), ("0" * 64, 1)]:
        result = subprocess.run([executable, "-c", command, "--", value, fixture.as_posix()],
                                check=False, capture_output=True, text=True)
        assert result.returncode == expected, result.stdout + result.stderr


CONTROLS = runpy.run_path(str(ROOT / "scripts/check_scanner_controls.py"))


@pytest.mark.parametrize("missing", CONTROLS["TOOL_VARIABLES"])
def test_controls_require_each_tool(missing):
    import sys

    environment = dict.fromkeys(CONTROLS["TOOL_VARIABLES"], sys.executable)
    del environment[missing]
    with pytest.raises(ValueError, match=missing):
        CONTROLS["validate_tools"](environment)


def test_controls_reject_invalid_and_nonexecutable_tool(tmp_path, monkeypatch):
    import sys

    environment = dict.fromkeys(CONTROLS["TOOL_VARIABLES"], sys.executable)
    for bad in (str(tmp_path / "absent"), str(tmp_path), "relative-tool"):
        environment["RESILINT_TEST_BASH"] = bad
        with pytest.raises(ValueError):
            CONTROLS["validate_tools"](environment)
    environment["RESILINT_TEST_BASH"] = sys.executable
    monkeypatch.setattr(os, "access", lambda *args: False)
    with pytest.raises(ValueError):
        CONTROLS["validate_tools"](environment)


def test_controls_cli_fails_before_pytest_without_tools():
    import sys

    environment = {k: v for k, v in os.environ.items() if k not in CONTROLS["TOOL_VARIABLES"]}
    result = subprocess.run([sys.executable, "-I", str(ROOT / "scripts/check_scanner_controls.py")],
                            check=False, capture_output=True, text=True, env=environment)
    assert result.returncode == 2
    assert "RESILINT_TEST_GITLEAKS" in result.stderr
    assert "passed" not in result.stdout


@pytest.mark.parametrize("mode", ["pass", "call_fail", "call_skip", "xfail", "xpass",
                                 "setup_skip", "setup_error", "teardown_skip", "teardown_error",
                                 "collection_error", "collection_skip", "missing_test", "unexpected_node", "duplicate_selection",
                                 "interrupted"])
def test_controls_gate_real_pytest_outcomes(tmp_path, mode):
    import sys

    fixture = tmp_path / "test_synthetic_controls.py"
    header = "import pytest\n"
    if mode.startswith(("setup_", "teardown_")):
        phase, outcome = mode.split("_")
        failure = "pytest.skip('synthetic skip')" if outcome == "skip" else (
            "raise RuntimeError('synthetic error')")
        header += "@pytest.fixture(autouse=True)\ndef phase_fixture(request):\n"
        if phase == "setup":
            header += "    if request.node.name == 'test_case_0':\n        " + failure + "\n"
        header += "    yield\n"
        if phase == "teardown":
            header += "    if request.node.name == 'test_case_0':\n        " + failure + "\n"
    bodies = {"call_fail": "assert False", "call_skip": "pytest.skip('synthetic skip')",
              "xfail": "pytest.xfail('synthetic expected failure')",
              "interrupted": "raise KeyboardInterrupt()"}
    count = 5 if mode == "missing_test" else 6
    for i in range(count):
        if i == 0 and mode == "xpass":
            header += "@pytest.mark.xfail(reason='synthetic unexpected pass', strict=False)\n"
        header += f"def test_case_{i}():\n    {bodies.get(mode, 'pass') if i == 0 else 'pass'}\n"
    if mode == "collection_error":
        header += "def invalid syntax\n"
    if mode == "collection_skip":
        header = "import pytest\npytest.skip('synthetic module skip', allow_module_level=True)\n"
    if mode == "unexpected_node":
        header = header.replace("test_case_5", "test_unexpected")
    fixture.write_text(header, encoding="utf-8")
    driver = tmp_path / "run_gate.py"
    driver.write_text("""import os, runpy, sys
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
import pytest
Gate = runpy.run_path(sys.argv[1])['ScannerControlGate']
name = 'test_synthetic_controls.py'
nodes = [name + '::test_case_' + str(i) for i in range(6)]
args = ['-q', '-p', 'no:cacheprovider', '--confcutdir', os.getcwd(), name]
if sys.argv[2] == 'duplicate_selection':
    args = ['-q', '-p', 'no:cacheprovider', '--keep-duplicates', '--confcutdir', os.getcwd(), name, name]
gate = Gate(nodes)
result = pytest.main(args, plugins=[gate])
sys.exit(0 if result == 0 and gate.complete() else 1)
""", encoding="utf-8")
    result = subprocess.run([sys.executable, "-I", str(driver),
                             str(ROOT / "scripts/check_scanner_controls.py"), mode],
                            cwd=tmp_path, check=False, capture_output=True, text=True)
    assert result.returncode == (0 if mode == "pass" else 1), result.stdout + result.stderr
    if mode == "pass":
        assert "6 passed" in result.stdout


def test_controls_gate_rejects_duplicate_expected_ids_and_incomplete_reports():
    from types import SimpleNamespace

    nodes = CONTROLS["EXPECTED"]
    assert len(nodes) == len(set(nodes)) == 6
    gate = CONTROLS["ScannerControlGate"]()
    gate.pytest_collection_finish(SimpleNamespace(items=[SimpleNamespace(nodeid=n) for n in nodes]))
    for node in nodes:
        for phase in ("setup", "call", "teardown"):
            gate.pytest_runtest_logreport(SimpleNamespace(nodeid=node, when=phase,
                                                         passed=True, outcome="passed"))
    assert gate.complete()
    session = SimpleNamespace(exitstatus=0)
    gate.pytest_sessionfinish(session, 2)
    assert session.exitstatus == 1
    del gate.reports[(nodes[-1], "teardown")]
    assert not gate.complete()
    gate.reports[(nodes[-1], "teardown")] = "passed"
    gate.pytest_runtest_logreport(SimpleNamespace(nodeid=nodes[-1], when="teardown",
                                                 passed=True, outcome="passed"))
    assert not gate.complete()
    duplicate = CONTROLS["ScannerControlGate"]([nodes[0], nodes[0]])
    duplicate.collected = [nodes[0], nodes[0]]
    duplicate.reports = {(nodes[0], phase): "passed" for phase in ("setup", "call", "teardown")}
    assert not duplicate.complete()


def test_controls_job_provisions_and_runs_required_gate():
    text = (ROOT / ".github/workflows/security.yml").read_text(encoding="utf-8")
    jobs = yaml.load(text, Loader=yaml.BaseLoader)["jobs"]
    controls = "\n".join(step.get("run", "") for step in jobs["scanner-controls"]["steps"])
    for variable in CONTROLS["TOOL_VARIABLES"]:
        assert "export " + variable + "=" in controls
    for lock in ("requirements-security-lock.txt", "requirements-security-test-lock.txt",
                 "requirements-lock.txt"):
        assert "-r " + lock in controls
    assert "scripts/check_scanner_controls.py" in controls
    assert "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1" in controls
    for name in ("secrets", "dependencies"):
        production = "\n".join(step.get("run", "") for step in jobs[name]["steps"])
        assert "requirements-security-test-lock.txt" not in production
        assert "check_scanner_controls.py" not in production
