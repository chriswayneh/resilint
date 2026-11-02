"""Tests for resilint report."""

from pathlib import Path

import pytest

from resilint.cli import main
from resilint.loader import normalize
from resilint.rules import check
from tests.helpers import TODAY, _write, good_vendor


@pytest.mark.parametrize("fmt", ["text", "json", "md", "sarif", "regmap"])
def test_formats(capsys, fmt):
    main(["check", "examples/vendors.yaml", "--format", fmt])
    out = capsys.readouterr().out
    assert "example-cloud-wms" in out and "not legal advice" in out


def test_md_escape_blocks_markup():
    from resilint.report import _md_escape
    out = _md_escape("<img src=x>[link](http://e)`c`*b*|&_")
    for ch in "<>[]`*|_":
        assert ch not in out
    assert "&amp;" in out and "&lt;" in out


def test_sarif_structure(capsys):
    import json
    main(["check", "examples/vendors.yaml", "--format", "sarif"])
    doc = json.loads(capsys.readouterr().out)
    assert doc["version"] == "2.1.0"
    run_ = doc["runs"][0]
    rule_ids = {r["id"] for r in run_["tool"]["driver"]["rules"]}
    assert {"RL001", "RL008"} <= rule_ids
    res = run_["results"]
    assert res and all(r["ruleId"] in rule_ids for r in res)
    loc = res[0]["locations"][0]["physicalLocation"]
    assert loc["artifactLocation"]["uri"] == "examples/vendors.yaml"
    wms = next(r for r in res if r["properties"]["vendor"] == "example-cloud-wms")
    line = wms["locations"][0]["physicalLocation"]["region"]["startLine"]
    assert "id: example-cloud-wms" in Path("examples/vendors.yaml").read_text().splitlines()[line - 1]
    assert all("not legal advice" in r["message"]["text"] for r in res)
    assert {r["level"] for r in res} <= {"error", "warning", "note"}


def test_sarif_csv_line_numbers(capsys):
    import json
    main(["check", "examples/vendors.csv", "--format", "sarif"])
    res = json.loads(capsys.readouterr().out)["runs"][0]["results"]
    lines = Path("examples/vendors.csv").read_text().splitlines()
    for r in res:
        n = r["locations"][0]["physicalLocation"]["region"]["startLine"]
        assert r["properties"]["vendor"] in lines[n - 1]


def test_sarif_uri_relative_to_cwd(tmp_path, monkeypatch, capsys):
    import json
    src = _write(tmp_path, "v.yaml", "vendors: [{id: a, criticality: high}]\n")
    monkeypatch.chdir(tmp_path)
    main(["check", str(src), "--format", "sarif"])
    res = json.loads(capsys.readouterr().out)["runs"][0]["results"]
    assert res[0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "v.yaml"


def test_sarif_uri_quoted_and_outside_cwd(tmp_path, monkeypatch, capsys):
    import json
    d = tmp_path / "in"
    d.mkdir()
    src = _write(d, "my reg%1.yaml", "vendors: [{id: a, criticality: high}]\n")
    monkeypatch.chdir(tmp_path)
    main(["check", str(src), "--format", "sarif"])
    loc = json.loads(capsys.readouterr().out)["runs"][0]["results"][0]["locations"][0]
    art = loc["physicalLocation"]["artifactLocation"]
    assert art == {"uri": "in/my%20reg%251.yaml", "uriBaseId": "%SRCROOT%"}
    other = tmp_path / "cwd"
    other.mkdir()
    monkeypatch.chdir(other)
    main(["check", str(src), "--format", "sarif"])
    out = json.loads(capsys.readouterr().out)["runs"][0]["results"][0]
    assert out["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "my%20reg%251.yaml"


def test_json_has_regulation_refs(capsys):
    import json
    main(["check", "examples/vendors.yaml", "--format", "json"])
    f = json.loads(capsys.readouterr().out)["findings"][0]
    assert set(f["regulation_refs"]) == {"DORA", "NIS2", "PRA SS2/21"}
    assert f["regulation_note"] == "draft mapping, not legal advice"


def test_regmap_report(capsys):
    main(["check", "examples/vendors.yaml", "--format", "regmap"])
    out = capsys.readouterr().out
    assert "draft mapping, not legal advice" in out
    for h in ("## DORA", "## NIS2", "## PRA SS2/21"):
        assert h in out
    assert "| Art. 28(8) | RL004 | 1 | example-cloud-wms |" in out


def test_regmap_escapes_vendor():
    from resilint.report import regmap
    reg = normalize({"vendors": [good_vendor(id="<b>|x", exit_plan=False)]})
    out = regmap(check(reg, today=TODAY), reg)
    assert "<b>" not in out and "&lt;b&gt;&#124;x" in out
