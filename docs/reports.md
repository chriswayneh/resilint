# Report contract v1

The local [`schema/report.v1.json`](../schema/report.v1.json) describes JSON check output using JSON Schema Draft 2020-12. It has only local fragment references; validating a loaded copy needs no network access. The schema is distributed in this repository, not promised as an installed package resource.

| Root field | Type / meaning |
| --- | --- |
| `tool` | Constant `resilint` |
| `version` | Package version string |
| `findings` | Array of findings after config/baseline filtering |

Each finding contains string fields `rule_id`, `rule` (the rule name), `severity`, `vendor`, `message`, `regulation`, `regulation_note` and `field`. `severity` is `low`, `medium`, `high` or `critical`. `regulation_refs` maps framework names to arrays of reference strings. The existing `regulation_note` value is `draft mapping, not legal advice`. `field` identifies the affected field and is part of [baseline identity](baseline.md); RL006 includes the process ID.

Findings are sorted by descending severity, vendor ID and rule ID. Same-key findings preserve rule emission order. The failure threshold does not remove lower-severity findings. Empty reports contain `findings: []`. Clients must tolerate additional root/finding fields, consistent with the [stability policy](stability.md).

## SARIF

SARIF output uses version 2.1.0. Results include `ruleId`, level, message, physical location and `properties.severity`/`properties.vendor`. Locations use the register source URI and the known vendor line, defaulting to line 1 when unavailable. `partialFingerprints['resilint/v1']` retains the existing `rule_id:vendor` representation; it is separate from the rule/vendor/field SHA-256 baseline identity. The driver lists every known rule and its draft references.

## Snapshot checks

Five checked-in snapshots cover `text`, `md`, `json`, `sarif` and `regmap`, including all nine rule IDs, two RL006 process findings and a vendor ID requiring Markdown escaping. Evaluation date is fixed to 2026-11-02, report tool version to `0.0.0`, and source URI to `fixtures/report-register.yaml`. Those normalizations keep unrelated dates, release bumps and platform paths from changing the snapshots.

Run `pytest -q tests/test_report_contract.py`. Review intentional output changes before updating [`tests/fixtures/reports/`](../tests/fixtures/reports). Snapshot matching is regression evidence, not a promise that human-readable prose can never change. Markdown/regulation reports and RoI notes display “Draft, not legal advice”.
