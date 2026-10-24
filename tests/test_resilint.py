from datetime import date
from pathlib import Path

import pytest

from resilint.cli import main
from resilint.loader import InputError, load, normalize, parse_csv
from resilint.rules import check

TODAY = date(2026, 10, 1)


def good_vendor(**kw):
    v = {"id": "v1", "criticality": "critical", "notification_sla_hours": 4,
         "recovery_time_hours": 2, "contacts": [{"email": "a@example.com"}],
         "exit_plan": True, "last_tested": "2026-06-01", "contacts_verified": "2026-09-01", "supports_processes": ["p1"]}
    v.update(kw)
    return v


def run(vendor=None, processes=None, **kw):
    reg = normalize({"vendors": [vendor or good_vendor()],
                     "processes": processes or [{"id": "p1", "rto_hours": 4}]})
    return [f.rule_id for f in check(reg, today=TODAY, **kw)]


def test_clean():
    assert run() == []


@pytest.mark.parametrize("field,value,rule", [
    ("notification_sla_hours", None, "RL001"),
    ("recovery_time_hours", None, "RL002"),
    ("contacts", [], "RL003"),
    ("exit_plan", False, "RL004"),
    ("last_tested", None, "RL005"),
    ("last_tested", "2024-01-01", "RL005"),
    ("recovery_time_hours", 8, "RL006"),
])
def test_rules(field, value, rule):
    assert rule in run(good_vendor(**{field: value}))


def test_stale_days_configurable():
    assert "RL005" not in run(good_vendor(last_tested="2025-01-01"), stale_days=1000)


def test_low_vendor_skipped():
    assert run(good_vendor(criticality="low", exit_plan=False)) == []


def test_concentration():
    procs = [{"id": f"p{i}", "rto_hours": 10} for i in range(4)]
    v = good_vendor(supports_processes=[p["id"] for p in procs])
    assert "RL007" in run(v, procs)
    assert "RL007" not in run(v, procs, max_critical=4)


def test_csv_matches_yaml():
    y = load("examples/vendors.yaml")
    c = load("examples/vendors.csv")
    ids = lambda r: [f.rule_id for f in check(r, today=TODAY)]
    assert ids(y) == ids(c) and ids(y)


def test_csv_semicolon_lists():
    data = parse_csv("id,criticality,contacts,supports_processes\n"
                     "v1,high,a@x.com;+1-555,p1;p2\n")
    reg = normalize(data)
    assert reg["vendors"][0]["contacts"] == ["a@x.com", "+1-555"]
    assert reg["vendors"][0]["supports_processes"] == ["p1", "p2"]


@pytest.mark.parametrize("content", [
    "vendors: notalist", "- 1\n- 2", "vendors: [{name: x}]",
    "vendors: [{id: a, criticality: urgent}]",
    "vendors: [{id: a, criticality: high, recovery_time_hours: soon}]",
    "vendors: [{id: a, criticality: high, last_tested: yesterday}]",
    "vendors: [{id: a, criticality: high}, {id: a, criticality: high}]",
    "!!python/object/apply:os.system ['echo pwned']", "key: [unclosed",
])
def test_bad_input(tmp_path, content):
    f = tmp_path / "v.yaml"
    f.write_text(content)
    with pytest.raises(InputError):
        load(f)
    assert main(["check", str(f)]) == 2


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


@pytest.mark.parametrize("fmt", ["text", "json", "md", "sarif", "regmap"])
def test_formats(capsys, fmt):
    main(["check", "examples/vendors.yaml", "--format", fmt])
    out = capsys.readouterr().out
    assert "example-cloud-wms" in out and "not legal advice" in out


# --- hardening (Red Team L1-L3, QE review) ---

def _write(tmp_path, name, body):
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


def test_yaml_aliases_refused(tmp_path):
    bomb = "a: &a [x, x]\nb: &b [*a, *a]\nvendors: [*b]\n"
    with pytest.raises(InputError, match="anchors/aliases are not allowed"):
        load(_write(tmp_path, "bomb.yaml", bomb))


def test_alias_message_reaches_user(tmp_path, capsys):
    p = _write(tmp_path, "alias.yaml", "a: &x 1\nvendors: [*x]\n")
    assert main(["check", str(p)]) == 2
    err = capsys.readouterr().err
    assert "YAML anchors/aliases are not allowed (line 2)" in err


def test_non_scalar_list_items_rejected():
    with pytest.raises(InputError, match="plain values"):
        normalize({"vendors": [good_vendor(supports_processes=[["p1"]])], "processes": []})


def test_deep_nesting_is_input_error(tmp_path):
    deep = "vendors: " + "[" * 5000 + "]" * 5000 + "\n"
    with pytest.raises(InputError):
        load(_write(tmp_path, "deep.yaml", deep))


