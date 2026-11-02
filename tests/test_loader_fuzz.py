"""Bounded, reproducible input properties for the loader and CLI error boundary."""

import csv
import io
import json
from contextlib import redirect_stderr, redirect_stdout

import pytest
import yaml
from hypothesis import example, given, settings
from hypothesis import strategies as st

from resilint.cli import main
from resilint.loader import InputError, load

TEXT = st.text(st.characters(exclude_categories=("Cs",)), max_size=48)
# Python 3.10's csv.writer cannot serialize NUL; raw/text properties cover it.
CSV_TEXT = st.text(st.characters(exclude_categories=("Cs",), exclude_characters="\x00"),
                   max_size=48)
SCALAR = st.one_of(st.none(), st.booleans(),
                   st.integers(min_value=-(10**100), max_value=10**100), st.floats(), TEXT)
VALUES = st.recursive(
    SCALAR,
    lambda children: st.one_of(st.lists(children, max_size=4),
                               st.dictionaries(TEXT, children, max_size=4)),
    max_leaves=15,
)
REGISTER = st.fixed_dictionaries({
    "vendors": st.lists(st.fixed_dictionaries(
        {"id": TEXT, "criticality": st.sampled_from(["critical", "high", "low", "urgent"])},
        optional={name: VALUES for name in (
            "notification_sla_hours", "recovery_time_hours", "contacts", "exit_plan",
            "last_tested", "contacts_verified", "supports_processes", "lei", "country",
        )},
    ), max_size=4),
}, optional={"schema_version": SCALAR, "processes": VALUES})


@pytest.fixture(scope="module")
def fuzz_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("loader-fuzz")


def _exercise(path, payload):
    path.write_bytes(payload)
    try:
        register = load(path)
    except InputError as error:
        assert str(error)
        expected = (2,)
    else:
        assert register["schema_version"] == 1
        assert isinstance(register["vendors"], list)
        expected = (0, 1)
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(["check", str(path), "--format", "json"])
    assert code in expected
    if code == 2:
        assert err.getvalue().startswith("resilint: error: ")
        assert not out.getvalue()
    else:
        assert isinstance(json.loads(out.getvalue())["findings"], list)
        assert not err.getvalue()
    assert path.read_bytes() == payload
    return code


@pytest.mark.parametrize("suffix", ["yaml", "csv"])
@settings(max_examples=100, derandomize=True, deadline=None)
@given(payload=st.binary(max_size=512))
def test_arbitrary_bytes_have_controlled_outcome(fuzz_dir, suffix, payload):
    _exercise(fuzz_dir / f"bytes.{suffix}", payload)


@settings(max_examples=100, derandomize=True, deadline=None)
@example(text="vendors: [{id: v1, criticality: high, last_tested: 2026-13-01}]")
@example(text="vendors: [{id: v1, criticality: high, last_tested: 2026-01-01T99:00:00Z}]")
@example(text="schema_version: '²'\nvendors: []")
@example(text="vendors: [{id: v1, criticality: high, recovery_time_hours: " + "1" * 400 + "}]")
@example(text="schema_version: '" + "1" * 5000 + "'\nvendors: []")
@example(text="schema_version: " + "1" * 5000 + "\nvendors: []")
@example(text="vendors: [{id: v1, criticality: high, recovery_time_hours: 0x" + "1" * 5000 + "}]")
@example(text="vendors: [{id: 0x" + "1" * 5000 + ", criticality: high}]")
@example(text='"\\UFFFFFFFF"')
@given(text=st.text(st.characters(exclude_categories=("Cs",)), max_size=1024))
def test_yaml_text_has_controlled_outcome(fuzz_dir, text):
    _exercise(fuzz_dir / "text.yaml", text.encode("utf-8"))


@settings(max_examples=150, derandomize=True, deadline=None)
@given(data=st.one_of(VALUES, REGISTER))
def test_yaml_structures_have_controlled_outcome(fuzz_dir, data):
    _exercise(fuzz_dir / "structure.yaml", yaml.safe_dump(data).encode("utf-8"))


@settings(max_examples=100, derandomize=True, deadline=None)
@example(text="id\nv1\rv2")
@example(text="id\n\x00")
@example(text="id\n" + "x" * (csv.field_size_limit() + 1))
@example(text="id," + "x" * (csv.field_size_limit() + 1) + "\nv1,a")
@given(text=st.text(st.characters(exclude_categories=("Cs",)), max_size=1024))
def test_csv_text_has_controlled_outcome(fuzz_dir, text):
    _exercise(fuzz_dir / "text.csv", text.encode("utf-8"))


@settings(max_examples=100, derandomize=True, deadline=None)
@given(rows=st.lists(st.lists(CSV_TEXT, min_size=1, max_size=6), max_size=6))
def test_csv_rows_have_controlled_outcome(fuzz_dir, rows):
    out = io.StringIO(newline="")
    writer = csv.writer(out)
    writer.writerow(["id", "criticality", "recovery_time_hours", "contacts", "last_tested"])
    writer.writerows(rows)
    _exercise(fuzz_dir / "rows.csv", out.getvalue().encode("utf-8"))


@pytest.mark.parametrize("suffix", ["yaml", "csv"])
@settings(max_examples=50, derandomize=True, deadline=None)
@given(hours=st.integers(min_value=0, max_value=10000),
       name=st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789", min_size=1, max_size=20))
def test_valid_registers_remain_usable(fuzz_dir, suffix, hours, name):
    vendor = {"id": name, "criticality": "high", "recovery_time_hours": hours}
    if suffix == "yaml":
        text = yaml.safe_dump({"vendors": [vendor]})
    else:
        out = io.StringIO(newline="")
        writer = csv.DictWriter(out, fieldnames=list(vendor))
        writer.writeheader()
        writer.writerow(vendor)
        text = out.getvalue()
    assert _exercise(fuzz_dir / f"valid.{suffix}", text.encode("utf-8")) in (0, 1)


@pytest.mark.parametrize("timestamp", ["2026-13-01", "2026-02-30"])
def test_shared_yaml_loader_rejects_invalid_drill_dates(tmp_path, timestamp):
    from resilint.drills import load_log

    path = tmp_path / "drills.yaml"
    path.write_text(f"drills: [{{vendor: v1, date: {timestamp}, kind: test, result: pass}}]")
    with pytest.raises(InputError, match="invalid YAML"):
        load_log(path)
