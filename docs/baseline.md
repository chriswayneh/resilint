# Baseline mode

Save existing findings to adopt checks without failing CI on already recorded gaps:

```bash
resilint check examples/vendors.yaml --write-baseline baseline.json
resilint check examples/vendors.yaml --baseline baseline.json
```

Successful `--write-baseline FILE` creation or refresh returns 0, even when the snapshot contains findings. It still emits the normal report in the chosen format. `--baseline FILE` filters reports and threshold exit status to findings absent from that file: 0 when none reach the threshold, 1 when new findings do, and 2 for invalid input or failed output. The two flags are mutually exclusive. Writing explicitly replaces an existing baseline; filtering never modifies it.

The version-1 JSON file contains exactly `schema_version: 1` and a sorted, deduplicated `fingerprints` array. Each fingerprint is SHA-256 of the compact ASCII JSON array `[rule_id, vendor_id, field]`, using escaped Unicode. Messages, dates, source-file paths, row order, thresholds and regulation text are not identity components. JSON findings expose the `field` identifier. Most fields are the relevant register key; RL006 uses `supports_processes:<process-id>` so a new affected process is a new finding even for an existing vendor. These baseline identities are separate from the existing SARIF partial-fingerprint representation.

This means a known finding stays baselined when only its message or measured value changes. Review baseline refreshes as policy changes. Hashes are identifiers, not encryption; do not treat a baseline as a privacy guarantee.

Configuration ignores apply first. Active ignored findings are excluded from a newly written snapshot, so their expiry normally causes a new finding later. An older baseline that already includes that identity can still suppress it independently. Refresh from a full check with `--write-baseline` to remove resolved identities; baseline filtering is intentionally unavailable during refresh.

Baseline inputs must be regular UTF-8 JSON files no larger than 5 MiB. Malformed JSON, unsupported versions, invalid fingerprints and oversized generated snapshots fail with exit 2. Baselines do not fetch references or other resources.

Output protects the register, loaded configuration, applied drill log and loaded baseline from overwrite; report and baseline destinations must differ. Existing output-root and symlink checks apply. Files are written locally using the normal report writer, with no multi-file transaction guarantee: a completed baseline write remains if a later report write fails. Keep baselines under version control for review and recovery.
