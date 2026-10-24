<div align="center">

# resilint

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status: planned](https://img.shields.io/badge/status-planned-lightgrey.svg)](ROADMAP.md)

### Vendor resilience checks that run every time your vendor list changes.

A planned open-source command-line tool and GitHub Action that reads your critical-vendor register from a YAML file in Git and flags missing or inconsistent resilience commitments, mapped to DORA, NIS2, and the UK PRA's SS2/21.

**Status:** Planned - design stage, no release yet. Nothing below is installable today. See the [roadmap](ROADMAP.md).

</div>

> **A note on this repo:** This GitHub account is my personal playground, where I experiment, learn, and build security tools in the open. Projects here are personal work, not a product or company offering.

---

## The problem, in business terms

- **A signed contract is the starting point, not proof of resilience.** Notification windows, recovery times, and exit plans are only useful if they exist, are current, and match what the business actually needs.
- **Annual questionnaires go stale.** A vendor's answers are a snapshot. Contacts change, services move, and new business processes start depending on a supplier between review cycles.
- **One vendor outage can cascade.** When several critical processes rely on the same supplier, a single failure becomes a business-wide incident. That concentration is often invisible until it happens.

Regulators now expect firms to show this is managed continuously, not once a year.

## What resilint will do

Your team keeps critical vendors and the business processes that depend on them in a plain YAML file under version control. On every change (pull request, commit, or scheduled run), resilint checks it and reports:

**Missing commitments** for any vendor marked critical:
- No incident notification time (SLA)
- No recovery time commitment
- No reachable contact, or a contact not verified recently
- No documented exit plan
- No resilience test or exercise within the required window

**Consistency problems:**
- A vendor's promised recovery time is slower than the recovery target of a business process that depends on it
- Too many critical processes concentrated on a single vendor (threshold you set)

It is read-only, runs offline, and works only on your own data. It does not contact vendors, scrape websites, or send anything anywhere.

## Evidence it will produce

| Audience | What they get |
|---|---|
| Board and risk committee | A short Markdown summary: how many critical vendors, how many have gaps, and where concentration risk sits |
| Internal and external auditors | Timestamped JSON findings tied to a Git commit, so every result is reproducible from history |
| Regulators | Each finding mapped to the article it relates to, plus (planned) export toward the DORA register-of-information templates |
| Engineering and procurement | Pull request annotations (SARIF) showing exactly which entry needs fixing |

Exit codes make it CI-friendly: `0` clean, `1` findings at or above your chosen severity, `2` bad input.

## Example (planned, illustrative only)

`vendors.yml`:

```yaml
processes:
  - id: order-fulfilment
    criticality: critical
    recovery_time_objective: 4h
    vendors: [example-cloud-wms]

vendors:
  - id: example-cloud-wms
    name: Example Cloud WMS Ltd
    criticality: critical
    notification_sla: 24h
    recovery_time: 8h
    contacts:
      - role: incident
        email: incidents@example.com
        verified: 2026-03-01
    exit_plan: null
    last_resilience_test: 2024-11-12
```

Planned output:

```text
$ resilint check vendors.yml

HIGH  RTO-MISMATCH   example-cloud-wms  recovery_time 8h exceeds order-fulfilment RTO 4h
                     maps to: DORA Art. 28, Art. 30; PRA SS2/21
HIGH  NO-EXIT-PLAN   example-cloud-wms  critical vendor has no exit plan
                     maps to: DORA Art. 28(8); PRA SS2/21
MED   STALE-TEST     example-cloud-wms  last resilience test older than 12 months
                     maps to: DORA Art. 30; NIS2 Art. 21(2)(d)

3 findings (2 high, 1 medium). Exit code 1.
```

Rule IDs, article references, and output format are draft and may change before v0.1.

## Regulatory mapping (draft)

| Check | DORA (EU 2022/2554) | NIS2 (EU 2022/2555) | UK PRA SS2/21 |
|---|---|---|---|
| Critical vendor recorded with dependent processes | Art. 28(3) register of information | Art. 21(2)(d) supply chain security | Outsourcing register |
| Notification SLA present | Art. 30 contract terms | Art. 21(2)(d) | Contractual requirements |
| Recovery time present and consistent with process targets | Art. 30 service levels | Art. 21(2)(c) business continuity | Business continuity |
| Reachable, recently verified contact | Art. 30 | Art. 21(2)(d) | Contractual requirements |
| Exit plan documented | Art. 28(8) exit strategies | Art. 21(2)(d) | Exit planning |
| Recent resilience test | Art. 30 participation in testing | Art. 21(2)(f) effectiveness assessment | Business continuity testing |
| Concentration on one vendor | Art. 28, Art. 29 concentration risk | Art. 21(2)(d) | Concentration risk |

Sources: [DORA, Regulation (EU) 2022/2554](https://eur-lex.europa.eu/eli/reg/2022/2554/oj) · [NIS2, Directive (EU) 2022/2555](https://eur-lex.europa.eu/eli/dir/2022/2555/oj) · [Bank of England PRA SS2/21, Outsourcing and third party risk management](https://www.bankofengland.co.uk/prudential-regulation/publication/2021/march/outsourcing-and-third-party-risk-management-ss).

This mapping is a working aid, not legal advice. Confirm interpretations with your compliance and legal teams.

## How it fits into a GRC program

resilint **complements, and does not replace,** third-party risk management (TPRM) and GRC platforms.

- **TPRM platforms** run questionnaires, due diligence, and vendor scoring. resilint checks that the commitments you already hold are recorded, current, and consistent.
- **Tabletop exercise tools** run scenarios but do not model contract commitments. resilint records whether a test happened and (planned) attaches the result to each vendor.
- **DORA register-of-information validators** check that a file has the right format. resilint checks whether the underlying commitments actually exist and make sense together.

Because the register lives in Git, every change has an author, a review, and a history auditors can follow.

## Status

**Planned - design stage, no release yet.** There is no code, package, or Action published. See the [roadmap](ROADMAP.md).

## Security

See [SECURITY.md](SECURITY.md).

## Built with

- Python (planned implementation language)
- AI-assisted development with Grok Bot, Cursor, Codex, and Claude

## License

[MIT](LICENSE)
