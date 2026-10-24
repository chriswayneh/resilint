"""Resilience rules. Regulation references are a draft mapping, not legal advice."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date

SEVERITIES = ("low", "medium", "high", "critical")
REG_NOTE = "draft mapping, not legal advice"

RULES = {
    "RL001": ("missing-notification-sla", "high",
              "DORA Art. 30(3)(b), 30(2)(f); NIS2 Art. 21(2)(d); PRA SS2/21 ch. 6"),
    "RL002": ("missing-recovery-time", "high",
              "DORA Art. 30(2)(e), 30(3)(a); NIS2 Art. 21(2)(c); PRA SS2/21 ch. 6"),
    "RL003": ("no-contact", "high", "DORA Art. 30(2); NIS2 Art. 21(2)(d); PRA SS2/21 ch. 6"),
    "RL004": ("no-exit-plan", "high",
              "DORA Art. 28(8), Art. 30(3)(f); NIS2 Art. 21(2)(d); PRA SS2/21 ch. 10"),
    "RL005": ("stale-or-missing-test", "medium",
              "DORA Art. 30(3)(c)-(d); NIS2 Art. 21(2)(f); PRA SS2/21 ch. 10"),
    "RL006": ("recovery-exceeds-rto", "high",
              "DORA Art. 30(2)(e), 30(3)(a); NIS2 Art. 21(2)(c); PRA SS2/21 ch. 10"),
    "RL007": ("concentration-risk", "medium",
              "DORA Art. 28(4)(c), Art. 29; NIS2 Art. 21(2)(d); PRA SS2/21 ch. 5"),
    "RL008": ("stale-or-missing-contact-verification", "medium",
              "DORA Art. 30(2), 28(3); NIS2 Art. 21(2)(d); PRA SS2/21 ch. 6"),
}


@dataclass
class Finding:
    rule_id: str
    rule: str
    severity: str
    vendor: str
    message: str
    regulation: str
    regulation_note: str = REG_NOTE

    def to_dict(self) -> dict:
        return asdict(self)


def _f(rule_id: str, vendor: str, message: str) -> Finding:
    name, sev, reg = RULES[rule_id]
    return Finding(rule_id, name, sev, vendor, message, reg)


def check(register: dict, stale_days: int = 365, max_critical: int = 3,
          contact_days: int = 180, today: date | None = None) -> list[Finding]:
    today = today or date.today()
    procs = register["processes"]
    out: list[Finding] = []
    for v in register["vendors"]:
        if v["criticality"] not in ("critical", "high"):
            continue
        vid = v["id"]
        if v["notification_sla_hours"] is None:
            out.append(_f("RL001", vid, "no incident notification SLA recorded"))
        if v["recovery_time_hours"] is None:
            out.append(_f("RL002", vid, "no recovery time commitment recorded"))
        if not v["contacts"]:
            out.append(_f("RL003", vid, "no email or phone contact recorded"))
        if not v["exit_plan"]:
            out.append(_f("RL004", vid, "no documented exit plan"))
        lt = v["last_tested"]
        if lt is None:
            out.append(_f("RL005", vid, "no resilience test date recorded"))
        elif (today - lt).days > stale_days:
            out.append(_f("RL005", vid,
                          f"last resilience test {lt.isoformat()} is older than {stale_days} days"))
        cv = v["contacts_verified"]
        if v["contacts"] and cv is None:
            out.append(_f("RL008", vid, "no contact verification date recorded"))
        elif v["contacts"] and (today - cv).days > contact_days:
            out.append(_f("RL008", vid, f"contacts last verified {cv.isoformat()}, "
                                        f"older than {contact_days} days"))
        rt = v["recovery_time_hours"]
        crit_count = 0
        for pid in v["supports_processes"]:
            p = procs.get(pid)
            if p is None:
                continue
            if p["criticality"] == "critical":
                crit_count += 1
            if rt is not None and p["rto_hours"] is not None and rt > p["rto_hours"]:
                out.append(_f("RL006", vid,
                              f"recovery time {rt:g}h exceeds {pid} RTO {p['rto_hours']:g}h"))
        if crit_count > max_critical:
            out.append(_f("RL007", vid,
                          f"supports {crit_count} critical processes (threshold {max_critical})"))
    return out


def at_or_above(findings: list[Finding], level: str) -> list[Finding]:
    floor = SEVERITIES.index(level)
    return [f for f in findings if SEVERITIES.index(f.severity) >= floor]