@pytest.mark.parametrize("val", [".nan", ".inf", "-.inf"])
def test_yaml_non_finite_rejected(tmp_path, val):
    body = ("vendors:\n  - id: v1\n    criticality: critical\n"
            f"    recovery_time_hours: {val}\n")
    with pytest.raises(InputError, match="finite"):
        load(_write(tmp_path, "nan.yaml", body))


@pytest.mark.parametrize("val", ["nan", "inf"])
def test_csv_non_finite_rejected(val):
    with pytest.raises(InputError, match="finite"):
        normalize({"vendors": [good_vendor(notification_sla_hours=val)], "processes": []})


def test_md_escape_blocks_markup():
    from resilint.report import _md_escape
    out = _md_escape("<img src=x>[link](http://e)`c`*b*|&_")
    for ch in "<>[]`*|_":
        assert ch not in out
    assert "&amp;" in out and "&lt;" in out


# --- v0.2: contact verification, schema version, SARIF ---

def test_contact_verification_missing_and_stale():
    assert "RL008" in run(good_vendor(contacts_verified=None))
    assert "RL008" in run(good_vendor(contacts_verified="2025-01-01"))
    assert "RL008" not in run(good_vendor(contacts_verified="2025-01-01"), contact_days=1000)


def test_contact_verification_skipped_without_contacts():
    ids = run(good_vendor(contacts=[], contacts_verified=None))
    assert "RL003" in ids and "RL008" not in ids


def test_contact_verification_bad_date():
    with pytest.raises(InputError, match="contacts_verified must be an ISO date"):
        normalize({"vendors": [good_vendor(contacts_verified="last week")]})


@pytest.mark.parametrize("ver", [1, "1", None])
def test_schema_version_supported(ver):
    data = {"vendors": [good_vendor()]}
    if ver is not None:
        data["schema_version"] = ver
    assert normalize(data)["schema_version"] == 1


@pytest.mark.parametrize("ver", [2, 0, "two", True, 1.5])
def test_schema_version_unsupported(tmp_path, ver):
    with pytest.raises(InputError, match="schema_version"):
        normalize({"schema_version": ver, "vendors": []})
    p = _write(tmp_path, "v.yaml", f"schema_version: {ver}\nvendors: []\n")
    assert main(["check", str(p)]) == 2


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


def test_sarif_uri_relative_to_cwd(tmp_path, monkeypatch, capsys):
    import json
    src = _write(tmp_path, "v.yaml", "vendors: [{id: a, criticality: high}]\n")
    monkeypatch.chdir(tmp_path)
    main(["check", str(src), "--format", "sarif"])
    res = json.loads(capsys.readouterr().out)["runs"][0]["results"]
    assert res[0]["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "v.yaml"


def test_output_refuses_symlinks(tmp_path):
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


def test_yaml_unquoted_datetimes(tmp_path):
    body = ("vendors:\n  - id: v1\n    criticality: high\n"
            "    last_tested: 2026-06-01T10:00:00Z\n"
            "    contacts_verified: 2026-09-01 08:30:00\n")
    v = load(_write(tmp_path, "dt.yaml", body))["vendors"][0]
    assert v["last_tested"] == date(2026, 6, 1)
    assert v["contacts_verified"] == date(2026, 9, 1)
    assert type(v["last_tested"]) is date


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


# --- v0.3: regulation mapping report, draft RoI export ---

def test_refs_split_and_prefix():
    from resilint.rules import RULES, refs
    r = refs(RULES["RL001"][2])
    assert r["DORA"] == ["Art. 30(3)(b)", "Art. 30(2)(f)"]
    assert r["NIS2"] == ["Art. 21(2)(d)"] and r["PRA SS2/21"] == ["ch. 6"]
    for _n, _s, reg in RULES.values():
        assert all(refs(reg)[fw] for fw in ("DORA", "NIS2", "PRA SS2/21"))


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


def test_lei_and_country():
    v = normalize({"vendors": [good_vendor(lei="9845000EXAMPLE000048", country="ie")]})
    assert v["vendors"][0]["lei"] == "9845000EXAMPLE000048"
    assert v["vendors"][0]["country"] == "IE"
    for bad in ({"lei": "SHORT"}, {"lei": "9845000EXAMPLE000049"}, {"country": "IRL"}, {"country": "UK"}, {"country": "EL"}, {"country": "XX"}, {"country": "ZZ"}):
        with pytest.raises(InputError):
            normalize({"vendors": [good_vendor(**bad)]})


def test_export_roi(tmp_path):
    out = tmp_path / "roi"
    out.mkdir()
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(out)]) == 0
    before = (out / "README.txt").read_text()
    (out / "b_06_01_functions.csv").write_text("mine")
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(out)]) == 2
    assert (out / "b_06_01_functions.csv").read_text() == "mine"
    assert (out / "README.txt").read_text() == before
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(out), "--force"]) == 0
    names = sorted(p.name for p in out.iterdir())
    assert names == ["README.txt", "b_02_02_links.csv", "b_05_01_providers.csv",
                     "b_06_01_functions.csv"]
    prov = (out / "b_05_01_providers.csv").read_text().splitlines()
    assert prov[0].startswith("provider_id,lei,legal_name")
    assert any(line.startswith("example-cloud-wms,") for line in prov)
    assert "not legal advice" in (out / "README.txt").read_text()
    assert "order-fulfilment,Order fulfilment,Yes,4" in (out / "b_06_01_functions.csv").read_text()


