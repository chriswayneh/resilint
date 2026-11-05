# resilint reference

Detailed reference for published [v1.0.0](https://github.com/chriswayneh/resilint/releases/tag/v1.0.0), including Action outputs, `init`, `explain`, pre-commit, rule configuration and baselines. See the [stability policy](stability.md) for compatibility commitments and limits.

- [Regulation mapping report and draft RoI export](#regulation-mapping-report-and-draft-roi-export)
- [Drill records](#drill-records)
- [GitHub Action](#github-action)
- [Starter register](#starter-register)
- [pre-commit](#pre-commit)
- [Input schema](#input-schema)
- [Rules](#rules)
- [Regulatory mapping (draft)](#regulatory-mapping-draft)
- [How it fits into a GRC program](#how-it-fits-into-a-grc-program)
- [Roadmap](#roadmap)

## Regulation mapping report and draft RoI export

```bash
resilint check examples/vendors.yaml --format regmap        # findings grouped by DORA / NIS2 / PRA reference
mkdir roi && resilint export-roi examples/vendors.yaml --out-dir roi
```

`--format regmap` lists every DORA, NIS2, and PRA SS2/21 reference the rules map to, with the rules, finding count, and affected vendors for each. JSON findings also carry a structured `regulation_refs` field. All references are a draft mapping, not legal advice.

`export-roi` writes three partial CSV tables and a README for working toward a register-of-information export. They are draft mapping, not legal advice, and require completion and validation before submission. The [export guide](roi.md) covers table contents, formula neutralization, output guards and `--force`.

## Drill records

```bash
resilint check examples/vendors.yaml --drills examples/drills.yaml   # sample log: RL009 shows
resilint drill record examples/vendors.yaml --vendor example-cloud-wms \
  --kind tabletop --result pass --date 2026-10-20 --notes "failover in 3h" --log /tmp/drills.yaml
```

`drill record` stores tabletop/test evidence in a separate log while preserving the register. `check --drills LOG` applies recorded outcomes and can report a failed latest drill. The [drill guide](drills.md) covers every flag, date handling, locking and recovery behavior. The Action accepts an optional `drills` input.

## GitHub Action

For controlled Action adoption, use a full reviewed commit SHA and update deliberately after reviewing release notes. The `@v1` alias and immutable `@v1.0.0` reference are available at stable commit `d5aa0b6223ed930adc753fe94aa212a9ba686c43`. See the [Action tag policy](stability.md#action-version-tags) for update behavior and pinning limits.

The `format` input accepts `text`, `json`, `md`, `sarif`, or `regmap`; `fail-on` accepts `low`, `medium`, `high`, or `critical`. These inputs are passed to the CLI for validation. Unknown values exit with code 2 and fail the Action before any report is written.

The Action exposes three string outputs from the same check that creates the report:

| Output | Value |
| --- | --- |
| `findings` | Total reported findings after configuration ignores, including severities below `fail-on` |
| `highest-severity` | `low`, `medium`, `high`, `critical`, or `none` when there are no findings |
| `exit-code` | `0` for a passing threshold, `1` for findings reaching it, `2` for an input or output error |

Give the Action an `id: resilience` and read `${{ steps.resilience.outputs.findings }}`, `${{ steps.resilience.outputs.highest-severity }}` or `${{ steps.resilience.outputs.exit-code }}` in later steps. Set `continue-on-error: true` on the calling step when later steps must run after findings or invalid input. Counts and severity are empty on check errors; installation/runner failures may leave every output unset. Outputs do not change the Action's failing exit status. See the [GitHub composite-output reference](https://docs.github.com/en/actions/reference/workflows-and-actions/metadata-syntax#outputs-for-composite-actions) for output wiring.

The composite Action uses Node 24 and requires Actions Runner v2.327.1 or later. Update self-hosted runners before using it; GitHub-hosted runners are supported.

```yaml
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
- uses: chriswayneh/resilint@d5aa0b6223ed930adc753fe94aa212a9ba686c43 # v1.0.0
  with:
    file: vendors.yaml
    fail-on: high
```

For code-scanning annotations, copy the [complete SARIF workflow](../examples/workflows/resilint-sarif.yml) into `.github/workflows/resilint.yml` and set the register path. It pins every Action to a full commit SHA, grants `security-events: write` only to the upload job, uploads reports after threshold findings, then restores the check's failing status. Invalid input skips upload and fails the final gate. The example pins the reviewed v1.0.0 release SHA.

Uploading sends the report's vendor identifiers, finding messages and source locations to GitHub Code Scanning. Use it only for registers suitable for your repository's access policy. resilint itself still runs offline. Code-scanning availability and repository requirements are described in [GitHub's SARIF upload guide](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/integrate-with-existing-tools/upload-sarif-file).

Each SARIF result points at the line of the vendor's `id` in your register, so the annotation lands on the entry that needs fixing. The file path is relative to the working directory (with `uriBaseId: %SRCROOT%`); when the register is outside the working directory, the SARIF uri is just the file name.

For GitLab, Azure Pipelines or another runner, see the [CI recipes](ci.md).

## Starter register

`init` and `explain` are included in v1.0.0.

Use `resilint explain RL004` for a rule's description, illustrative fix and draft regulation references. All RL001–RL009 IDs are supported without a register or configuration file. Unknown IDs return 2. Examples must be replaced with actual evidence.

The CLI can create a commented fictional starter with `resilint init` (default `vendors.yaml`) or `resilint init path/to/vendors.yaml`. The destination's parent directory must exist. It refuses to overwrite any existing file or symlink and respects `RESILINT_OUTPUT_ROOT`. Replace the example commitments before using it for real checks.

Running `resilint check vendors.yaml` on the untouched starter intentionally reports RL004 (missing exit plan), RL005 (no resilience test date) and RL008 (unverified contacts), returning 1. Creation itself returns 0; a refused or failed write returns 2.

## pre-commit

The `resilint` hook is included in v1.0.0.

The hook `resilint` checks every selected register without changing it. It defaults to files named `vendors.yaml`, `vendors.yml` or `vendors.csv`; override `files` in your hook configuration for other names. Thresholds and ignores come from the repository's `.resilint.yaml`. Hook arguments are filenames; configure thresholds in that file instead of adding CLI flags to `args`.

From a resilint checkout, try the hook without installing a Git hook:

```bash
pip install pre-commit
pre-commit try-repo . resilint --files examples/vendors.yaml
```

The fictional example intentionally has high findings, so this command runs successfully as a check and reports a failing hook. Clean registers pass; malformed registers fail. Multiple files are all checked, with errors taking precedence over threshold findings. pre-commit installs a Python environment on first use; subsequent checks run offline. See [pre-commit configuration](https://pre-commit.com/#pre-commit-configyaml---repos) to add this repository at a reviewed commit containing `.pre-commit-hooks.yaml`; the reviewed v1.0.0 commit is `d5aa0b6223ed930adc753fe94aa212a9ba686c43`.

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
    lei: 9845000EXAMPLE000048   # optional ISO 17442 LEI (checksum validated), used by export-roi
    country: IE                 # optional assigned ISO 3166-1 alpha-2 code (GB, GR; not UK, EL), used by export-roi
    supports_processes: [order-fulfilment]
```

CSV (`examples/vendors.csv`), one row per record, header row required. UTF-8 BOM and CRLF line endings are supported; header names are trimmed and case-insensitive. Headers must be nonempty and unique, and each data row must match the header's field count. Invalid rows return exit 2 with a physical CSV line number (the ending line for multiline quoted records).

Comma is the default separator. For semicolon-delimited spreadsheet exports, use `resilint check register.csv --csv-delimiter ';'`. The same option works with `export-roi` and `drill record`; YAML input ignores it. Semicolons still separate list values such as contacts and supported processes, so quote those cells when semicolon is also the field separator. Quoted separators and embedded newlines follow CSV quoting rules.

| Column | Notes |
|---|---|
| `record_type` | `vendor` (default) or `process` |
| `id`, `name`, `criticality` | as in YAML |
| `notification_sla_hours`, `recovery_time_hours`, `exit_plan`, `last_tested`, `contacts_verified`, `lei`, `country` | vendor rows |
| `contacts`, `supports_processes` | vendor rows; multiple values separated by `;` |
| `rto_hours` | process rows |

Only vendors marked `critical` or `high` are checked. Files are read with safe YAML loading, limited to 5 MiB (5,242,880 bytes), and never sent anywhere. YAML and CSV registers above that size are rejected before parsing with exit 2 and a `file larger than 5 MB` diagnostic.

CI checks a fictional CSV register with 10,000 critical vendors linked to 2,000 critical processes in under 5 seconds. The timed interval includes file loading, normalization, rule checks and JSON reporting of 10,000 recovery-time findings; fixture creation, Python startup and verification are excluded. This is a regression budget for that workload, not a timing guarantee for every register or machine. Run `pytest -q tests/test_perf.py --durations=3` to check it locally.

## Rules

To adopt checks gradually, use `--write-baseline FILE` to snapshot existing finding identities and `--baseline FILE` to report only new findings. Successful snapshot creation returns 0 even when findings exist. See [baseline behavior and refresh guidance](baseline.md).

Per-project thresholds and expiring suppressions can be stored in `.resilint.yaml`; explicit CLI flags take precedence. See the [rule configuration guide](config.md).

CLI failures use `resilint: error: <file>:<line>: <message>` on stderr with exit 2. A known physical input line is one-based; `0` means no reliable line is available, and `<cli>` identifies argument errors. Output errors name the destination, and drill-log errors name the log. Control characters are escaped to keep each diagnostic on one line. Exit 0 means success without findings at the selected threshold; exit 1 means findings reached that threshold. Argument parsing may also print usage.

For editor and CI validation, use the [register v1 JSON Schema](../schema/register.v1.json) and [field reference and validation guide](schema.md). The schema complements runtime validation and resilience checks.

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
| RL009 | medium | Most recent drill in the `--drills` log failed |

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
| RL009 failed drill | Art. 30(3)(c) contingency plan testing; Art. 11(6) testing of ICT business continuity plans | Art. 21(2)(c) business continuity, 21(2)(f) effectiveness assessment | Ch. 10 business continuity and exit plans |

DORA Art. 30(3) applies to contracts supporting critical or important functions.

Sources: [DORA, Regulation (EU) 2022/2554](https://eur-lex.europa.eu/eli/reg/2022/2554/oj) · [NIS2, Directive (EU) 2022/2555](https://eur-lex.europa.eu/eli/dir/2022/2555/oj) · [Bank of England PRA SS2/21, Outsourcing and third party risk management](https://www.bankofengland.co.uk/prudential-regulation/publication/2021/march/outsourcing-and-third-party-risk-management-ss).

This mapping is a working aid, not legal advice. Confirm interpretations with your compliance and legal teams.

## How it fits into a GRC program

resilint **complements, and does not replace,** third-party risk management (TPRM) and GRC platforms.

- **TPRM platforms** run questionnaires, due diligence, and vendor scoring. resilint checks that the commitments you already hold are recorded, current, and consistent.
- **Tabletop exercise tools** run scenarios but do not model contract commitments. resilint records whether a test happened and, with `drill record`, attaches each tabletop or test result to the vendor.
- **DORA register-of-information validators** check that a file has the right format. resilint checks whether the underlying commitments actually exist and make sense together.

Because the register lives in Git, every change has an author, a review, and a history auditors can follow.

## Roadmap

**[v1.0.0 released](https://github.com/chriswayneh/resilint/releases/tag/v1.0.0)** (2026-11-04 Chicago). See the [changelog](../CHANGELOG.md) for release notes.

| Version | Theme | Highlights |
| --- | --- | --- |
| **v0.1–v0.4** | Core checks and evidence ✅ | YAML/CSV registers, resilience rules, SARIF, regulation mapping, draft RoI export and drill records |
| **v0.4.1** | Maintenance | Windows locking ✅ · dependency updates ✅ · version/docs checks ✅ · Action input checks ✅ |
| **v0.5** | Real-world data | Test organization, coverage, fuzzing, performance, CSV robustness and register schema ✅ · Rule configuration, baselines and platform parity complete |
| **v0.6** | CI integration | Action outputs and self-tests, SARIF examples, pre-commit, `init` and `explain` |
| **v0.9** | Documentation and API freeze | Usage guides, output schemas, snapshots and a stability policy |
| **Before v1.0** | Packaging and release automation | Wheels, PyPI publishing, provenance, SBOM and security scanning |
| **v1.0** | Stable release | Release candidate, synthetic dogfooding, fresh-install tests and final reviews |

All milestone work above is included in v1.0.0; the intermediate labels were not separate releases. v2/v3 are deferred.

The [full roadmap](../ROADMAP.md) has milestone summaries. Detailed tasks and acceptance criteria are in [`roadmap/`](../roadmap/README.md).
