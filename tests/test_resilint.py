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