def test_export_roi_csv_injection_neutralized():
    from resilint.roi import export
    reg = normalize({"vendors": [good_vendor(name="=HYPERLINK(1)", id="@v")]})
    prov = export(reg)["b_05_01_providers.csv"]
    assert "'=HYPERLINK(1)" in prov and "'@v" in prov
    assert "\n=" not in prov and ",=" not in prov


def test_export_roi_bad_out_dir(tmp_path):
    assert main(["export-roi", "examples/vendors.yaml",
                 "--out-dir", str(tmp_path / "missing")]) == 2
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real)
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(link)]) == 2
    assert not list(real.iterdir())
    bad = _write(tmp_path, "bad.yaml", "vendors: notalist")
    assert main(["export-roi", str(bad), "--out-dir", str(real)]) == 2


def test_export_roi_respects_output_root(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.setenv("RESILINT_OUTPUT_ROOT", str(ws))
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(other)]) == 2
    assert not list(other.iterdir())


# --- v0.4: drill records ---

def _reg(tmp_path, **kw):
    import yaml
    p = tmp_path / "reg.yaml"
    p.write_text(yaml.safe_dump({"vendors": [good_vendor(last_tested="2024-01-01", **kw)],
                                 "processes": [{"id": "p1", "rto_hours": 4}]}))
    return p


def _rec(reg, log, *extra):
    return main(["drill", "record", str(reg), "--vendor", "v1", "--log", str(log), *extra])


def test_drill_pass_updates_last_tested(tmp_path, capsys):
    reg, log = _reg(tmp_path), tmp_path / "drills.yaml"
    assert main(["check", str(reg), "--fail-on", "medium"]) == 1
    assert _rec(reg, log, "--kind", "tabletop", "--result", "pass",
                "--date", date.today().isoformat()) == 0
    assert "last-tested date updated" in capsys.readouterr().out
    assert main(["check", str(reg), "--drills", str(log), "--fail-on", "medium"]) == 0


def test_drill_fail_raises_rl009_and_keeps_last_tested(tmp_path, capsys):
    from resilint.drills import apply, load_log
    reg, log = _reg(tmp_path), tmp_path / "drills.yaml"
    assert _rec(reg, log, "--kind", "test", "--result", "pass", "--date", "2026-05-01") == 0
    assert _rec(reg, log, "--kind", "test", "--result", "fail", "--date", "2026-09-01") == 0
    r = load(reg)
    apply(r, load_log(log))
    assert r["vendors"][0]["last_tested"] == date(2026, 5, 1)
    ids = [f.rule_id for f in check(r, today=TODAY)]
    assert "RL009" in ids and "RL005" not in ids


def test_drill_latest_wins_regardless_of_log_order(tmp_path):
    from resilint.drills import apply, load_log
    reg, log = _reg(tmp_path), tmp_path / "drills.yaml"
    _rec(reg, log, "--kind", "test", "--result", "pass", "--date", "2026-09-01")
    _rec(reg, log, "--kind", "test", "--result", "fail", "--date", "2026-01-01")
    r = load(reg)
    apply(r, load_log(log))
    assert "RL009" not in [f.rule_id for f in check(r, today=TODAY)]


def test_drill_register_untouched(tmp_path):
    reg = _reg(tmp_path)
    before = reg.read_bytes()
    _rec(reg, tmp_path / "d.yaml", "--kind", "test", "--result", "pass")
    assert reg.read_bytes() == before


def test_drill_default_log_next_to_register(tmp_path):
    reg = _reg(tmp_path)
    assert main(["drill", "record", str(reg), "--vendor", "v1", "--kind", "test",
                 "--result", "partial"]) == 0
    assert (tmp_path / "drills.yaml").is_file()


