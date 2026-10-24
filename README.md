<div align="center">

# resilint

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Release: v0.1.0](https://img.shields.io/badge/release-v0.1.0-blue.svg)](https://github.com/chriswayneh/resilint/releases/tag/v0.1.0)

### Vendor resilience checks that run every time your vendor list changes.

An open-source command-line tool and GitHub Action that reads your critical-vendor register from a YAML file in Git and flags missing or inconsistent resilience commitments, mapped to DORA, NIS2, and the UK PRA's SS2/21.

**Status:** v0.1.0 released; v0.2 (SARIF, contact verification, versioned schema) on `main` after review. See the [roadmap](ROADMAP.md).

</div>

> **A note on this repo:** This GitHub account is my personal playground, where I experiment, learn, and build security tools in the open. Projects here are personal work, not a product or company offering.

---

## The problem, in business terms

- **A signed contract is the starting point, not proof of resilience.** Notification windows, recovery times, and exit plans are only useful if they exist, are current, and match what the business actually needs.
- **Annual questionnaires go stale.** A vendor's answers are a snapshot. Contacts change, services move, and new business processes start depending on a supplier between review cycles.
- **One vendor outage can cascade.** When several critical processes rely on the same supplier, a single failure becomes a business-wide incident. That concentration is often invisible until it happens.

Regulators now expect firms to show this is managed continuously, not once a year.

## What resilint does

Your team keeps critical vendors and the business processes that depend on them in a plain YAML file under version control, or exports a CSV from the spreadsheet they already keep. On every change (pull request, commit, or scheduled run), resilint checks it and reports:

**Missing commitments** for any vendor marked critical or high:
- No incident notification time (SLA)
- No recovery time commitment
- No email or phone contact
- No documented exit plan
- No resilience test or exercise within the required window

**Consistency problems:**
- A vendor's promised recovery time is slower than the recovery target of a business process that depends on it
- Too many critical processes concentrated on a single vendor (threshold you set)
- Vendor contacts that have never been verified, or not within a window you set (default 180 days)

It is read-only, runs offline, and works only on your own data. It does not contact vendors, scrape websites, or send anything anywhere.

## Evidence it produces (text, JSON, Markdown, SARIF)

| Audience | What they get |
|---|---|
| Board and risk committee | A short Markdown summary: how many critical vendors, how many have gaps, and where concentration risk sits |
| Internal and external auditors | Timestamped JSON findings tied to a Git commit, so every result is reproducible from history |
| Regulators | Each finding tagged with a draft article mapping, plus (planned) export toward the DORA register-of-information templates |
| Engineering and procurement | Pull request annotations (SARIF) showing exactly which entry needs fixing |

Exit codes make it CI-friendly: `0` clean, `1` findings at or above your chosen severity, `2` bad input.

## Quick start

```bash
pip install git+https://github.com/chriswayneh/resilint
resilint check examples/vendors.yaml               # text
resilint check examples/vendors.csv --format md    # one-page gap report for leadership
resilint check examples/vendors.yaml --format json --fail-on medium --stale-days 180
```

Options: `--format text|json|md|sarif`, `--output FILE` (write the report to a file), `--fail-on low|medium|high|critical` (default `high`), `--stale-days N` (default 365), `--max-critical N` (concentration threshold, default 3), `--contact-days N` (max age of `contacts_verified`, default 180).
Exit codes: `0` no findings at or above `--fail-on`, `1` findings at or above it, `2` bad input.

Example Markdown report (from the fictional `examples/` data):

```markdown
# Vendor resilience gap report

- Vendors in register: **2**
- Critical/high vendors checked: **2**
- Vendors with gaps: **1**
- Findings: **2** high, **2** medium

| Severity | Vendor | Gap | Rule | Maps to |
|---|---|---|---|---|
| high | example-cloud-wms | no documented exit plan | RL004 | DORA Art. 28(8), Art. 30(3)(f); ... |
| high | example-cloud-wms | recovery time 8h exceeds order-fulfilment RTO 4h | RL006 | DORA Art. 30(2)(e), 30(3)(a); ... |
| medium | example-cloud-wms | contacts last verified 2025-01-15, older than 180 days | RL008 | ... |
| medium | example-cloud-wms | last resilience test 2024-11-12 is older than 365 days | RL005 | ... |
```

### GitHub Action

```yaml
- uses: actions/checkout@v4
- uses: chriswayneh/resilint@main   # pin to a release tag once one exists
  with:
    file: vendors.yaml
    fail-on: high
```

To get pull request annotations, write SARIF and upload it to code scanning (pin actions to full commit SHAs in your own workflow):

```yaml
permissions:
  contents: read
  security-events: write
steps:
  - uses: actions/checkout@v4
  - uses: chriswayneh/resilint@main
    continue-on-error: true      # still upload when findings fail the step
    with:
      file: vendors.yaml
      format: sarif
      output: resilint.sarif
  - uses: github/codeql-action/upload-sarif@v3
    with:
      sarif_file: resilint.sarif
```

Each SARIF result points at the line of the vendor's `id` in your register, so the annotation lands on the entry that needs fixing.

## Input schema

YAML anchors and aliases (`&name` / `*name`) are refused (exit 2) to block alias-expansion attacks.

YAML (`examples/vendors.yaml`):

```yaml
schema_version: 1               # optional; defaults to 1, unknown versions exit 2
processes:
  - id: order-fulfilment        # required
    name: Order fulfilment
    criticality: critical       # critical|high|medium|low (default critical)
    rto_hours: 4                # recovery time objective
vendors:
  - id: example-cloud-wms       # required, unique
    name: Example Cloud WMS Ltd
    criticality: critical       # required: critical|high|medium|low
    notification_sla_hours: 24
    recovery_time_hours: 8
    contacts:                   # at least one email or phone
      - email: incidents@example.com
      - phone: "+1-555-0100"
    exit_plan: docs/exit/wms.md # true/false or a document reference
    last_tested: 2024-11-12     # ISO date
    contacts_verified: 2025-01-15  # ISO date the contacts were last confirmed working
    supports_processes: [order-fulfilment]
```

CSV (`examples/vendors.csv`), one row per record, header row required:

| Column | Notes |
|---|---|
| `record_type` | `vendor` (default) or `process` |
| `id`, `name`, `criticality` | as in YAML |
| `notification_sla_hours`, `recovery_time_hours`, `exit_plan`, `last_tested`, `contacts_verified` | vendor rows |
| `contacts`, `supports_processes` | vendor rows; multiple values separated by `;` |
| `rto_hours` | process rows |

Only vendors marked `critical` or `high` are checked. Files are read with safe YAML loading, limited to 5 MB, and never sent anywhere.

## Rules

| ID | Severity | Finding |
|---|---|---|
| RL001 | high | No notification SLA |
| RL002 | high | No recovery time |
| RL003 | high | No email or phone contact |
| RL004 | high | No exit plan |
| RL005 | medium | Last test missing or older than `--stale-days` |
| RL006 | high | Vendor recovery time exceeds the RTO of a process it supports |
| RL007 | medium | Vendor supports more than `--max-critical` critical processes |
| RL008 | medium | Contacts present but `contacts_verified` missing or older than `--contact-days` |

## Regulatory mapping (draft)

Each finding carries a `regulation` field and the label "draft mapping, not legal advice".

| Rule | DORA (EU 2022/2554) | NIS2 (EU 2022/2555) | UK PRA SS2/21 |
|---|---|---|---|
| RL001 notification SLA | Art. 30(3)(b) notice periods and reporting obligations; Art. 30(2)(f) incident assistance | Art. 21(2)(d) supply chain security | Ch. 6 outsourcing agreements |
| RL002 recovery time | Art. 30(2)(e), 30(3)(a) service level descriptions | Art. 21(2)(c) business continuity | Ch. 6 outsourcing agreements |
| RL003 contact | Art. 30(2) contract terms | Art. 21(2)(d) | Ch. 6 outsourcing agreements |
| RL004 exit plan | Art. 28(8) exit strategies; Art. 30(3)(f) | Art. 21(2)(d) | Ch. 10 business continuity and exit plans |
| RL005 recent test | Art. 30(3)(c) contingency plan testing, 30(3)(d) TLPT participation | Art. 21(2)(f) effectiveness assessment | Ch. 10 business continuity and exit plans |
| RL006 recovery vs. RTO | Art. 30(2)(e), 30(3)(a) | Art. 21(2)(c) | Ch. 10 business continuity and exit plans |
| RL007 concentration | Art. 28(4)(c), Art. 29 concentration risk | Art. 21(2)(d) | Ch. 5 pre-outsourcing (materiality and risk assessment) |
| RL008 contact verification | Art. 30(2) contract terms; Art. 28(3) register of information kept up to date | Art. 21(2)(d) | Ch. 6 outsourcing agreements |

DORA Art. 30(3) applies to contracts supporting critical or important functions.

Sources: [DORA, Regulation (EU) 2022/2554](https://eur-lex.europa.eu/eli/reg/2022/2554/oj) · [NIS2, Directive (EU) 2022/2555](https://eur-lex.europa.eu/eli/dir/2022/2555/oj) · [Bank of England PRA SS2/21, Outsourcing and third party risk management](https://www.bankofengland.co.uk/prudential-regulation/publication/2021/march/outsourcing-and-third-party-risk-management-ss).

This mapping is a working aid, not legal advice. Confirm interpretations with your compliance and legal teams.

## How it fits into a GRC program

resilint **complements, and does not replace,** third-party risk management (TPRM) and GRC platforms.

- **TPRM platforms** run questionnaires, due diligence, and vendor scoring. resilint checks that the commitments you already hold are recorded, current, and consistent.
- **Tabletop exercise tools** run scenarios but do not model contract commitments. resilint records whether a test happened and (planned, v0.4) attaches the result to each vendor.
- **DORA register-of-information validators** check that a file has the right format. resilint checks whether the underlying commitments actually exist and make sense together.

Because the register lives in Git, every change has an author, a review, and a history auditors can follow.

## Status

**v0.1.0 released** (2026-10-24); v0.2 in review. See the [roadmap](ROADMAP.md) and [changelog](CHANGELOG.md).

## Security

See [SECURITY.md](SECURITY.md).

## Built with

- Python 3.10+ (standard library + PyYAML)
- AI-assisted development with Grok Bot, Cursor, Codex, and Claude

## License

[MIT](LICENSE)
