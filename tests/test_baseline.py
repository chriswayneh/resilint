"""Baseline identity stability, filtering and safe file handling."""

import json
from dataclasses import replace
from datetime import date, timedelta

import pytest
import yaml

from resilint.baseline import dump_baseline, fingerprint, load_baseline
from resilint.cli import main
from resilint.loader import MAX_BYTES, InputError, normalize
from resilint.rules import _f, check
from tests.helpers import TODAY, good_vendor


def _register(tmp_path):
    path = tmp_path / "register.yaml"
    path.write_text("vendors: [{id: v1, criticality: high}]\n", encoding="utf-8")
    return path


def test_fingerprint_is_stable_and_field_specific():
    finding = _f("RL001", "v:1", "old message")
    assert fingerprint(finding) == fingerprint(replace(finding, message="new message"))
    assert fingerprint(finding) != fingerprint(replace(finding, vendor="v:2"))
    assert fingerprint(finding) != fingerprint(replace(finding, rule_id="RL002"))
    assert fingerprint(finding) != fingerprint(replace(finding, field="other"))
    assert len(fingerprint(replace(finding, vendor="\ud800"))) == 64
    # Encoding tuples as JSON prevents delimiter collisions in user-controlled ids/fields.
    assert fingerprint(replace(finding, vendor="a:b", field="c")) != fingerprint(
        replace(finding, vendor="a", field="b:c"))


def test_process_rto_findings_have_distinct_stable_identity():
    reg = normalize({"vendors": [good_vendor(recovery_time_hours=8,
                      supports_processes=["p1", "p2"])],
                     "processes": [{"id": "p1", "rto_hours": 1},
                                   {"id": "p2", "rto_hours": 2}]})
    findings = [f for f in check(reg, today=TODAY) if f.rule_id == "RL006"]
    assert {f.field for f in findings} == {"supports_processes:p1", "supports_processes:p2"}
    assert len({fingerprint(f) for f in findings}) == 2
    reg["processes"]["p1"]["rto_hours"] = 3
    changed = [f for f in check(reg, today=TODAY) if f.rule_id == "RL006"]
    assert {fingerprint(f) for f in changed} == {fingerprint(f) for f in findings}


def test_serialization_is_deterministic_and_deduplicated():
    a, b = _f("RL001", "a", "x"), _f("RL002", "b", "y")
    assert dump_baseline([a, b, a]) == dump_baseline([b, a])
    assert json.loads(dump_baseline([])) == {"schema_version": 1, "fingerprints": []}


@pytest.mark.parametrize("fmt", ["json", "text", "md", "sarif", "regmap"])
def test_write_then_filter_existing_findings(tmp_path, capsys, fmt):
    register = _register(tmp_path)
    baseline = tmp_path / "baseline.json"
    args = ["check", str(register), "--format", fmt]
    assert main([*args, "--write-baseline", str(baseline)]) == 0
    assert load_baseline(baseline)
    capsys.readouterr()
    assert main([*args, "--baseline", str(baseline)]) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    if fmt == "json":
        assert json.loads(captured.out)["findings"] == []
    elif fmt == "sarif":
        assert json.loads(captured.out)["runs"][0]["results"] == []


def test_new_vendor_finding_is_reported_and_inputs_unchanged(tmp_path, capsys):
    register = _register(tmp_path)
    baseline = tmp_path / "baseline.json"
    assert main(["check", str(register), "--write-baseline", str(baseline)]) == 0
    data = yaml.safe_load(register.read_text())
    data["vendors"].append({"id": "v2", "criticality": "high"})
    register.write_text(yaml.safe_dump(data))
    before, old = register.read_bytes(), baseline.read_bytes()
    capsys.readouterr()
    assert main(["check", str(register), "--baseline", str(baseline), "--format", "json"]) == 1
    assert {f["vendor"] for f in json.loads(capsys.readouterr().out)["findings"]} == {"v2"}
    assert register.read_bytes() == before
    assert baseline.read_bytes() == old


@pytest.mark.parametrize("body", ["{", "[]", '{"schema_version":true,"fingerprints":[]}',
    '{"schema_version":2,"fingerprints":[]}', '{"schema_version":1,"fingerprints":"bad"}',
    '{"schema_version":1,"fingerprints":["bad"]}',
    '{"schema_version":1,"fingerprints":[],"extra":true}'])
