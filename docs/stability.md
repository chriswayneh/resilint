# Stability policy for v1

This policy takes effect with v1.0.0. Development commits and release candidates can change before that release; the current package version does not imply unreleased features are already stable.

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
