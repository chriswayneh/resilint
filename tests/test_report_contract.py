"""Schema and snapshots freeze deliberate report behavior with fixed inputs."""

import json
from datetime import date
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, ValidationError

from resilint import report
from resilint.drills import apply
from resilint.loader import load
from resilint.rules import RULES, check

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures"
SCHEMA = json.loads((ROOT / "schema/report.v1.json").read_text(encoding="utf-8"))


def report_case():
    register = load(FIXTURES / "report-register.yaml")
    register["source"] = "fixtures/report-register.yaml"
    apply(register, [{"vendor": "example-vendor-b", "date": date(2026, 10, 1),
                      "kind": "test", "result": "fail", "notes": "Fictional failed drill"}])
    findings = check(register, today=date(2026, 11, 2))
    return register, findings


@pytest.mark.parametrize("fmt", sorted(report.FORMATS))
def test_report_golden(fmt, monkeypatch):
    monkeypatch.setattr(report, "__version__", "0.0.0")
    register, findings = report_case()
    assert {finding.rule_id for finding in findings} == set(RULES)
    assert len([f for f in findings if f.rule_id == "RL006"]) == 2
    actual = report.FORMATS[fmt](findings, register) + "\n"
    assert actual == (FIXTURES / "reports" / f"report.{fmt}").read_text(encoding="utf-8")


def test_json_report_schema():
    Draft202012Validator.check_schema(SCHEMA)
    register, findings = report_case()
    validator = Draft202012Validator(SCHEMA)
    validator.validate(json.loads(report.as_json(findings, register)))
    validator.validate(json.loads(report.as_json([], register)))


@pytest.mark.parametrize("mutation", ["missing_field", "bad_severity", "bad_refs", "bad_tool"])
def test_report_schema_rejects_broken_contract(mutation):
    register, findings = report_case()
    data = json.loads(report.as_json(findings, register))
    if mutation == "missing_field":
        del data["findings"][0]["field"]
    elif mutation == "bad_severity":
        data["findings"][0]["severity"] = "urgent"
    elif mutation == "bad_refs":
        data["findings"][0]["regulation_refs"] = {"DORA": "not an array"}
    else:
        data["tool"] = "another-tool"
    with pytest.raises(ValidationError):
        Draft202012Validator(SCHEMA).validate(data)


def test_report_schema_allows_additive_fields():
    register, findings = report_case()
    data = json.loads(report.as_json(findings, register))
    data["future_metadata"] = {}
    data["findings"][0]["future_detail"] = True
    Draft202012Validator(SCHEMA).validate(data)
