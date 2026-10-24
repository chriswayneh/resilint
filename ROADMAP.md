# Roadmap

Status: **Planned - design stage, no release yet.** Milestones and scope may change.

## v0.1 - Core checks
- Versioned YAML schema for vendors and business processes
- Missing-field rules for critical vendors: notification SLA, recovery time, reachable contact, exit plan, recent resilience test date
- Exit codes: `0` clean, `1` findings at or above `--fail-on`, `2` bad input
- JSON and Markdown evidence output

## v0.2 - Consistency and CI
- Consistency rules: vendor recovery time vs. dependent process recovery target; concentration of critical processes on one vendor
- GitHub Action wrapper
- SARIF output for pull request annotations

## v0.3 - Regulatory reporting
- Regulation mapping report (DORA, NIS2, UK PRA SS2/21) per finding
- Export toward DORA register-of-information templates, checkable with an existing RoI validator such as dora-roi-validator

## v0.4 - Drill records
- `drill record` command to attach tabletop or test results to a vendor and update its last-tested date

## Non-goals
- No vendor questionnaires
- No scraping or contacting vendors
- No hosted SaaS; it runs locally and offline on your own data
