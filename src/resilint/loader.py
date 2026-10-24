"""Load a vendor register from YAML or CSV into one normalized schema."""

from __future__ import annotations

import csv
import io
import math
from datetime import date
from pathlib import Path
from typing import Any

import yaml

CRITICALITIES = ("critical", "high", "medium", "low")
MAX_BYTES = 5 * 1024 * 1024


class InputError(Exception):
    """Raised for unreadable or invalid input (exit code 2)."""


class _NoAliasLoader(yaml.SafeLoader):
    """SafeLoader that refuses YAML anchors/aliases (blocks alias bombs)."""

    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            event = self.peek_event()
            raise yaml.composer.ComposerError(
                None, None, "YAML aliases are not allowed", event.start_mark)
        return super().compose_node(parent, index)


def _num(value: Any, field: str, ctx: str) -> float | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, bool):
        raise InputError(f"{ctx}: {field} must be a number of hours")
    try:
        n = float(value)
    except (TypeError, ValueError):
        raise InputError(f"{ctx}: {field} must be a number of hours, got {value!r}") from None
    if not math.isfinite(n):
        raise InputError(f"{ctx}: {field} must be a finite number of hours")
    if n < 0:
        raise InputError(f"{ctx}: {field} must not be negative")
    return n


def _date(value: Any, ctx: str) -> date | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        raise InputError(f"{ctx}: last_tested must be an ISO date (YYYY-MM-DD)") from None


def _exit_plan(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    s = str(value).strip()
    return bool(s) and s.lower() not in ("false", "no", "n", "0", "none", "null")


def _contacts(value: Any, ctx: str) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [c.strip() for c in value.split(";") if c.strip()]
    if not isinstance(value, list):
        raise InputError(f"{ctx}: contacts must be a list")
    out = []
    for c in value:
        if isinstance(c, dict):
            for key in ("email", "phone"):
                if c.get(key):
                    out.append(str(c[key]).strip())
        elif isinstance(c, str) and c.strip():
            out.append(c.strip())
    return out


def _list(value: Any, ctx: str, field: str) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [p.strip() for p in value.split(";") if p.strip()]
    if not isinstance(value, list):
        raise InputError(f"{ctx}: {field} must be a list")
    if any(isinstance(p, (list, dict)) for p in value):
        raise InputError(f"{ctx}: {field} items must be plain values")
    return [str(p).strip() for p in value if str(p).strip()]


def normalize(data: Any) -> dict:
    if not isinstance(data, dict):
        raise InputError("top level must be a mapping with 'vendors' (and optional 'processes')")
    raw_vendors = data.get("vendors")
    if not isinstance(raw_vendors, list):
        raise InputError("'vendors' must be a list")
    raw_procs = data.get("processes") or []
    if not isinstance(raw_procs, list):
        raise InputError("'processes' must be a list")

    processes = {}
    for i, p in enumerate(raw_procs):
        ctx = f"processes[{i}]"
        if not isinstance(p, dict) or not p.get("id"):
            raise InputError(f"{ctx}: each process needs an 'id'")
        pid = str(p["id"]).strip()
        crit = str(p.get("criticality") or "critical").strip().lower()
        if crit not in CRITICALITIES:
            raise InputError(f"{ctx}: criticality must be one of {', '.join(CRITICALITIES)}")
        processes[pid] = {
            "id": pid,
            "name": str(p.get("name") or pid),
            "criticality": crit,
            "rto_hours": _num(p.get("rto_hours"), "rto_hours", ctx),
        }

    vendors = []
    seen = set()
    for i, v in enumerate(raw_vendors):
        ctx = f"vendors[{i}]"
        if not isinstance(v, dict) or not v.get("id"):
            raise InputError(f"{ctx}: each vendor needs an 'id'")
        vid = str(v["id"]).strip()
        if vid in seen:
            raise InputError(f"{ctx}: duplicate vendor id {vid!r}")
        seen.add(vid)
        ctx = f"vendor {vid}"
        crit = str(v.get("criticality") or "").strip().lower()
        if crit not in CRITICALITIES:
            raise InputError(f"{ctx}: criticality must be one of {', '.join(CRITICALITIES)}")
        vendors.append({
            "id": vid,
            "name": str(v.get("name") or vid),
            "criticality": crit,
            "notification_sla_hours": _num(
                v.get("notification_sla_hours"), "notification_sla_hours", ctx),
            "recovery_time_hours": _num(v.get("recovery_time_hours"), "recovery_time_hours", ctx),
            "contacts": _contacts(v.get("contacts"), ctx),
            "exit_plan": _exit_plan(v.get("exit_plan")),
            "last_tested": _date(v.get("last_tested"), ctx),
            "supports_processes": _list(v.get("supports_processes"), ctx, "supports_processes"),
        })
    return {"vendors": vendors, "processes": processes}


def parse_csv(text: str) -> dict:
    """CSV: one row per vendor. Processes use rows with record_type=process."""
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or "id" not in [f.strip() for f in reader.fieldnames]:
        raise InputError("CSV must have a header row including 'id'")
    vendors, processes = [], []
    for row in reader:
        row = {(k or "").strip(): (v or "").strip() for k, v in row.items() if k}
        kind = row.get("record_type", "vendor").lower() or "vendor"
        if kind == "process":
            processes.append(row)
        elif kind == "vendor":
            vendors.append(row)
        else:
            raise InputError(f"CSV row {row.get('id')!r}: record_type must be vendor or process")
    return {"vendors": vendors, "processes": processes}


def load(path: str | Path) -> dict:
    p = Path(path)
    try:
        if not p.is_file():
            raise InputError(f"{p}: file not found")
        if p.stat().st_size > MAX_BYTES:
            raise InputError(f"{p}: file larger than 5 MB")
        text = p.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise InputError(f"{p}: cannot read file ({e.strerror})") from None
    except UnicodeDecodeError:
        raise InputError(f"{p}: file is not UTF-8 text") from None
    if p.suffix.lower() == ".csv":
        data = parse_csv(text)
    else:
        try:
            data = yaml.load(text, Loader=_NoAliasLoader)  # nosec B506 - SafeLoader subclass
        except yaml.YAMLError as e:
            raise InputError(f"{p}: invalid YAML ({e.__class__.__name__})") from None
        except RecursionError:
            raise InputError(f"{p}: YAML nested too deeply") from None
    try:
        return normalize(data)
    except RecursionError:
        raise InputError(f"{p}: input nested too deeply") from None
