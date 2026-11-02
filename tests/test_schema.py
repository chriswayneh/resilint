"""Validate the published authoring schema and fictional register examples."""

import json
from copy import deepcopy
from datetime import date
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from resilint.loader import ISO_COUNTRIES, InputError, load, normalize

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schema/register.v1.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA, format_checker=FormatChecker())


def _json_value(value):
    def convert(obj):
        if isinstance(obj, date):
            return obj.isoformat()
        raise TypeError(type(obj).__name__)
    return json.loads(json.dumps(value, default=convert, allow_nan=False))


def test_schema_is_valid_and_country_enum_matches_loader():
    Draft202012Validator.check_schema(SCHEMA)
    countries = SCHEMA["$defs"]["vendor"]["properties"]["country"]["enum"]
    assert set(countries) == ISO_COUNTRIES | {None}


def test_yaml_register_example_validates_before_normalization():
    raw = yaml.safe_load((ROOT / "examples/vendors.yaml").read_text(encoding="utf-8"))
    VALIDATOR.validate(_json_value(raw))


def test_csv_register_example_validates_after_projection():
    reg = load(ROOT / "examples/vendors.csv")
    reg["processes"] = list(reg["processes"].values())
    VALIDATOR.validate(_json_value(reg))


@pytest.mark.parametrize("document", [
    {"vendors": []},
    {"vendors": [{"id": "v1", "criticality": "high"}]},
    {"vendors": [], "processes": [{"id": "p1"}]},
    {"vendors": [], "processes": None, "extra": "ignored"},
])
def test_optional_fields_and_defaults(document):
    before = deepcopy(document)
    VALIDATOR.validate(document)
    normalize(document)
    assert document == before


@pytest.mark.parametrize("field,value", [
    ("id", " "), ("criticality", "urgent"), ("recovery_time_hours", -1),
    ("notification_sla_hours", True), ("last_tested", "2026-02-30"),
    ("contacts_verified", "yesterday"), ("country", "ZZ"), ("lei", "not-an-lei"),
    ("contacts", [{}]), ("supports_processes", [["p1"]]), ("exit_plan", {}),
])
def test_invalid_vendor_fields(field, value):
    vendor = {"id": "v1", "criticality": "high", field: value}
    with pytest.raises(ValidationError):
        VALIDATOR.validate({"vendors": [vendor]})


@pytest.mark.parametrize("document", [
    {}, {"vendors": {}}, {"vendors": [{}]}, {"vendors": [{"id": "v1"}]},
    {"vendors": [], "schema_version": 2}, {"vendors": [], "schema_version": True},
    {"vendors": [], "processes": [{}]},
    {"vendors": [], "processes": [{"id": "p1", "rto_hours": -1}]},
])
def test_invalid_structure(document):
    with pytest.raises(ValidationError):
        VALIDATOR.validate(document)


def test_schema_does_not_replace_runtime_identity_checks():
    vendor = {"id": "v1", "criticality": "high"}
    document = {"vendors": [vendor, dict(vendor)]}
    VALIDATOR.validate(document)
    with pytest.raises(InputError, match="duplicate vendor id"):
        normalize(document)
