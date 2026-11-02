# Changelog

## [Unreleased]
### Added
- Dedicated installation, usage, rule, drill, export and FAQ guides document every CLI option; CI checks relative Markdown links and headings without fetching external URLs.
- `resilint explain RL001` through `RL009` provides offline rule descriptions, illustrative fixes and draft references; unknown IDs return a controlled error.
- `resilint init [FILE]` creates a packaged, commented fictional starter register without overwriting existing files; its three intentional findings guide the first edit.
- GitLab CI, Azure Pipelines and generic CI recipes preserve check exit status and document report handling.
- A pre-commit hook checks multiple vendor registers with repository rule settings, preserves inputs and treats option-like filenames as data.
- A hosted Action self-test checks SARIF creation, threshold failure, zero findings and invalid-input outputs using the local composite Action.
- A complete SHA-pinned SARIF upload workflow example scopes upload permissions to its job and preserves threshold/input failure status after upload.
- The GitHub Action exposes `findings`, `highest-severity` and `exit-code` from its report-producing check, preserving threshold failures and distinguishing errors from empty reports.
- Baseline snapshots and filtering with stable rule/vendor/field fingerprints, including distinct process identities for recovery-time findings; JSON findings now include their field identifier.
- `.resilint.yaml` rule thresholds and exact rule/vendor ignores with required reasons and expiry dates; explicit CLI flags override file settings and expired ignores re-fire findings.
- CLI exit-2 diagnostics consistently include file and line context, with `0` for an unavailable line and `<cli>` for argument errors; control characters are escaped and CSV/YAML parser locations are retained where known.
- Published a Draft 2020-12 register JSON Schema with field examples, editor/CI guidance and validation tests for the fictional register examples; runtime validation remains unchanged.
- CSV register commands accept `--csv-delimiter ';'`; BOM/CRLF files and case-insensitive, whitespace-trimmed headers are supported. Malformed rows and invalid vendor/process values report their CSV row number with exit 2.
- A CI performance regression checks 10,000 vendors and 2,000 processes from CSV, including JSON reporting, within five seconds; CLI tests verify clear errors above the documented 5 MiB input cap.
- Reproducible Hypothesis tests exercise bounded YAML/CSV bytes, text, structured fields and valid registers through both the loader and CLI.
- Repository metadata checks keep package/runtime versions, the latest released changelog entry, and README release references synchronized.
### Fixed
- Invalid YAML scalar dates and oversized numeric values, unsupported schema-version strings, and CSV parser/field-limit errors now return a diagnostic with exit 2 instead of an uncaught exception.
- `drill record` now locks the log on Windows using a native byte-range lock, preventing concurrent writers from losing successful records. Linux/macOS retain their existing lock behavior and the same bounded wait.
- Unexpected operating-system lock errors return exit 2 and close the lock file instead of raising a traceback.
### Changed
- CI now tests Linux, Windows and macOS on Python 3.10, 3.12 and 3.13 independently; concurrent drill-write failures include each child process's diagnostic.
- Each CI matrix job now requires at least 90% total statement coverage across `src/resilint`, using the development dependency `pytest-cov` and reporting missing lines.
- Tests are grouped by loader, rules, reports, RoI exports, drills and CLI behavior, with shared helpers and platform fixtures; existing assertions and parametrized cases are preserved.
- The Action format description includes `regmap` and documents CLI input validation. Self-tests execute its Bash check step to verify invalid formats and severity thresholds exit 2 without writing a report.
- Roadmap documentation uses compact version and milestone summaries, with detailed task criteria and contributor guidance under `roadmap/`.
- The composite Action and CI use SHA-pinned `actions/setup-python` v7.1.0. The development Action requires a Node 24-capable Actions Runner (v2.327.1 or later); update self-hosted runners before upgrading.
- CI runs lint, type checks, and tests on both Linux and Windows with Python 3.10 and 3.12. Symlink tests require symlink privileges in CI; local Windows runs skip those tests only when that privilege is unavailable.
- Runtime dependency PyYAML is updated to 6.0.3, retaining hash-pinned installation; all 73 allowed distribution hashes match PyPI's published SHA-256 digests.

