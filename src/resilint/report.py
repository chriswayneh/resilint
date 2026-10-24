"""Text, JSON, and Markdown output."""

from __future__ import annotations

import json
from collections import Counter

from . import __version__
from .rules import REG_NOTE, RULES, SEVERITIES


def _order(findings):
    return sorted(findings, key=lambda f: (-SEVERITIES.index(f.severity), f.vendor, f.rule_id))


def _md_escape(s: str) -> str:
    s = s.replace("\r", " ").replace("\n", " ")
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    for ch in "\\|[]`*_":
        s = s.replace(ch, "&#" + str(ord(ch)) + ";")
    return s


def text(findings, register) -> str:
    lines = [f"{f.severity.upper():8} {f.rule_id} {f.vendor}: {f.message}\n"
             f"         maps to: {f.regulation} ({REG_NOTE})" for f in _order(findings)]
    c = Counter(f.severity for f in findings)
    summary = ", ".join(f"{c[s]} {s}" for s in reversed(SEVERITIES) if c[s])
    lines.append(f"{len(findings)} findings" + (f" ({summary})" if summary else "") + ".")
    return "\n".join(lines)


def as_json(findings, register) -> str:
    return json.dumps({"tool": "resilint", "version": __version__,
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
    out += ["", f"_Regulation references are a {REG_NOTE}. Generated offline by resilint {__version__}._"]
    return "\n".join(out)


_SARIF_LEVEL = {"critical": "error", "high": "error", "medium": "warning", "low": "note"}


def sarif(findings, register) -> str:
    """SARIF 2.1.0 for code-scanning / pull request annotations."""
    uri = register.get("source", "")
    rules = [{"id": rid, "name": name,
              "shortDescription": {"text": name.replace("-", " ")},
              "defaultConfiguration": {"level": _SARIF_LEVEL[sev]},
              "properties": {"regulation": reg, "regulation_note": REG_NOTE}}
             for rid, (name, sev, reg) in RULES.items()]
    results = [{"ruleId": f.rule_id, "level": _SARIF_LEVEL[f.severity],
                "message": {"text": f"{f.vendor}: {f.message} "
                                    f"(maps to {f.regulation}; {REG_NOTE})"},
                "locations": [{"physicalLocation": {
                    "artifactLocation": {"uri": uri},
                    "region": {"startLine": register.get("lines", {}).get(f.vendor, 1)}}}],
                "partialFingerprints": {"resilint/v1": f"{f.rule_id}:{f.vendor}"},
                "properties": {"severity": f.severity, "vendor": f.vendor}}
               for f in _order(findings)]
    return json.dumps({
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json", "version": "2.1.0",
        "runs": [{"tool": {"driver": {"name": "resilint", "version": __version__,
                                      "informationUri": "https://github.com/chriswayneh/resilint",
                                      "rules": rules}},
                  "results": results}]}, indent=2)


FORMATS = {"text": text, "json": as_json, "md": markdown, "sarif": sarif}
