"""Shared fictional vendor data and file helpers."""

from datetime import date

TODAY = date(2026, 10, 1)


def good_vendor(**kw):
    v = {"id": "v1", "criticality": "critical", "notification_sla_hours": 4,
         "recovery_time_hours": 2, "contacts": [{"email": "a@example.com"}],
         "exit_plan": True, "last_tested": "2026-06-01", "contacts_verified": "2026-09-01", "supports_processes": ["p1"]}
    v.update(kw)
    return v


def _write(tmp_path, name, body):
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p
