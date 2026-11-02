"""Tests for resilint rules."""


import pytest

from resilint.loader import normalize
from resilint.rules import check
from tests.helpers import TODAY, good_vendor


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


def test_contact_verification_missing_and_stale():
    assert "RL008" in run(good_vendor(contacts_verified=None))
    assert "RL008" in run(good_vendor(contacts_verified="2025-01-01"))
    assert "RL008" not in run(good_vendor(contacts_verified="2025-01-01"), contact_days=1000)


def test_contact_verification_skipped_without_contacts():
    ids = run(good_vendor(contacts=[], contacts_verified=None))
    assert "RL003" in ids and "RL008" not in ids


def test_refs_split_and_prefix():
    from resilint.rules import RULES, refs
    r = refs(RULES["RL001"][2])
    assert r["DORA"] == ["Art. 30(3)(b)", "Art. 30(2)(f)"]
    assert r["NIS2"] == ["Art. 21(2)(d)"] and r["PRA SS2/21"] == ["ch. 6"]
    for _n, _s, reg in RULES.values():
        assert all(refs(reg)[fw] for fw in ("DORA", "NIS2", "PRA SS2/21"))