## [0.4.0] - 2026-10-24
### Added
- `resilint drill record REGISTER --vendor ID --kind tabletop|test --result pass|partial|fail [--date] [--notes] [--log]`: adds a drill result to a drill log (default `drills.yaml` next to the register) and rewrites the log in normalized form (comments in the log are not kept); the register is never rewritten. Future dates and log entries for unknown vendors are refused.
- `check --drills LOG`: the latest passed or partial drill updates a vendor's effective last-tested date; rule RL009 (medium) flags a vendor whose most recent drill failed, with a draft regulation reference (not legal advice). Action input `drills`.
- README "See it in 60 seconds" section with generated sample output.
### Security
- Drill logs use the register's safe YAML loading, alias refusal, and 5 MB cap; notes are limited to 500 characters; writes use the not-the-input, no-symlink, and `RESILINT_OUTPUT_ROOT` checks, an exclusive lock on a `LOG.lock` sidecar (POSIX-only, Linux/macOS; on Windows no lock is taken, so avoid concurrent `drill record` runs there), and an atomic temp-file replace.
- `export-roi` uses NFKC normalization only to detect formula-injection characters and writes the original text (prefixed with `'` when unsafe).
- `export-roi --force` validates every target file (symlink, output root, input file) before writing any of them.

## [0.3.0] - 2026-10-24
### Added
- export-roi `critical_or_important`: critical/high -> Yes, medium/low -> No, unset -> Assessment not performed. B_02.02 output is a partial column set.
- `--format regmap`: regulation mapping report grouping findings by DORA, NIS2, and PRA SS2/21 reference (draft mapping, not legal advice).
- `regulation_refs` (structured per-framework references) on every finding in JSON output.
- `resilint export-roi FILE --out-dir DIR`: draft CSV export toward DORA register-of-information templates B_05.01, B_06.01, and B_02.02.
- Optional vendor fields `lei` (ISO 17442 format and check digits) and `country` (validated against the assigned ISO 3166-1 alpha-2 list).
### Security
- `RESILINT_OUTPUT_ROOT`: when set, output paths whose real path is outside it are refused (exit 2). The GitHub Action sets it to `$GITHUB_WORKSPACE`.
- `export-roi` neutralizes spreadsheet formula injection (NFKC-normalized; `= + - @ | %`, tab, CR/LF, including after leading whitespace), refuses symlinked or missing output directories (path normalized first, so trailing slashes can't bypass the check), enforces `RESILINT_OUTPUT_ROOT`, and refuses to overwrite existing files (`O_EXCL`) unless `--force`.

## [0.2.0] - 2026-10-24
### Added
- SARIF 2.1.0 output (`--format sarif`) with per-vendor line locations for pull request annotations; `--output FILE`; Action `format: sarif` and `output` inputs.
- `contacts_verified` vendor field (YAML and CSV) and rule RL008 (missing or stale contact verification, `--contact-days`, default 180), with a draft regulation reference (not legal advice).
- Versioned input schema: optional top-level `schema_version` (currently `1`); unsupported versions exit 2.
### Security
- `--output` refuses the input file and symlink paths (exit 2) and opens with `O_NOFOLLOW` where available.
- SARIF uri is percent-encoded, relative to `%SRCROOT%`, and reduced to the file name for inputs outside the working directory.
- Unquoted YAML datetimes in `last_tested` and `contacts_verified` are converted to dates instead of breaking date checks.

## [0.1.0] - 2026-10-24
### Added
- `resilint check` for YAML and CSV vendor registers, with text, JSON, and Markdown output.
- Rules RL001-RL007 with draft DORA / NIS2 / PRA SS2/21 references (not legal advice).
- `--fail-on`, `--stale-days`, `--max-critical`; exit codes 0/1/2.
- Composite GitHub Action, CI (pytest + ruff), fictional examples.
- Dependabot for github-actions and pip; hash-pinned PyYAML (`requirements-lock.txt`).
### Security
- Actions pinned to full commit SHAs; YAML aliases refused with a clear error message; deep nesting and non-finite hours (NaN/inf) rejected with exit 2; Markdown report escapes HTML/Markdown characters.
### Fixed
- RL006 regulation reference matches README; report version comes from `__version__`; Quick start points at `examples/vendors.yaml`.
