"""Integrated adoption checks on 500 fictional vendors through the public CLI."""

import csv
import json
import shutil
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from resilint.cli import main
from resilint.loader import load
from resilint.rules import RULES

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/large"
INPUTS = ("vendors.yaml", "drills.yaml", "config.yaml")


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    original = {name: (FIXTURE / name).read_bytes() for name in INPUTS}
    for name in INPUTS:
        shutil.copyfile(FIXTURE / name, tmp_path / name)
    monkeypatch.chdir(tmp_path)
    yield tmp_path
    for name, body in original.items():
        assert (FIXTURE / name).read_bytes() == body
        assert (tmp_path / name).read_bytes() == body


def check_json(workspace, name, *extra):
    output = workspace / name
    code = main(["check", str(workspace / "vendors.yaml"), "--drills",
                 str(workspace / "drills.yaml"), "--format", "json", "--output",
                 str(output), *map(str, extra)])
    return code, json.loads(output.read_text(encoding="utf-8"))


def test_large_fixture_is_bounded_and_visibly_synthetic():
    path = FIXTURE / "vendors.yaml"
    assert path.stat().st_size < 500_000
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    ids = {v["id"] for v in data["vendors"]}
    assert len(data["vendors"]) == len(ids) == 500
    assert ids == {f"fictional-vendor-{i:04d}" for i in range(500)}
    assert {v["criticality"] for v in data["vendors"]} == {"critical", "high", "medium", "low"}
    process_ids = {p["id"] for p in data["processes"]}
    assert len(process_ids) == 4
    for vendor in data["vendors"]:
        assert vendor["name"].startswith("Fictional Vendor ")
        assert set(vendor["supports_processes"]) <= process_ids
        assert all(c["email"].endswith("@example.test") for c in vendor["contacts"])
    assert len(load(path)["vendors"]) == 500


@pytest.mark.parametrize("fmt", ["text", "md", "json", "sarif", "regmap"])
def test_large_cli_formats_schema_and_rule_parity(workspace, fmt):
    code, reference = check_json(workspace, "reference.json")
    assert code == 1
    ids = {f["rule_id"] for f in reference["findings"]}
    assert ids == set(RULES)
    schema = json.loads((ROOT / "schema/report.v1.json").read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(reference)
    output = workspace / f"report.{fmt}"
    assert main(["check", str(workspace / "vendors.yaml"), "--drills",
                 str(workspace / "drills.yaml"), "--format", fmt, "--output", str(output)]) == 1
    text = output.read_text(encoding="utf-8")
    assert text
    if fmt == "json":
        assert json.loads(text) == reference
    elif fmt == "sarif":
        results = json.loads(text)["runs"][0]["results"]
        assert len(results) == len(reference["findings"])
        assert {r["ruleId"] for r in results} == ids
    else:
        assert "not legal advice" in text


def test_large_config_baseline_and_new_identities(workspace):
    assert check_json(workspace, "default.json")[0] == 1
    config = ["--config", workspace / "config.yaml"]
    code, configured = check_json(workspace, "configured.json", *config)
    assert code == 0
    assert configured["findings"] and not any(f["rule_id"] == "RL007"
                                             for f in configured["findings"])
    baseline = workspace / "baseline.json"
    assert main(["check", str(workspace / "vendors.yaml"), "--drills",
                 str(workspace / "drills.yaml"), *map(str, config),
                 "--write-baseline", str(baseline)]) == 0
    code, filtered = check_json(workspace, "filtered.json", *config, "--baseline", baseline)
    assert code == 0 and filtered["findings"] == []
    data = yaml.safe_load((workspace / "vendors.yaml").read_text(encoding="utf-8"))
    data["vendors"].append({"id": "fictional-new-vendor", "name": "Fictional new vendor",
                            "criticality": "critical"})
    changed = workspace / "new-vendor.yaml"
    changed.write_text(yaml.safe_dump(data), encoding="utf-8")
    output = workspace / "new-findings.json"
    assert main(["check", str(changed), "--drills", str(workspace / "drills.yaml"),
                 *map(str, config), "--baseline", str(baseline), "--format", "json",
                 "--output", str(output)]) == 0
    findings = json.loads(output.read_text(encoding="utf-8"))["findings"]
    assert findings and {f["vendor"] for f in findings} == {"fictional-new-vendor"}
    assert {"RL001", "RL002", "RL003", "RL004", "RL005"} <= {f["rule_id"] for f in findings}


def test_large_failed_to_passing_drill_overlay(workspace):
    before = check_json(workspace, "before.json")[1]["findings"]
    assert any(f["rule_id"] == "RL009" and f["vendor"] == "fictional-vendor-0000"
               for f in before)
    mutable = workspace / "mutable-drills.yaml"
    shutil.copyfile(workspace / "drills.yaml", mutable)
    assert main(["drill", "record", str(workspace / "vendors.yaml"), "--vendor",
                 "fictional-vendor-0000", "--kind", "test", "--result", "pass",
                 "--date", "2000-01-02", "--notes", "Fictional successful retest",
                 "--log", str(mutable)]) == 0
    output = workspace / "after.json"
    assert main(["check", str(workspace / "vendors.yaml"), "--drills", str(mutable),
                 "--format", "json", "--output", str(output)]) == 1
    after = json.loads(output.read_text(encoding="utf-8"))["findings"]
    assert not any(f["rule_id"] == "RL009" for f in after)


def test_large_roi_export_counts_and_disclaimer(workspace, capsys):
    output = workspace / "roi"
    output.mkdir()
    assert main(["export-roi", str(workspace / "vendors.yaml"), "--out-dir", str(output)]) == 0
    assert "not legal advice" in capsys.readouterr().out
    register = load(workspace / "vendors.yaml")
    tables = {}
    for name in ("b_05_01_providers.csv", "b_06_01_functions.csv", "b_02_02_links.csv"):
        with (output / name).open(encoding="utf-8", newline="") as stream:
            tables[name] = list(csv.DictReader(stream))
    assert len(tables["b_05_01_providers.csv"]) == 500
    assert len(tables["b_06_01_functions.csv"]) == 4
    links = tables["b_02_02_links.csv"]
    assert len(links) == sum(len(v["supports_processes"]) for v in register["vendors"])
    assert {row["function_known"] for row in links} == {"true"}
    assert "not legal advice" in (output / "README.txt").read_text(encoding="utf-8")
