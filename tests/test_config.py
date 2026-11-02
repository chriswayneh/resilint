"""Rule configuration validation, precedence and suppression expiry."""

import json
from datetime import date, datetime, timedelta

import pytest
import yaml

from resilint.cli import main
from resilint.config import Ignore, Settings, apply_ignores, load_config
from resilint.loader import MAX_BYTES, InputError
from resilint.rules import _f
from tests.helpers import good_vendor


def _config(tmp_path, data, name="settings.yaml"):
    path = tmp_path / name
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    return path


def _register(tmp_path, **changes):
    today = date.today().isoformat()
    vendor = good_vendor(last_tested=today, contacts_verified=today, supports_processes=[])
    vendor.update(changes)
    path = tmp_path / "register.yaml"
    path.write_text(yaml.safe_dump({"vendors": [vendor]}), encoding="utf-8")
    return path


def test_default_config_and_explicit_selection(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert load_config() == Settings()
    register = _register(tmp_path, notification_sla_hours=None)
    _config(tmp_path, {"fail_on": "critical"}, ".resilint.yaml")
    assert main(["check", str(register), "--format", "json"]) == 0
    assert len(json.loads(capsys.readouterr().out)["findings"]) == 1
    selected = _config(tmp_path, {"fail_on": "high"})
    assert main(["check", str(register), "--config", str(selected)]) == 1
    assert main(["check", str(register), "--fail-on", "high"]) == 1


@pytest.mark.parametrize("field,flag", [("stale_days", "--stale-days"),
                                        ("contact_days", "--contact-days")])
def test_cli_date_threshold_overrides_file(tmp_path, capsys, field, flag):
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    register = _register(tmp_path, **{
        "last_tested" if field == "stale_days" else "contacts_verified": yesterday})
    config = _config(tmp_path, {field: 0, "fail_on": "medium"})
    args = ["check", str(register), "--config", str(config), "--format", "json"]
    assert main(args) == 1
    assert len(json.loads(capsys.readouterr().out)["findings"]) == 1
    assert main([*args, flag, "2"]) == 0
    assert json.loads(capsys.readouterr().out)["findings"] == []


def test_cli_concentration_overrides_file(tmp_path, capsys):
    register = _register(tmp_path, supports_processes=["p1", "p2"])
    data = yaml.safe_load(register.read_text())
    data["processes"] = [{"id": "p1"}, {"id": "p2"}]
    register.write_text(yaml.safe_dump(data))
    config = _config(tmp_path, {"max_critical": 1, "fail_on": "medium"})
    args = ["check", str(register), "--config", str(config), "--format", "json"]
    assert main(args) == 1
    assert json.loads(capsys.readouterr().out)["findings"][0]["rule_id"] == "RL007"
    assert main([*args, "--max-critical", "2"]) == 0
    assert json.loads(capsys.readouterr().out)["findings"] == []


@pytest.mark.parametrize("days,expected", [(-1, 1), (0, 0), (1, 0)])
def test_expired_ignore_refires_cli_finding(tmp_path, capsys, days, expected):
    register = _register(tmp_path, notification_sla_hours=None)
    expiry = date.today() + timedelta(days=days)
    config = _config(tmp_path, {"ignore": [{"rule": "RL001", "vendor": "v1",
        "reason": "Fictional remediation tracking", "expires": expiry}]})
    assert main(["check", str(register), "--config", str(config), "--format", "json"]) == expected
    assert len(json.loads(capsys.readouterr().out)["findings"]) == expected


def test_ignore_matches_exact_rule_and_vendor():
    today = date(2026, 11, 2)
    findings = [_f("RL001", "v1", "x"), _f("RL001", "v2", "x"), _f("RL002", "v1", "x")]
    settings = Settings(ignore=(Ignore("RL001", "v1", "Reason", today),))
    assert apply_ignores(findings, settings, today) == findings[1:]
    assert apply_ignores(findings, settings, today + timedelta(days=1)) == findings


@pytest.mark.parametrize("data", [
    [], {"unknown": 1}, {"fail_on": "urgent"}, {"fail_on": []},
    {"stale_days": -1}, {"contact_days": True}, {"max_critical": "3"}, {"ignore": None},
    {"ignore": [{}]}, {"ignore": ["bad"]},
])
def test_invalid_config_is_exit_two(tmp_path, capsys, data):
    config = _config(tmp_path, data)
    with pytest.raises(InputError):
        load_config(config)
    assert main(["check", "unused", "--config", str(config)]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert f"resilint: error: {config}:0:" in captured.err


@pytest.mark.parametrize("field,value", [("rule", "RL999"), ("rule", 1), ("vendor", " "),
                                        ("reason", ""), ("expires", "not-a-date"),
                                        ("expires", "20261102"), ("expires", 4),
                                        ("expires", datetime(2026, 11, 2)),
                                        ("expires", "2026-02-30")])
def test_invalid_ignore_rejected(tmp_path, field, value):
    row = {"rule": "RL001", "vendor": "v1", "reason": "Reason", "expires": "2026-11-02"}
    row[field] = value
    with pytest.raises(InputError, match=r"ignore\[0\]"):
        load_config(_config(tmp_path, {"ignore": [row]}))


@pytest.mark.parametrize("payload", [b"ignore: [\n", b"a: &a 1\nignore: [*a]\n", b"\xff",
                                    b"ignore: [{expires: 2026-13-01}]\n"])
def test_invalid_config_encoding_or_yaml(tmp_path, payload):
    path = tmp_path / "config.yaml"
    path.write_bytes(payload)
    with pytest.raises(InputError) as error:
        load_config(path)
    assert error.value.path == str(path)


def test_missing_oversize_and_empty_config(tmp_path):
    path = tmp_path / "settings.yaml"
    with pytest.raises(InputError, match="cannot read config"):
        load_config(path)
    path.write_text("")
    assert load_config(path) == Settings(source=str(path))
    with path.open("wb") as stream:
        stream.seek(MAX_BYTES)
        stream.write(b"x")
    with pytest.raises(InputError, match="larger than 5 MB"):
        load_config(path)


def test_quoted_expiry_and_zero_thresholds(tmp_path):
    path = _config(tmp_path, {"stale_days": 0, "contact_days": 0, "max_critical": 0,
        "ignore": [{"rule": "RL001", "vendor": "v1", "reason": "Reason",
                    "expires": "2026-11-02"}]})
    settings = load_config(path)
    assert settings.ignore[0].expires == date(2026, 11, 2)
    assert (settings.stale_days, settings.contact_days, settings.max_critical) == (0, 0, 0)


def test_nonregular_config_rejected(tmp_path):
    with pytest.raises(InputError, match="regular file"):
        load_config(tmp_path)


@pytest.mark.parametrize("explicit", [False, True])
def test_report_cannot_overwrite_loaded_config(tmp_path, monkeypatch, capsys, explicit):
    monkeypatch.chdir(tmp_path)
    register = _register(tmp_path)
    config = _config(tmp_path, {"fail_on": "low"}, ".resilint.yaml")
    original = config.read_bytes()
    args = ["check", str(register), "--output", str(config)]
    if explicit:
        args += ["--config", str(config)]
    assert main(args) == 2
    assert "must not be the input file" in capsys.readouterr().err
    assert config.read_bytes() == original