@pytest.mark.parametrize("extra", [
    ["--vendor", "nope"], ["--date", "2026-13-01"], ["--notes", "x" * 501],
])
def test_drill_record_rejects_bad_input(tmp_path, extra):
    reg = _reg(tmp_path)
    args = ["drill", "record", str(reg), "--vendor", "v1", "--kind", "test", "--result", "pass",
            "--log", str(tmp_path / "d.yaml")]
    assert main(args + extra) == 2
    assert not (tmp_path / "d.yaml").exists()


def test_drill_log_refuses_symlink_and_register(tmp_path):
    reg = _reg(tmp_path)
    target = tmp_path / "victim.txt"
    target.write_text("keep")
    (tmp_path / "link.yaml").symlink_to(target)
    assert _rec(reg, tmp_path / "link.yaml", "--kind", "test", "--result", "pass") == 2
    assert target.read_text() == "keep"
    assert _rec(reg, reg, "--kind", "test", "--result", "pass") == 2


def test_drill_log_respects_output_root(tmp_path, monkeypatch):
    reg = _reg(tmp_path)
    root = tmp_path / "root"
    root.mkdir()
    monkeypatch.setenv("RESILINT_OUTPUT_ROOT", str(root))
    assert _rec(reg, tmp_path / "d.yaml", "--kind", "test", "--result", "pass") == 2


@pytest.mark.parametrize("text", [
    "drills: &a [*a]",
    "drills: [{vendor: v1, date: 2026-01-01, kind: test, result: maybe}]",
    "drills: [{vendor: v1, date: 2026-01-01, kind: test, result: pass, notes: [1]}]",
    "drills: [{vendor: ghost, date: 2026-01-01, kind: test, result: pass}]",
    "- just a list",
])
def test_drill_log_invalid(tmp_path, text):
    reg = _reg(tmp_path)
    log = tmp_path / "d.yaml"
    log.write_text(text)
    assert main(["check", str(reg), "--drills", str(log)]) == 2


def test_drill_log_size_cap(tmp_path):
    reg = _reg(tmp_path)
    log = tmp_path / "d.yaml"
    log.write_bytes(b"#" * (5 * 1024 * 1024 + 1))
    assert main(["check", str(reg), "--drills", str(log)]) == 2


def test_drill_in_regmap_and_sarif(tmp_path, capsys):
    reg, log = _reg(tmp_path), tmp_path / "d.yaml"
    _rec(reg, log, "--kind", "tabletop", "--result", "fail")
    capsys.readouterr()
    main(["check", str(reg), "--drills", str(log), "--format", "regmap"])
    out = capsys.readouterr().out
    assert "RL009" in out and "not legal advice" in out
    main(["check", str(reg), "--drills", str(log), "--format", "sarif"])
    assert "RL009" in capsys.readouterr().out


def test_country_assigned_codes_accepted():
    for code in ("GB", "GR", "IE", "US"):
        assert normalize({"vendors": [good_vendor(country=code)]})["vendors"][0]["country"] == code


def test_examples_have_lei_and_country():
    for f in ("examples/vendors.yaml", "examples/vendors.csv"):
        v = {x["id"]: x for x in load(f)["vendors"]}["example-cloud-wms"]
        assert v["lei"] == "9845000EXAMPLE000048" and v["country"] == "IE"


def test_roi_critical_or_important_mapping():
    from resilint.roi import export
    procs = [{"id": "a", "criticality": "critical"}, {"id": "b", "criticality": "high"},
             {"id": "c", "criticality": "medium"}, {"id": "d", "criticality": "low"}, {"id": "e"}]
    out = export(normalize({"vendors": [good_vendor()], "processes": procs}))
    rows = out["b_06_01_functions.csv"].splitlines()[1:]
    got = {r.split(",")[0]: r.split(",")[2] for r in rows}
    assert got == {"a": "Yes", "b": "Yes", "c": "No", "d": "No", "e": "Assessment not performed"}
    assert "Contractual arrangements - specific information" in out["README.txt"]
    assert "partial column set" in out["README.txt"]


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


def test_export_roi_trailing_slash_symlink_refused(tmp_path):
    p = tmp_path / "p"
    real = tmp_path / "real"
    p.mkdir()
    real.mkdir()
    (p / "l").symlink_to(real)
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(p / "l") + "/"]) == 2
    assert not list(real.iterdir())


@pytest.mark.parametrize("val", [" =cmd|x!A0", " \t@x", "\r=1+1", "\n=1+1", "\uff1d1+1",
                                 "-1", "+44 20", "|x", "%x", "\u3000=1"])
def test_cell_formula_variants_neutralized(val):
    from resilint.roi import _cell
    out = _cell(val)
    assert out.startswith("'")
    assert "\r" not in out and "\n" not in out


def test_cell_plain_values_untouched():
    from resilint.roi import _cell
    assert _cell("Example Co") == "Example Co"
    assert _cell(4.0) == "4"
