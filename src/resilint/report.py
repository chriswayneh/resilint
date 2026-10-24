"""Text, JSON, and Markdown output."""

from __future__ import annotations

import json
from collections import Counter

from .rules import REG_NOTE, SEVERITIES


def _order(findings):
    return sorted(findings, key=lambda f: (-SEVERITIES.index(f.severity), f.vendor, f.rule_id))


def _md_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def text(findings, register) -> str:
    lines = [f"{f.severity.upper():8} {f.rule_id} {f.vendor}: {f.message}\n"
             f"         maps to: {f.regulation} ({REG_NOTE})" for f in _order(findings)]
    c = Counter(f.severity for f in findings)
    summary = ", ".join(f"{c[s]} {s}" for s in reversed(SEVERITIES) if c[s])
    lines.append(f"{len(findings)} findings" + (f" ({summary})" if summary else "") + ".")
    return "\n".join(lines)


def as_json(findings, register) -> str:
    return json.dumps({"tool": "resilint", "version": "0.1.0",
                       "findings": [f.to_dict() for f in _order(findings)]}, indent=2)


def markdown(findings, register) -> str:
    vendors = register["vendors"]
    in_scope = [v for v in vendors if v["criticality"] in ("critical", "high")]
    with_gaps = {f.vendor for f in findings}
    c = Counter(f.severity for f in findings)
    out = ["# Vendor resilience gap report", "",
           f"- Vendors in register: **{len(vendors)}**",
           f"- Critical/high vendors checked: **{len(in_scope)}**",
           f"- Vendors with gaps: **{len(with_gaps)}**",
           "- Findings: " + (", ".join(f"**{c[s]}** {s}" for s in reversed(SEVERITIES) if c[s])
                             or "**none**"), ""]
    if findings:
        out += ["| Severity | Vendor | Gap | Rule | Maps to |", "|---|---|---|---|---|"]
        for f in _order(findings):
            out.append(f"| {f.severity} | {_md_escape(f.vendor)} | {_md_escape(f.message)} "
                       f"| {f.rule_id} | {f.regulation} |")
    else:
        out.append("No gaps found for critical or high vendors.")
    out += ["", f"_Regulation references are a {REG_NOTE}. Generated offline by resilint 0.1.0._"]
    return "\n".join(out)


FORMATS = {"text": text, "json": as_json, "md": markdown}
