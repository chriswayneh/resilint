# Rule configuration

`resilint check` reads `.resilint.yaml` from the current working directory when present. Use `--config FILE` to select another file; an explicitly selected missing file is an error. Export and drill-record commands do not apply rule settings.

```yaml
fail_on: high
stale_days: 365
contact_days: 180
max_critical: 3
ignore:
  - rule: RL001
    vendor: example-cloud
    reason: Fictional remediation tracked in the team's work queue
    expires: 2027-01-31
```

All keys are optional; an empty file uses defaults shown above and no ignores. Unknown keys, invalid values or malformed files fail with exit 2. Config files use safe YAML, reject aliases and have the same 5 MiB limit as registers. These are local settings and are never fetched remotely.

`fail_on` accepts `low`, `medium`, `high` or `critical`. Day and concentration thresholds must be nonnegative integers; booleans and numeric strings are rejected. Explicit `--fail-on`, `--stale-days`, `--contact-days` and `--max-critical` flags override the corresponding file values, including zero. Without a flag or file value the built-in default applies. The entire file is validated even if a flag overrides a value. For example:

```bash
resilint check examples/vendors.yaml --config team.yaml --fail-on critical
```

Each ignore requires exactly `rule`, `vendor`, `reason` and `expires`. Rule IDs must be known; vendor matching is exact and case-sensitive, with no wildcards. Rule/vendor/reason must be nonblank text. Expiry must be a calendar date in `YYYY-MM-DD` form, either a YAML date or quoted string. An ignore applies through its expiry date according to the machine's local date; the finding reappears on the following day. A past expiry is valid configuration but does not suppress anything.

Active ignores remove matching rule/vendor findings from every report format and from the exit-code calculation. Other findings remain visible. Keep reasons and expiry dates under version control for review: configuration can deliberately hide findings, so CI should use a configuration file whose authors are trusted to set project policy. No vendor is contacted, and no source register or configuration file is rewritten.

The composite GitHub Action supplies its `fail-on` input as an explicit CLI flag, so that input takes precedence over config `fail_on`. Its other thresholds can come from `.resilint.yaml` in the workflow working directory.
