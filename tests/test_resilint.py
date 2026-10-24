from datetime import date

import pytest

from resilint.cli import main
from resilint.loader import InputError, load, normalize, parse_csv
from resilint.rules import check

TODAY = date(2026, 10, 1)


def good_vendor(**kw):
    v = {"id": "v1", "criticality": "critical", "notification_sla_hours": 4,
         "recovery_time_hours": 2, "contacts": [{"email": "a@example.com"}],
         "exit_plan": True, "last_tested": "2026-06-01", "supports_processes": ["p1"]}
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


@pytest.mark.parametrize("fmt", ["text", "json", "md"])
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
