# Drill records

Record actual tabletop/test evidence separately from the vendor register:

```bash
resilint drill record vendors.yaml --vendor example-vendor --kind tabletop --result pass
resilint check vendors.yaml --drills drills.yaml
```

| Argument or flag | Meaning / default |
| --- | --- |
| `FILE` | Required register used to validate the vendor ID |
| `--vendor ID` | Required existing vendor |
| `--kind` | Required `tabletop` or `test` |
| `--result` | Required `pass`, `partial` or `fail` |
| `--date YYYY-MM-DD` | Actual drill date; defaults to the local current date; future dates refused |
| `--notes TEXT` | Optional notes, at most 500 characters |
| `--log FILE` | Log destination; defaults to `drills.yaml` beside the register |
| `--csv-delimiter` | `,` or `;` for a CSV register; default comma |
| `-h`, `--help` | Show command help |

Only record an outcome once it occurred. The register is never rewritten. The log is normalized YAML, so existing log comments/layout are not retained. Logs use safe YAML parsing, alias refusal, UTF-8 and the 5 MiB input cap; every entry must reference an existing vendor.

Writers serialize through a persistent `LOG.lock` sidecar, using Windows byte-range locking or POSIX `flock`. A busy lock is retried for about two seconds, then returns exit 2. Successful writes replace the log through a temporary file in the same directory. Do not delete the sidecar while writers are active. Output-root, input-identity and symlink guards apply.

Log-target validation, reading and replacement all occur while holding that lock, so cooperating writers do not inspect a Windows log during another writer's replacement. An unsuccessful record attempt can leave the persistent sidecar; validation failures do not modify the register or log.

`check --drills LOG` applies records in date order. Passed/partial records can advance a vendor's effective `last_tested`; the latest failed drill raises RL009 for critical/high vendors. The original register stays unchanged. Config ignores and baselines apply after this evaluation. See [CLI usage](usage.md), [rules](rules.md) and [configuration](config.md).
