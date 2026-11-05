# Stability policy for v1

This policy applies to v1.0.0 and later stable v1 releases. Development commits and release candidates can change before stable publication; their version identifiers do not imply that unreleased changes are stable.

## Supported interfaces

| Surface | Compatibility commitment within v1 |
| --- | --- |
| CLI | Documented `check`, `init`, `explain`, `drill record` and `export-roi` commands; their flags, accepted values and documented defaults |
| Exit status | `0` success, `1` threshold findings, `2` controlled input/output/argument errors; snapshot creation's documented success behavior |
| Diagnostics | The exit-2 `resilint: error: FILE:LINE: MESSAGE` envelope; exact prose is not an API |
| Register schema v1 | Documented fields, types and normalization; unsupported schema versions are rejected |
| JSON reports | Existing documented field names, types and meanings; clients must tolerate additional fields |
| SARIF | SARIF 2.1.0 and documented rule IDs, severity/vendor properties, location structure and partial-fingerprint representation |
| Baselines | Version-1 file format and SHA-256 identity over rule/vendor/field; known identities remain comparable |
| Rule IDs | RL001–RL009 retain their identity and purpose; removed IDs are never reassigned |
| Configuration | Documented keys, precedence, exact ignore matching and inclusive expiry semantics |
| Integrations | Documented Action inputs/outputs and the `resilint` pre-commit hook ID and filename behavior |

The Python import API, private modules/adapters, dataclass constructors, internal keyword arguments, test helpers and package layout are implementation details. Human-readable text, Markdown, `regmap`, help prose and illustrative fix wording may improve without preserving byte-for-byte output. The draft RoI column mapping is experimental and can change with explicit release notes; it is not a filing contract. Regulation references remain draft mapping, not legal advice.

## Version changes

Patch releases fix defects without intentionally removing supported interfaces. Correcting a false positive/negative or rejecting unsafe malformed input may change findings; release notes must describe that effect. Critical security fixes can tighten accepted input when retaining it would be unsafe.

Minor releases may add commands, flags, optional fields or rules. New rules can introduce findings and fail an existing CI threshold, so review the changelog and pin an exact version when updates need controlled adoption. Existing default thresholds and severity meanings remain stable unless a documented defect is corrected. Removing supported interfaces, renaming fields or repurposing rule IDs requires a major release.

## Deprecation

Deprecations are announced in the changelog and affected guide with a replacement and migration example. Deprecated CLI options remain usable for the rest of the major version and for at least one subsequent minor release and six months before removal in a later major version. Warnings go to stderr, preserve the command's existing exit status, and have regression tests. Security-driven exceptions must state the reason and migration path.

There are no active deprecations or planned removals for v1. Python internals and the experimental draft RoI mapping are explicitly outside the stable interface above. See [CLI usage](usage.md), [schema](schema.md), [baseline format](baseline.md), [configuration](config.md) and the [changelog](../CHANGELOG.md).

## Action version tags

The `@v1` alias and immutable `@v1.0.0` reference are available and currently point to reviewed stable source `d5aa0b6223ed930adc753fe94aa212a9ba686c43`. The `v1` alias tracks reviewed stable v1 releases only, after the [release checklist](../roadmap/README.md#release-checklist) is complete. It must never point to a release candidate or a different major version.

| Reference | Update behavior |
| --- | --- |
| `@v1` | Moving major alias; receives reviewed stable v1 fixes and additions without a workflow edit |
| `@v1.0.0` | Exact release name; project policy keeps version tags immutable |
| Full 40-character commit SHA | Pins this repository's code for controlled adoption; update deliberately after reviewing release notes |

Resolve a chosen published version reference to its commit and record the readable version in a comment beside the SHA. A SHA does not make the runner, network services or every transitive dependency immutable. New minor-version rules can produce new findings even within v1; review the changelog before updating a pinned reference when findings changes need controlled adoption.

This policy describes reference behavior and grants no operational authorization. Creating or moving any tag requires actual user authorization and the applicable release gates. The moving major alias is distinct from immutable version tags; this document does not authorize rewriting version tags or branch history.

## v1 freeze audit

The v0.4.0 CLI was compared with the proposed v1 interface. All 17 existing long flags, the five report formats, the three existing command paths and RL001–RL009 are retained. The additions are `init`, `explain`, `--config`, `--baseline`, `--write-baseline` and `--csv-delimiter`.

- Removed interfaces: none.
- Deprecated interfaces: none; no deprecation warnings are currently emitted.
- Excluded from the freeze: Python internals/adapters, exact human-readable prose and the experimental draft RoI column mapping listed above.

There is no replacement migration to perform for v1. Normal invocations of all five command paths have a warning-free smoke test in `tests/test_cli_freeze.py`. Future deprecations must add positive warning/migration tests under the policy above. The new diagnostic envelope and input validation tightenings are described in the changelog; configuration/baseline policy and new rules should always be reviewed before updating CI.
