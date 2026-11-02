"""Tests for resilint loader."""

from datetime import date

import pytest

from resilint.cli import main
from resilint.loader import InputError, load, normalize, parse_csv
from resilint.rules import check
from tests.helpers import TODAY, _write, good_vendor


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


def test_yaml_aliases_refused(tmp_path):
    bomb = "a: &a [x, x]\nb: &b [*a, *a]\nvendors: [*b]\n"
    with pytest.raises(InputError, match="anchors/aliases are not allowed"):
        load(_write(tmp_path, "bomb.yaml", bomb))


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


def test_yaml_unquoted_datetimes(tmp_path):
    body = ("vendors:\n  - id: v1\n    criticality: high\n"
            "    last_tested: 2026-06-01T10:00:00Z\n"
            "    contacts_verified: 2026-09-01 08:30:00\n")
    v = load(_write(tmp_path, "dt.yaml", body))["vendors"][0]
    assert v["last_tested"] == date(2026, 6, 1)
    assert v["contacts_verified"] == date(2026, 9, 1)
    assert type(v["last_tested"]) is date


def test_lei_and_country():
    v = normalize({"vendors": [good_vendor(lei="9845000EXAMPLE000048", country="ie")]})
    assert v["vendors"][0]["lei"] == "9845000EXAMPLE000048"
    assert v["vendors"][0]["country"] == "IE"
    for bad in ({"lei": "SHORT"}, {"lei": "9845000EXAMPLE000049"}, {"country": "IRL"}, {"country": "UK"}, {"country": "EL"}, {"country": "XX"}, {"country": "ZZ"}):
        with pytest.raises(InputError):
            normalize({"vendors": [good_vendor(**bad)]})


def test_country_assigned_codes_accepted():
    for code in ("GB", "GR", "IE", "US"):
        assert normalize({"vendors": [good_vendor(country=code)]})["vendors"][0]["country"] == code


def test_examples_have_lei_and_country():
    for f in ("examples/vendors.yaml", "examples/vendors.csv"):
        v = {x["id"]: x for x in load(f)["vendors"]}["example-cloud-wms"]
        assert v["lei"] == "9845000EXAMPLE000048" and v["country"] == "IE"
