# Changelog

## [0.1.0] - unreleased (in review)
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
