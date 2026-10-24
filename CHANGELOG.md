# Changelog

## [0.4.0] - Unreleased
### Added
- `resilint drill record REGISTER --vendor ID --kind tabletop|test --result pass|partial|fail [--date] [--notes] [--log]`: appends a drill result to a drill log (default `drills.yaml` next to the register); the register is never rewritten.
- `check --drills LOG`: the latest passed or partial drill updates a vendor's effective last-tested date; rule RL009 (medium) flags a vendor whose most recent drill failed, with a draft regulation reference (not legal advice). Action input `drills`.
- README "See it in 60 seconds" section with generated sample output.
### Security
- Drill logs use the register's safe YAML loading, alias refusal, and 5 MB cap; notes are limited to 500 characters; writes use the no-follow, not-the-input, and `RESILINT_OUTPUT_ROOT` checks.

## [0.3.0] - unreleased (in review)
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
