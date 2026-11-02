"""Load a vendor register from YAML or CSV into one normalized schema."""

from __future__ import annotations

import csv
import io
import math
import os
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml

CRITICALITIES = ("critical", "high", "medium", "low")
MAX_BYTES = 5 * 1024 * 1024
SCHEMA_VERSIONS = (1,)
# ISO 3166-1 alpha-2 officially assigned codes (249).
ISO_COUNTRIES = frozenset("""
AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW
""".split())  # noqa: SIM905


class InputError(Exception):
    """Raised for unreadable or invalid input (exit code 2)."""

    def __init__(self, message: str, *, path: str | None = None, line: int = 0):
        super().__init__(message)
        self.path = path
        self.line = line


class _AliasRefused(yaml.YAMLError):
    """A YAML anchor/alias was found; aliases are refused."""

    def __init__(self, message: str, *, line: int = 0):
        super().__init__(message)
        self.line = line


class _NoAliasLoader(yaml.SafeLoader):
    """SafeLoader that refuses YAML anchors/aliases (blocks alias bombs)."""

    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            line = self.peek_event().start_mark.line + 1
            raise _AliasRefused(f"YAML anchors/aliases are not allowed (line {line})", line=line)
        return super().compose_node(parent, index)

    def get_single_data(self):
        try:
            return super().get_single_data()
        except (ValueError, OverflowError) as e:
            raise yaml.YAMLError(f"invalid YAML value ({e.__class__.__name__})") from None


def _num(value: Any, field: str, ctx: str) -> float | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, bool):
        raise InputError(f"{ctx}: {field} must be a number of hours")
    try:
        n = float(value)
    except (TypeError, ValueError, OverflowError):
        raise InputError(f"{ctx}: {field} must be a number of hours, got {value!r}") from None
    if not math.isfinite(n):
        raise InputError(f"{ctx}: {field} must be a finite number of hours")
    if n < 0:
        raise InputError(f"{ctx}: {field} must not be negative")
    return n


def _date(value: Any, ctx: str, field: str = "last_tested") -> date | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        raise InputError(f"{ctx}: {field} must be an ISO date (YYYY-MM-DD)") from None


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


def _lei(value: Any, ctx: str) -> str | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    s = str(value).strip().upper()
    if not re.fullmatch(r"[0-9A-Z]{18}[0-9]{2}", s):
        raise InputError(f"{ctx}: lei must be 20 characters (ISO 17442)")
    if int("".join(str(int(c, 36)) for c in s)) % 97 != 1:
        raise InputError(f"{ctx}: lei check digits are invalid")
    return s


def _country(value: Any, ctx: str) -> str | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    s = str(value).strip().upper()
    if s not in ISO_COUNTRIES:
        raise InputError(f"{ctx}: country must be an assigned ISO 3166-1 alpha-2 code, got {s!r}")
    return s


def normalize(data: Any, *, csv_rows: tuple[list[int], list[int]] | None = None) -> dict:
    if not isinstance(data, dict):
        raise InputError("top level must be a mapping with 'vendors' (and optional 'processes')")
    version = data.get("schema_version", 1)
    if isinstance(version, str) and version.strip().isdecimal():
        try:
            version = int(version.strip())
        except ValueError:
            raise InputError("unsupported schema_version; supported: 1") from None
    if isinstance(version, bool) or version not in SCHEMA_VERSIONS:
        raise InputError(f"unsupported schema_version {version!r}; supported: "
                         + ", ".join(str(n) for n in SCHEMA_VERSIONS))
    raw_vendors = data.get("vendors")
    if not isinstance(raw_vendors, list):
        raise InputError("'vendors' must be a list")
    raw_procs = data.get("processes") or []
    if not isinstance(raw_procs, list):
        raise InputError("'processes' must be a list")

    processes = {}
    for i, p in enumerate(raw_procs):
        ctx = f"CSV row {csv_rows[1][i]}" if csv_rows is not None else f"processes[{i}]"
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
            "criticality_assessed": bool(str(p.get("criticality") or "").strip()),
            "rto_hours": _num(p.get("rto_hours"), "rto_hours", ctx),
        }

    vendors = []
    seen = set()
    for i, v in enumerate(raw_vendors):
        ctx = f"CSV row {csv_rows[0][i]}" if csv_rows is not None else f"vendors[{i}]"
        if not isinstance(v, dict) or not v.get("id"):
            raise InputError(f"{ctx}: each vendor needs an 'id'")
        vid = str(v["id"]).strip()
        if vid in seen:
            raise InputError(f"{ctx}: duplicate vendor id {vid!r}")
        seen.add(vid)
        ctx = f"{ctx}: vendor {vid}" if csv_rows is not None else f"vendor {vid}"
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
            "lei": _lei(v.get("lei"), ctx),
            "country": _country(v.get("country"), ctx),
            "contacts_verified": _date(v.get("contacts_verified"), ctx, "contacts_verified"),
            "supports_processes": _list(v.get("supports_processes"), ctx, "supports_processes"),
        })
    return {"schema_version": version, "vendors": vendors, "processes": processes}


