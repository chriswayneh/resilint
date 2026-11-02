# Draft register-of-information export

Draft mapping, not legal advice. These CSVs are partial working tables, not official regulatory templates or a submission-ready filing. Complete missing fields and validate against the applicable official requirements before use.

```bash
mkdir roi-output
resilint export-roi vendors.yaml --out-dir roi-output
```

| Argument or flag | Meaning |
| --- | --- |
| `FILE` | Required YAML or CSV register |
| `--out-dir DIR` | Required existing directory, not a symlink |
| `--force` | Explicitly overwrite existing export files; otherwise any existing target is refused |
| `--csv-delimiter` | Register CSV separator, `,` (default) or `;`; output remains comma-separated |
| `-h`, `--help` | Show command help |

The export writes `b_05_01_providers.csv`, `b_06_01_functions.csv`, `b_02_02_links.csv` and `README.txt`. The names map toward provider, function and provider/function-link tables; the README states the partial mapping and limitations. Critical/high functions map to “Yes”, medium/low to “No”, and missing assessment to “Assessment not performed”.

Cells with formula-like prefixes are neutralized before CSV output; embedded line breaks become spaces. The register remains unchanged. Output-root, input-file and symlink guards apply. All destinations are checked before writing, but the export is not a multi-file transaction: an I/O failure can leave earlier completed files. Configuration ignores, baselines and drill overlays do not apply to this export command.

Success returns 0; invalid input, an existing target without `--force`, or a write error returns 2. See [schema](schema.md), [usage](usage.md) and the [FAQ](faq.md).