def test_invalid_baseline_fails_closed(tmp_path, capsys, body):
    register = _register(tmp_path)
    path = tmp_path / "baseline.json"
    path.write_text(body)
    with pytest.raises(InputError):
        load_baseline(path)
    assert main(["check", str(register), "--baseline", str(path)]) == 2
    assert f"resilint: error: {path}:" in capsys.readouterr().err


def test_unreadable_nonregular_and_oversize_baseline(tmp_path):
    path = tmp_path / "baseline.json"
    with pytest.raises(InputError, match="cannot read"):
        load_baseline(path)
    with pytest.raises(InputError, match="regular file"):
        load_baseline(tmp_path)
    path.write_bytes(b"\xff")
    with pytest.raises(InputError, match="cannot read"):
        load_baseline(path)
    with path.open("wb") as stream:
        stream.seek(MAX_BYTES)
        stream.write(b"x")
    with pytest.raises(InputError, match="larger than 5 MB"):
        load_baseline(path)


@pytest.mark.parametrize("target", ["register", "config", "drills", "report"])
def test_baseline_write_protects_inputs_and_report(tmp_path, capsys, target):
    register = _register(tmp_path)
    config = tmp_path / "config.yaml"
    config.write_text("fail_on: high\n")
    log = tmp_path / "drills.yaml"
    log.write_text("drills: []\n")
    report = tmp_path / "report.json"
    args = ["check", str(register), "--config", str(config), "--drills", str(log)]
    paths = {"register": register, "config": config, "drills": log, "report": report}
    before = {p: p.read_bytes() for p in (register, config, log)}
    if target == "report":
        args += ["--output", str(report)]
    assert main([*args, "--write-baseline", str(paths[target])]) == 2
    assert capsys.readouterr().err.startswith("resilint: error:")
    assert all(p.read_bytes() == data for p, data in before.items())
    assert not report.exists()


def test_report_cannot_overwrite_loaded_baseline(tmp_path, capsys):
    register = _register(tmp_path)
    baseline = tmp_path / "baseline.json"
    baseline.write_text(dump_baseline([]))
    before = baseline.read_bytes()
    assert main(["check", str(register), "--baseline", str(baseline),
                 "--output", str(baseline)]) == 2
    assert "must not be the input file" in capsys.readouterr().err
    assert baseline.read_bytes() == before


def test_baseline_options_are_explicit_and_mutually_exclusive(capsys):
    with pytest.raises(SystemExit) as error:
        main(["check", "unused", "--baseline", "a", "--write-baseline", "b"])
    assert error.value.code == 2
    capsys.readouterr()
    assert main(["check", "unused", "--baseline", ""]) == 2
    assert "baseline path must not be empty" in capsys.readouterr().err


def test_active_ignore_is_not_baked_into_baseline(tmp_path, capsys):
    register = _register(tmp_path)
    config = tmp_path / "settings.yaml"
    baseline = tmp_path / "baseline.json"
    row = {"rule": "RL001", "vendor": "v1", "reason": "Temporary exception",
           "expires": (date.today() + timedelta(days=1)).isoformat()}
    config.write_text(json.dumps({"ignore": [row]}))
    args = ["check", str(register), "--config", str(config), "--format", "json"]
    assert main([*args, "--write-baseline", str(baseline)]) == 0
    row["expires"] = (date.today() - timedelta(days=1)).isoformat()
    config.write_text(json.dumps({"ignore": [row]}))
    capsys.readouterr()
    assert main([*args, "--baseline", str(baseline)]) == 1
    assert [f["rule_id"] for f in json.loads(capsys.readouterr().out)["findings"]] == ["RL001"]


def test_baseline_respects_output_root(tmp_path, monkeypatch, capsys):
    register = _register(tmp_path)
    root = tmp_path / "allowed"
    root.mkdir()
    monkeypatch.setenv("RESILINT_OUTPUT_ROOT", str(root))
    target = tmp_path / "outside.json"
    assert main(["check", str(register), "--write-baseline", str(target)]) == 2
    assert "outside" in capsys.readouterr().err
    assert not target.exists()


def test_generated_baseline_cap_preserves_existing_file(tmp_path, monkeypatch, capsys):
    import resilint.baseline as module
    register = _register(tmp_path)
    target = tmp_path / "baseline.json"
    target.write_text("existing")
    monkeypatch.setattr(module, "MAX_BYTES", 10)
    assert main(["check", str(register), "--write-baseline", str(target)]) == 2
    assert "generated baseline larger" in capsys.readouterr().err
    assert target.read_text() == "existing"
