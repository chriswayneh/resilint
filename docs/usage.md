# CLI usage

See [installation](install.md) for release/development availability. Run `resilint --version` for the package version. Global `-h`/`--help`, and `--help` after any subcommand, print usage and exit 0.

## Create a register and understand a finding

```bash
resilint init
resilint check vendors.yaml
resilint explain RL004
```

`init [FILE]` defaults to `vendors.yaml`, writes a commented fictional YAML starter, and refuses to overwrite existing files or symlinks. Parent directories must exist. The untouched starter intentionally has RL004, RL005 and RL008 findings; replace the example with actual commitments. `explain RULE` supports RL001–RL009 without reading a register or config and prints descriptions, fix examples and draft references. Unknown IDs exit 2. Neither command contacts vendors.

## Check a register

```bash
resilint check vendors.yaml --format json --output findings.json --fail-on high
```

| Argument or flag | Meaning / default |
| --- | --- |
| `FILE` | Required YAML or CSV register; see [schema](schema.md) |
| `--format` | `text` (default), `json`, `md`, `sarif` or `regmap` |
| `--output FILE` | Write the report; otherwise print to stdout |
| `--fail-on` | Lowest failing severity: `low`, `medium`, `high` (default), `critical` |
| `--stale-days N` | Maximum test age in days; default 365 |
| `--contact-days N` | Maximum contact-verification age in days; default 180 |
| `--max-critical N` | Allowed critical-process concentration; default 3 |
| `--config FILE` | Explicit [rule settings](config.md); otherwise optional cwd `.resilint.yaml` |
| `--baseline FILE` | Report only identities absent from a [baseline](baseline.md) |
| `--write-baseline FILE` | Save current config-filtered identities; mutually exclusive with `--baseline` |
| `--drills LOG` | Apply a separate [drill log](drills.md) before evaluating rules |
| `--csv-delimiter` | `,` (default) or `;`; ignored for YAML |

Threshold numbers must be nonnegative integers. Config settings apply first and explicit CLI flags override them. All findings remain in the report regardless of the failure threshold; active ignores and baseline identities are filtered out. Successful baseline creation returns 0 even when findings exist.

## Exit codes and diagnostics

| Code | Meaning |
| --- | --- |
| 0 | Successful command; for ordinary checks, no reported finding reaches the threshold |
| 1 | Check findings reach the configured threshold; a completed report is still available |
| 2 | Invalid input/arguments, failed output, or another controlled command error |

Exit-2 diagnostics use `resilint: error: FILE:LINE: MESSAGE` on stderr. `0` means no source line is known and `<cli>` means an argument-level error. Argument errors can also print usage. YAML parser lines and CSV physical row-end lines are included when available. Embedded controls are escaped.

## Files and report formats

Registers are read without mutation. Input files are capped at 5 MiB; YAML aliases are refused. CSV supports UTF-8 BOM, CRLF, normalized header case/whitespace and the selected comma/semicolon separator. See [schema details](schema.md).

Text is readable in terminals; JSON is structured; Markdown and `regmap` carry draft regulation mappings; SARIF 2.1.0 supports code-scanning annotations. See the [report contract](reports.md) for fields, schema and snapshots. Locations and vendor identifiers can reveal register data. See [CI report handling](ci.md) before publishing them.

Output refuses input-file aliases and final symlinks. `RESILINT_OUTPUT_ROOT`, when set, constrains outputs to that directory tree; unset/empty allows ordinary filesystem destinations. The Action sets it to the workspace. Parent directories must exist. Normal reports and baselines are not atomic multi-file transactions; use version control or backups for recovery. Protection assumes trusted output parent directories, not concurrent hostile directory replacement.

For the remaining commands and all their flags, see [drill records](drills.md) and [draft RoI exports](roi.md). See [rule guidance](rules.md), [configuration](config.md), [baselines](baseline.md) and [FAQ](faq.md).
