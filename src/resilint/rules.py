"""Resilience rules. Regulation references are a draft mapping, not legal advice."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date

SEVERITIES = ("low", "medium", "high", "critical")
REG_NOTE = "draft mapping, not legal advice"
DISCLAIMER = "Draft, not legal advice"

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
    "RL009": ("last-drill-failed", "medium",
              "DORA Art. 30(3)(c), Art. 11(6); NIS2 Art. 21(2)(c), 21(2)(f); PRA SS2/21 ch. 10"),
}


FRAMEWORKS = ("DORA", "NIS2", "PRA SS2/21")

# Examples illustrate recorded evidence; they do not establish commitments.
GUIDANCE = {
    "RL001": (("A critical/high vendor has no incident-notification commitment recorded. "
              "Record the hours agreed in the contract."), "notification_sla_hours: 24"),
    "RL002": (("A critical/high vendor has no recovery-time commitment recorded. "
              "Record the agreed recovery time in hours."), "recovery_time_hours: 4"),
    "RL003": (("A critical/high vendor has no email or phone contact. "
              "Record a verified incident contact."), "contacts:\n  - email: incidents@example.test"),
    "RL004": (("A critical/high vendor has no documented exit plan. "
              "Create or locate the plan and record its reference."),
              "exit_plan: docs/exit/example-vendor.md"),
    "RL005": (("A critical/high vendor has no test date, or its test is older than stale_days. "
              "Complete a resilience test and record its actual date; replace YYYY-MM-DD below."),
              "last_tested: YYYY-MM-DD"),
    "RL006": (("A critical/high vendor's recovery time exceeds a supported process's RTO. "
              "Resolve the mismatch and record the agreed commitment; the example assumes a 4h RTO."),
              "recovery_time_hours: 4"),
    "RL007": (("A critical/high vendor supports more critical processes than max_critical. "
              "Review concentration and recovery options, keeping all actual dependencies recorded. "
              "Update this list only after a real dependency change."),
              "supports_processes: [example-process]"),
    "RL008": (("A critical/high vendor's contacts lack verification or are older than contact_days. "
              "Verify the contacts and record the actual date; replace YYYY-MM-DD below."),
              "contacts_verified: YYYY-MM-DD"),
    "RL009": (("The latest applied drill for a critical/high vendor failed. "
              "Address the failure, rerun the drill, then record the actual result and date. "
              "The example is for a completed successful retest; replace the vendor and date."),
              ("resilint drill record vendors.yaml --vendor example-vendor --kind test "
              "--result pass --date YYYY-MM-DD")),
}


def explain(rule_id: str) -> str:
    name, severity, regulation = RULES[rule_id]
    description, example = GUIDANCE[rule_id]
    return (f"{rule_id}: {name}\nSeverity: {severity}\n\n{description}\n\n"
            f"Illustrative fix (use your actual evidence):\n{example}\n\n"
            f"References ({REG_NOTE}):\n{regulation}")

FINDING_FIELDS = {
    "RL001": "notification_sla_hours", "RL002": "recovery_time_hours", "RL003": "contacts",
    "RL004": "exit_plan", "RL005": "last_tested", "RL006": "supports_processes",
    "RL007": "supports_processes", "RL008": "contacts_verified", "RL009": "drills",
}


def refs(regulation: str) -> dict[str, list[str]]:
    """Split a rule's reference string into {framework: [references]}."""
    out: dict[str, list[str]] = {fw: [] for fw in FRAMEWORKS}
    for part in regulation.split(";"):
        part = part.strip()
        for fw in FRAMEWORKS:
            if part.startswith(fw + " "):
                for x in part[len(fw) + 1:].split(", "):
                    x = x.strip()
                    if x:
                        out[fw].append("Art. " + x if x[0].isdigit() else x)
    return out


@dataclass
class Finding:
    rule_id: str
    rule: str
    severity: str
    vendor: str
    message: str
    regulation: str
    regulation_note: str = REG_NOTE
    regulation_refs: dict = field(default_factory=dict)
    field: str = ""

    def __post_init__(self):
        if not self.regulation_refs:
            self.regulation_refs = refs(self.regulation)

    def to_dict(self) -> dict:
        return asdict(self)


def _f(rule_id: str, vendor: str, message: str, field: str = "") -> Finding:
    name, sev, reg = RULES[rule_id]
    return Finding(rule_id, name, sev, vendor, message, reg,
                   field=field or FINDING_FIELDS[rule_id])


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
        drills = v.get("drills") or []
        if drills and drills[-1]["result"] == "fail":
            d = drills[-1]
            out.append(_f("RL009", vid,
                          f"most recent {d['kind']} on {d['date'].isoformat()} failed"))
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
                              f"recovery time {rt:g}h exceeds {pid} RTO {p['rto_hours']:g}h",
                              field=f"supports_processes:{pid}"))
        if crit_count > max_critical:
            out.append(_f("RL007", vid,
                          f"supports {crit_count} critical processes (threshold {max_critical})"))
    return out


def at_or_above(findings: list[Finding], level: str) -> list[Finding]:
    floor = SEVERITIES.index(level)
    return [f for f in findings if SEVERITIES.index(f.severity) >= floor]
