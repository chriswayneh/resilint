"""Spreadsheet CSV formats and row-specific CLI errors."""

import csv
import io

import pytest

from resilint.cli import main
from resilint.loader import InputError, load, parse_csv


@pytest.mark.parametrize("delimiter", [",", ";"])
def test_bom_crlf_headers_and_quoted_lists(tmp_path, delimiter):
    out = io.StringIO(newline="")
    writer = csv.writer(out, delimiter=delimiter)
    writer.writerow([" ID ", " CRITICALITY ", " RECORD_TYPE ", " RTO_HOURS ",
                     " RECOVERY_TIME_HOURS ", " CONTACTS ", " SUPPORTS_PROCESSES "])
    writer.writerow(["p1", "critical", "process", "2", "", "", ""])
    writer.writerow(["v1", "high", "vendor", "", "4", "a@example.com;b@example.com", "p1;p2"])
    path = tmp_path / "register.csv"
    payload = ("\ufeff" + out.getvalue()).encode("utf-8")
    path.write_bytes(payload)
    reg = load(path, csv_delimiter=delimiter)
    assert reg["processes"]["p1"]["rto_hours"] == 2
    assert reg["vendors"][0]["contacts"] == ["a@example.com", "b@example.com"]
    assert reg["vendors"][0]["supports_processes"] == ["p1", "p2"]
    assert reg["lines"] == {"v1": 3}
    assert path.read_bytes() == payload


@pytest.mark.parametrize("body,row", [
    ("id,criticality\nv1,high,extra\n", 2),
    ("id,criticality\nv1\n", 2),
    ('id,criticality\n"v1,high\n', 2),
    ('"id,criticality\n', 1),
    ("id,criticality\nv1,urgent\n", 2),
    ("id,criticality,recovery_time_hours\nv1,high,nope\n", 2),
    ("id,criticality,last_tested\nv1,high,yesterday\n", 2),
    ("id,criticality\nv1,high\nv1,low\n", 3),
    ("id,criticality\n,high\n", 2),
    ("id,record_type,rto_hours\np1,process,nope\n", 2),
    ("id,record_type\nx,other\n", 2),
    ("id, ID \na,b\n", 1),
    ("id,\na,b\n", 1),
    ("name,criticality\na,high\n", 1),
    ('id,criticality,contacts\nv1,high,"line one\nline two"\nv2,urgent,x\n', 4),
])
def test_bad_csv_reports_physical_row(tmp_path, capsys, body, row):
    path = tmp_path / "bad.csv"
    path.write_text(body, encoding="utf-8")
    with pytest.raises(InputError, match=f"CSV row {row}:"):
        load(path)
    assert main(["check", str(path), "--format", "json"]) == 2
    captured = capsys.readouterr()
    assert f"CSV row {row}:" in captured.err
    assert captured.out == ""


@pytest.mark.parametrize("command", ["check", "export-roi", "drill"])
def test_csv_delimiter_reaches_each_register_command(tmp_path, capsys, command):
    path = tmp_path / "register.csv"
    path.write_text("id;criticality\nv1;low\n", encoding="utf-8")
    if command == "drill":
        args = ["drill", "record", str(path), "--vendor", "v1", "--kind", "test",
                "--result", "pass", "--log", str(tmp_path / "drills.yaml")]
    elif command == "export-roi":
        args = [command, str(path), "--out-dir", str(tmp_path)]
    else:
        args = [command, str(path), "--format", "json"]
    assert main([*args, "--csv-delimiter", ";"]) == 0
    assert capsys.readouterr().err == ""


def test_invalid_delimiter_is_controlled():
    with pytest.raises(InputError, match="delimiter"):
        parse_csv("id\nv1", delimiter="||")
    with pytest.raises(SystemExit) as error:
        main(["check", "unused.csv", "--csv-delimiter", "||"])
    assert error.value.code == 2
