"""Drill records: tabletop or test results attached to vendors in a separate log file.

The register itself is never rewritten (so its comments and layout are kept); `check --drills`
applies the log: a passed or partial drill updates the vendor's effective last-tested date.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import yaml

from .loader import MAX_BYTES, InputError, _AliasRefused, _date, _NoAliasLoader

KINDS = ("tabletop", "test")
RESULTS = ("pass", "partial", "fail")
MAX_NOTES = 500


def _entry(raw: Any, ctx: str, vendor_ids: set[str] | None = None) -> dict:
    if not isinstance(raw, dict):
        raise InputError(f"{ctx}: each drill must be a mapping")
    vendor = str(raw.get("vendor") or "").strip()
    if not vendor:
        raise InputError(f"{ctx}: vendor is required")
    if vendor_ids is not None and vendor not in vendor_ids:
        raise InputError(f"{ctx}: unknown vendor {vendor!r}")
    d = _date(raw.get("date"), ctx, "date")
    if d is None:
        raise InputError(f"{ctx}: date is required")
    if d > date.today():
        raise InputError(f"{ctx}: date {d.isoformat()} is in the future")
    kind = str(raw.get("kind") or "").strip().lower()
    if kind not in KINDS:
        raise InputError(f"{ctx}: kind must be one of {', '.join(KINDS)}")
    result = str(raw.get("result") or "").strip().lower()
    if result not in RESULTS:
        raise InputError(f"{ctx}: result must be one of {', '.join(RESULTS)}")
    notes = raw.get("notes")
    if notes is not None and not isinstance(notes, (str, int, float)):
        raise InputError(f"{ctx}: notes must be text")
    notes = "" if notes is None else str(notes).strip()
    if len(notes) > MAX_NOTES:
        raise InputError(f"{ctx}: notes longer than {MAX_NOTES} characters")
    return {"vendor": vendor, "date": d, "kind": kind, "result": result, "notes": notes}


def load_log(path: str | Path, missing_ok: bool = False,
             vendor_ids: set[str] | None = None) -> list[dict]:
    p = Path(path)
    try:
        if not p.exists() and missing_ok:
            return []
        if not p.is_file():
            raise InputError(f"{p}: drill log not found")
        if p.stat().st_size > MAX_BYTES:
            raise InputError(f"{p}: file larger than 5 MB")
        text = p.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise InputError(f"{p}: cannot read file ({e.strerror})") from None
    except UnicodeDecodeError:
        raise InputError(f"{p}: file is not UTF-8 text") from None
    try:
        data = yaml.load(text, Loader=_NoAliasLoader)  # nosec B506 - SafeLoader subclass
    except _AliasRefused as e:
        raise InputError(f"{p}: {e}") from None
    except yaml.YAMLError as e:
        raise InputError(f"{p}: invalid YAML ({e.__class__.__name__})") from None
    except RecursionError:
        raise InputError(f"{p}: YAML nested too deeply") from None
    if data is None:
        return []
    if not isinstance(data, dict) or not isinstance(data.get("drills", []), list):
        raise InputError(f"{p}: top level must be a mapping with a 'drills' list")
    return [_entry(d, f"{p}: drills[{i}]", vendor_ids) for i, d in enumerate(data.get("drills") or [])]


def dump_log(drills: list[dict]) -> str:
    rows = [{**d, "date": d["date"].isoformat()} for d in drills]
    for r in rows:
        if not r["notes"]:
            del r["notes"]
    return ("# resilint drill log (tabletop and test results per vendor)\n"
            + yaml.safe_dump({"drills": rows}, sort_keys=False, allow_unicode=True))


def apply(register: dict, drills: list[dict]) -> None:
    """Attach drills to vendors; pass/partial drills advance last_tested."""
    by_id = {v["id"]: v for v in register["vendors"]}
    for v in register["vendors"]:
        v.setdefault("drills", [])
    for d in sorted(drills, key=lambda x: x["date"]):
        v = by_id.get(d["vendor"])
        if v is None:
            raise InputError(f"drill log: unknown vendor {d['vendor']!r}")
        v["drills"].append(d)
        if d["result"] in ("pass", "partial"):
            lt: date | None = v["last_tested"]
            if lt is None or d["date"] > lt:
                v["last_tested"] = d["date"]
