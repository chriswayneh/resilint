# Roadmap working guide

The [roadmap overview](../ROADMAP.md) is the readable summary. [Task definitions](issues.yml) retain the acceptance criteria, files, effort estimates and dependencies for all 38 tasks.

- [Contributor rules](#contributor-rules)
- [Coverage gate](#coverage-gate)
- [Loader property tests](#loader-property-tests)
- [Release checklist](#release-checklist)
- [Released versions](#released-versions)
- [Historical baseline](#historical-baseline)

Include final task status, completion PRs in `issues.yml`, and overview updates in the feature PR so they reach `main` together at merge. Mark a version released only after publication by the maintainer or authorized delegate.

## Contributor rules

1. One task = one branch `<type>/<task-id>-<slug>` = one small PR against `main`. Don't bundle tasks.
2. Never force-push, rebase, or rewrite history. Fix review feedback with new commits.
3. Merge after review passes on the exact head commit (code PRs also need a security review). The maintainer may explicitly delegate review, merging and release publication; delegated work retains all validation gates.
4. Never change repo visibility, settings, branch protection, or secrets. Tags and releases are created by the maintainer or an explicitly authorized delegate (task R-5).
5. Every PR must pass the gate commands locally: `ruff check . && mypy src && pytest -q && git diff --check`. Paste the output in the PR body.
6. The PR body includes the task id, what changed, the acceptance results, and a CHANGELOG `[Unreleased]` entry for any user-visible change.
7. Keep these non-goals: no network calls, no vendor contact or scraping, no SaaS, no telemetry. Use fictional data only in examples and tests.
8. Update docs in the same PR when behavior, flags, or schema change.

## Coverage gate

Install development dependencies with `pip install -e ".[dev]"`, then run this from the repository root:

```bash
pytest -q --cov=src/resilint --cov-report=term-missing --cov-fail-under=90
```

Each CI matrix job requires at least 90% total statement coverage across all Python modules in `src/resilint`, including modules the tests never import. This is an aggregate statement-coverage threshold, not a per-file or branch-coverage threshold. Missing lines are listed in the terminal report. No additional coverage exclusions are configured.

The CI coverage command is explicit; plain `pytest -q` and targeted test runs retain their existing behavior. Coverage data files are ignored by Git.

## Loader property tests

After installing `.[dev]`, run `pytest -q tests/test_loader_fuzz.py` from the repository root. Hypothesis uses reproducible generation with up to 750 bounded generated examples per run, plus explicit regression seeds. Each example checks the loader and JSON CLI: either a usable register/report, or `InputError` and exit 2 with a diagnostic. Inputs remain unchanged.

Raw inputs are capped at 512 bytes or 1,024 characters; structured values use at most 15 leaves. Explicit seeds also cover invalid dates, oversized numbers and CSV field limits. Valid generated registers ensure the loader still accepts ordinary data. These finite checks do not prove every possible input safe. Hypothesis deadlines are disabled for filesystem/CI variability; input sizes and example counts are bounded. Its local cache is ignored by Git.

## Release checklist

Apply this checklist to each release from v0.4.1 through v1.0.0.

- [ ] All milestone PRs merged by the maintainer or authorized delegate after review (+ security review for code) on the exact head SHA
- [ ] `pyproject.toml` version == `src/resilint/__init__.py` == CHANGELOG heading (`tests/test_meta.py` green)
- [ ] CHANGELOG: `[Unreleased]` renamed to `[X.Y.Z] - YYYY-MM-DD`; Added/Changed/Security/Fixed filled in; fresh empty `[Unreleased]`
- [ ] README/ROADMAP/SECURITY status and badges reflect the release; Action examples pinned to the new tag
- [ ] `ruff check . && mypy src && pytest -q` green; CI matrix green on `main`
- [ ] `python -m build && twine check dist/*`; fresh-venv install + `resilint --version`
- [ ] Secrets scan clean (gitleaks/trufflehog on full history); `pip-audit` clean; examples contain only fictional data
- [ ] Action self-test green; all `uses:` are full-SHA pinned
- [ ] Tag `vX.Y.Z` created by the maintainer or authorized delegate; release notes from CHANGELOG; SBOM + provenance attached; PyPI publish approved in the `pypi` environment
- [ ] For v1: move the `v1` tag; announce the stability policy

## Released versions

### v0.1 - Core checks (released 2026-10-24)

- YAML schema for vendors and business processes, plus CSV import from spreadsheet exports
- Missing-field rules for critical/high vendors: notification SLA, recovery time, contact, exit plan, recent resilience test
- Consistency rules: vendor recovery time vs. dependent process RTO; concentration of critical processes on one vendor
- Draft regulation reference on every finding (DORA, NIS2, UK PRA SS2/21)
- Text, JSON, and Markdown output; exit codes `0`/`1`/`2`
- Minimal composite GitHub Action

### v0.2 - CI polish (released 2026-10-24)

- SARIF 2.1.0 output (`--format sarif`, `--output FILE`) for pull request annotations via code scanning
- `contacts_verified` dates with rule RL008 and `--contact-days`; versioned schema (`schema_version: 1`, unknown versions rejected)

### v0.3 - Regulatory reporting (released 2026-10-24)

- Regulation mapping report (`--format regmap`) and structured `regulation_refs` per finding (DORA, NIS2, UK PRA SS2/21)
- `export-roi`: draft CSV export toward DORA register-of-information templates (B_05.01, B_06.01, B_02.02), to be completed and checked with an existing RoI validator; optional `lei` and `country` vendor fields

### v0.4 - Drill records (released 2026-10-24)

- `drill record` command to attach tabletop or test results to a vendor and update its last-tested date
- `check --drills LOG` applies the log; rule RL009 flags a vendor whose most recent drill failed

## Historical baseline

Baseline snapshot (2026-11-02, before M0-1): `main` @ 7e1a9f9. Released tags v0.1.0–v0.4.0 (all 2026-10-24). `pyproject.toml` and `__init__.py` are 0.4.0. ~1,000 LOC across `src/resilint/{cli,loader,rules,report,roi,drills}.py`, with 68 tests in one file (`tests/test_resilint.py`). CI runs ruff, mypy, and pytest on ubuntu with Python 3.10 and 3.12. The composite `action.yml` uses SHA-pinned actions.
At baseline, open PRs: #9 (Windows drill locks + Windows CI, which also folds in #8), #8 (docs reconcile v0.4.0), and Dependabot #2/#3/#4 (checkout 7.0.1, setup-python 7.1.0, pyyaml 6.0.3). There were no open issues.
At baseline, known drift: CHANGELOG says `[0.4.0] - Unreleased`, even though v0.4.0 was tagged and released. The README badge and status still say v0.2.0. The Action `format` input description omits `regmap`. There is no PyPI package or release workflow, and the install is `pip install git+...`.