def parse_csv(text: str, delimiter: str = ",") -> dict:
    """CSV: one row per vendor. Processes use rows with record_type=process."""
    if delimiter not in (",", ";"):
        raise InputError("CSV delimiter must be ',' or ';'")
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff"), newline=""),
                            delimiter=delimiter, strict=True)
    vendors: list[dict] = []
    processes: list[dict] = []
    lines: dict[str, int] = {}
    vendor_rows: list[int] = []
    process_rows: list[int] = []
    try:
        headers = [f.strip().lower() for f in (reader.fieldnames or [])]
        if not headers or "id" not in headers:
            raise InputError("CSV row 1: header must include 'id'")
        if any(not f for f in headers) or len(set(headers)) != len(headers):
            raise InputError("CSV row 1: header names must be nonempty and unique")
        reader.fieldnames = headers
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise InputError(f"CSV row {reader.line_num}: field count does not match header")
            row = {k: v.strip() for k, v in row.items()}
            kind = row.get("record_type", "vendor").lower() or "vendor"
            if kind == "process":
                processes.append(row)
                process_rows.append(reader.line_num)
            elif kind == "vendor":
                vendors.append(row)
                vendor_rows.append(reader.line_num)
                lines.setdefault(row.get("id", ""), reader.line_num)
            else:
                raise InputError(f"CSV row {reader.line_num}: record_type must be vendor or process")
    except csv.Error as e:
        line = max(1, reader.reader.line_num)
        raise InputError(f"CSV row {line}: invalid CSV ({e})") from None
    return {"vendors": vendors, "processes": processes, "_lines": lines,
            "_rows": (vendor_rows, process_rows)}


def _yaml_lines(text: str, ids) -> dict:
    """Best-effort line of each vendor's `id:` entry, for SARIF annotations."""
    want, out = set(ids), {}
    pat = re.compile(r"""^\s*(?:-\s*)?id:\s*["']?([^"'#]+?)["']?\s*(?:#.*)?$""")
    for n, line in enumerate(text.splitlines(), 1):
        m = pat.match(line)
        if m and m.group(1) in want and m.group(1) not in out:
            out[m.group(1)] = n
    return out


def _load(path: str | Path, *, csv_delimiter: str = ",") -> dict:
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
    csv_lines = None
    csv_rows = None
    if p.suffix.lower() == ".csv":
        data = parse_csv(text, delimiter=csv_delimiter)
        csv_lines = data.pop("_lines")
        csv_rows = data.pop("_rows")
    else:
        try:
            data = yaml.load(text, Loader=_NoAliasLoader)  # nosec B506 - SafeLoader subclass
        except _AliasRefused as e:
            raise InputError(f"{p}: {e}", line=e.line) from None
        except yaml.YAMLError as e:
            mark = getattr(e, "problem_mark", None)
            raise InputError(f"{p}: invalid YAML ({e.__class__.__name__})",
                             line=mark.line + 1 if mark is not None else 0) from None
        except RecursionError:
            raise InputError(f"{p}: YAML nested too deeply") from None
    try:
        reg = normalize(data, csv_rows=csv_rows)
    except RecursionError:
        raise InputError(f"{p}: input nested too deeply") from None
    except (ValueError, OverflowError) as e:
        raise InputError(f"{p}: invalid input value ({e.__class__.__name__})") from None
    ids = [v["id"] for v in reg["vendors"]]
    try:
        rel = Path(os.path.relpath(p)).as_posix()
    except ValueError:  # different drive on Windows
        rel = p.name
    if rel == ".." or rel.startswith("../"):
        rel = p.name
    reg["source"] = quote(rel)
    reg["lines"] = csv_lines if csv_lines is not None else _yaml_lines(text, ids)
    return reg


def load(path: str | Path, *, csv_delimiter: str = ",") -> dict:
    """Load a register, retaining file and known physical-line context on errors."""
    try:
        return _load(path, csv_delimiter=csv_delimiter)
    except InputError as error:
        error.path = str(path)
        match = re.match(r"CSV row ([0-9]+):", str(error))
        if match:
            error.line = int(match.group(1))
        raise
