"""Draft export toward DORA register-of-information (RoI) templates.

Column choices are a draft mapping, not legal advice, and do not replace the
official templates. Validate the result with an RoI validator before use.
"""

from __future__ import annotations

import csv
import io

from .rules import REG_NOTE

_UNSAFE = ("=", "+", "-", "@", "\t", "\r")


def _cell(value) -> str:
    """Stringify and neutralize spreadsheet formula injection."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        value = f"{value:g}"
    s = str(value).replace("\r", " ").replace("\n", " ")
    return "'" + s if s.startswith(_UNSAFE) else s


def _csv(header, rows) -> str:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows([[_cell(c) for c in row] for row in rows])
    return buf.getvalue()


def export(register: dict) -> dict[str, str]:
    """Return {filename: csv_text} for the draft RoI-oriented tables."""
    vendors, procs = register["vendors"], register["processes"]
    providers = _csv(
        ["provider_id", "lei", "legal_name", "country", "criticality",
         "notification_sla_hours", "recovery_time_hours", "exit_plan", "last_tested"],
        [[v["id"], v["lei"], v["name"], v["country"], v["criticality"],
          v["notification_sla_hours"], v["recovery_time_hours"], v["exit_plan"],
          v["last_tested"].isoformat() if v["last_tested"] else None] for v in vendors])
    functions = _csv(
        ["function_id", "function_name", "critical_or_important", "rto_hours"],
        [[p["id"], p["name"], p["criticality"] == "critical", p["rto_hours"]]
         for p in procs.values()])
    links = _csv(
        ["provider_id", "function_id", "function_known"],
        [[v["id"], pid, pid in procs] for v in vendors for pid in v["supports_processes"]])
    note = (f"resilint draft RoI export ({REG_NOTE}).\n"
            "b_05_01_providers.csv  -> toward template B_05.01 (ICT third-party service providers)\n"
            "b_06_01_functions.csv  -> toward template B_06.01 (functions identification)\n"
            "b_02_02_links.csv      -> toward template B_02.02 (provider-to-function links)\n"
            "Not official templates. Many required RoI fields are not captured; "
            "complete and validate with an RoI validator before submission.\n")
    return {"b_05_01_providers.csv": providers, "b_06_01_functions.csv": functions,
            "b_02_02_links.csv": links, "README.txt": note}
