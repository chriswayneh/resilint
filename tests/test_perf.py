"""CI budget for a large fictional CSV register, including JSON reporting."""

import csv
import json
from datetime import date
from time import perf_counter

import pytest

from resilint.cli import main
from resilint.loader import MAX_BYTES


def test_large_register_checks_within_five_seconds(tmp_path, capsys):
    path = tmp_path / "large.csv"
    today = date.today().isoformat()
    fields = ["record_type", "id", "criticality", "rto_hours", "notification_sla_hours",
              "recovery_time_hours", "contacts", "exit_plan", "last_tested",
              "contacts_verified", "supports_processes"]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for i in range(2000):
            writer.writerow({"record_type": "process", "id": f"p{i}",
                             "criticality": "critical", "rto_hours": 2})
        for i in range(10000):
            writer.writerow({"record_type": "vendor", "id": f"v{i}",
                             "criticality": "critical", "notification_sla_hours": 4,
                             "recovery_time_hours": 4, "contacts": "test@example.com",
                             "exit_plan": "yes", "last_tested": today,
                             "contacts_verified": today, "supports_processes": f"p{i % 2000}"})
    original = path.read_bytes()
    assert len(original) < MAX_BYTES

    start = perf_counter()
    code = main(["check", str(path), "--format", "json"])
    elapsed = perf_counter() - start

    captured = capsys.readouterr()
    assert code == 1
    assert captured.err == ""
    findings = json.loads(captured.out)["findings"]
    assert len(findings) == 10000
    by_vendor = {finding["vendor"]: finding for finding in findings}
    assert len(by_vendor) == 10000
    for i in range(10000):
        finding = by_vendor[f"v{i}"]
        assert finding["rule_id"] == "RL006"
        assert finding["vendor"] == f"v{i}"
        assert finding["message"] == f"recovery time 4h exceeds p{i % 2000} RTO 2h"
    assert path.read_bytes() == original
    assert elapsed < 5, f"large-register CLI check took {elapsed:.3f}s (budget: <5s)"


@pytest.mark.parametrize("suffix", ["yaml", "csv"])
def test_oversize_register_has_clear_cli_error(tmp_path, capsys, suffix):
    path = tmp_path / f"oversize.{suffix}"
    with path.open("wb") as stream:
        stream.seek(MAX_BYTES)
        stream.write(b"x")
    assert main(["check", str(path), "--format", "json"]) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "file larger than 5 MB" in captured.err
    assert str(path) in captured.err
