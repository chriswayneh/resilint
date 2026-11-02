# Roadmap

Status: **[v0.4.0 released](https://github.com/chriswayneh/resilint/releases/tag/v0.4.0) (2026-10-24).** Milestones and scope may change.

## v0.1 - Core checks (released 2026-10-24)
- YAML schema for vendors and business processes, plus CSV import from spreadsheet exports
- Missing-field rules for critical/high vendors: notification SLA, recovery time, contact, exit plan, recent resilience test
- Consistency rules: vendor recovery time vs. dependent process RTO; concentration of critical processes on one vendor
- Draft regulation reference on every finding (DORA, NIS2, UK PRA SS2/21)
- Text, JSON, and Markdown output; exit codes `0`/`1`/`2`
- Minimal composite GitHub Action

## v0.2 - CI polish (released 2026-10-24)
- SARIF 2.1.0 output (`--format sarif`, `--output FILE`) for pull request annotations via code scanning
- `contacts_verified` dates with rule RL008 and `--contact-days`; versioned schema (`schema_version: 1`, unknown versions rejected)

## v0.3 - Regulatory reporting (released 2026-10-24)
- Regulation mapping report (`--format regmap`) and structured `regulation_refs` per finding (DORA, NIS2, UK PRA SS2/21)
- `export-roi`: draft CSV export toward DORA register-of-information templates (B_05.01, B_06.01, B_02.02), to be completed and checked with an existing RoI validator; optional `lei` and `country` vendor fields

## v0.4 - Drill records (released 2026-10-24)
- `drill record` command to attach tabletop or test results to a vendor and update its last-tested date
- `check --drills LOG` applies the log; rule RL009 flags a vendor whose most recent drill failed

## v0.4.1 - Cross-platform reliability (in development)
- Serialize concurrent `drill record` writes on Windows as well as Linux/macOS
- Return a clean input error when the operating system cannot acquire a drill-log lock
- Run lint, type checks, and the full test suite on Linux and Windows with Python 3.10 and 3.12
- Verify lock contention, release after success or invalid input, and preservation of concurrent records

## Non-goals
- No vendor questionnaires
- No scraping or contacting vendors
- No hosted SaaS; it runs locally and offline on your own data
