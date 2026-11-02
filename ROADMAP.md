# Roadmap

Status: **v0.4.0 released (2026-10-24). Next: v0.4.1 maintenance, then the path to v1.0.0 below.** Milestones and scope may change.

## Released

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

## Path to v1.0.0

Baseline snapshot (2026-11-02, before M0-1): `main` @ 7e1a9f9. Released tags v0.1.0–v0.4.0 (all 2026-10-24). `pyproject.toml` and `__init__.py` are 0.4.0. ~1,000 LOC across `src/resilint/{cli,loader,rules,report,roi,drills}.py`, with 68 tests in one file (`tests/test_resilint.py`). CI runs ruff, mypy, and pytest on ubuntu with Python 3.10 and 3.12. The composite `action.yml` uses SHA-pinned actions.
At baseline, open PRs: #9 (Windows drill locks + Windows CI, which also folds in #8), #8 (docs reconcile v0.4.0), and Dependabot #2/#3/#4 (checkout 7.0.1, setup-python 7.1.0, pyyaml 6.0.3). There were no open issues.
At baseline, known drift: CHANGELOG says `[0.4.0] - Unreleased`, even though v0.4.0 was tagged and released. The README badge and status still say v0.2.0. The Action `format` input description omits `regmap`. There is no PyPI package or release workflow, and the install is `pip install git+...`.

Progress (2026-11-02): **M0-1 complete.** [PR #9](https://github.com/chriswayneh/resilint/pull/9) merged at `90ddefe` after maintainer approval of reviewed head `e23e460`; PR #8 closed as included. Exact-head CI passed on Ubuntu/Windows × Python 3.10/3.12 (113 tests each), and the security diff review completed with no findings. Windows drill locking and release documentation corrections are on `main`; v0.4.1 remains unreleased. Next: M0-2 dependency triage.

### Contributor rules
1. One task = one branch `<type>/<task-id>-<slug>` = one small PR against `main`. Don't bundle tasks.
2. Never force-push, rebase, or rewrite history. Fix review feedback with new commits.
3. Contributors do not merge. The maintainer merges after review passes on the exact head commit (code PRs also need a security review).
4. Never change repo visibility, settings, branch protection, or secrets. Tags and releases are created only by the maintainer (task R-5).
5. Every PR must pass the gate commands locally: `ruff check . && mypy src && pytest -q && git diff --check`. Paste the output in the PR body.
6. The PR body includes the task id, what changed, the acceptance results, and a CHANGELOG `[Unreleased]` entry for any user-visible change.
7. Keep these non-goals: no network calls, no vendor contact or scraping, no SaaS, no telemetry. Use fictional data only in examples and tests.
8. Update docs in the same PR when behavior, flags, or schema change.

### Milestone 0 — Land open work and reconcile (v0.4.1)
| ID | Title | Why | Files | Acceptance | Size | Deps |
|---|---|---|---|---|---|---|
| M0-1 | **Complete** — Review/land PR #9 (supersedes #8) | Windows lock data loss; release docs drift | `drills.py`, `ci.yml`, docs | CI green on ubuntu+windows × 3.10/3.12; review passes; close #8 as included | M | — |
| M0-2 | Triage Dependabot #2, #3, #4 | Stale pins; checkout/setup-python are major jumps | `ci.yml`, `action.yml`, `requirements-lock.txt` | Each PR is CI green; pins stay full SHAs; the lock keeps `--require-hashes`; pyyaml 6.0.3 hash verified | S | M0-1 |
| M0-3 | Version/docs sync check | Stop recurring drift | new `tests/test_meta.py` | Test asserts `pyproject` version == `__version__` == the top released CHANGELOG heading or `[Unreleased]`; the README has no hard-coded old version | S | M0-1 |
| M0-4 | Action `format` input lists `regmap`; validate inputs | Docs mismatch | `action.yml`, README | The description matches CLI choices; an invalid format exits 2 in an action self-test (M2-3) | S | M0-1 |

### Milestone 1 — v0.5 Hardening (real-world data)
| ID | Title | Why | Files | Acceptance | Size | Deps |
|---|---|---|---|---|---|---|
| H-1 | Split tests by module | A 685-line single file is hard to review | `tests/test_{loader,rules,report,roi,drills,cli}.py`, `conftest.py` | Same test count or more; `pytest -q` green; no behavior change | M | M0-1 |
| H-2 | Coverage gate | Measurable quality | `pyproject` dev deps (`pytest-cov`), `ci.yml` | CI fails if coverage is <90% for `src/resilint` | S | H-1 |
| H-3 | Property/fuzz tests for loader | Untrusted YAML/CSV from teams | `tests/test_loader_fuzz.py` (hypothesis) | Random YAML/CSV never raises an uncaught exception. Outcomes are only a clean result or exit 2 with a message | M | H-1 |
| H-4 | Large-register performance | Real registers have 1k–10k vendors | `tests/test_perf.py`, `loader.py`/`rules.py` if needed | 10,000 vendors + 2,000 processes checks in <5s on CI; the 5 MB cap is documented, with a clear error past it | M | H-1 |
| H-5 | CSV robustness | Spreadsheet exports vary | `loader.py`, tests, README | Handles UTF-8 BOM, `;` delimiter (`--csv-delimiter`), CRLF, and header case/whitespace. A bad row gives an error with the row number and exits 2 | M | H-1 |
| H-6 | Published JSON Schema for the register | Lets teams validate in editors/CI | `schema/register.v1.json`, `docs/schema.md`, test | Examples validate against the schema (test with `jsonschema` as a dev dep); every field is documented with type and example | M | H-1 |
| H-7 | Stable error messages and codes | Usable in CI logs | `loader.py`, `cli.py` | Every exit-2 path prints `resilint: error: <file>:<line>: <msg>` to stderr; tests cover each path | M | H-1 |
| H-8 | Rule config file | Teams need per-repo thresholds and suppressions | `config.py` (new), `cli.py`, docs | `.resilint.yaml` supports `fail_on`, `stale_days`, `contact_days`, `max_critical`, and `ignore: [{rule, vendor, reason, expires}]`. An expired ignore re-fires the finding. CLI flags override the file. Tests cover precedence | L | H-7 |
| H-9 | Baseline mode | Adopting on an existing register without failing CI day one | `cli.py`, `baseline.py` | `--baseline FILE` reports only new findings, and `--write-baseline` creates the file. Stable finding fingerprints (rule+vendor+field) are tested | M | H-8 |
| H-10 | Windows/macOS CLI parity | Users run locally | `ci.yml` | Matrix ubuntu/windows/macos × 3.10/3.12/3.13 is green | S | M0-1 |

### Milestone 2 — v0.6 CI integration and DX
| ID | Title | Why | Files | Acceptance | Size | Deps |
|---|---|---|---|---|---|---|
| C-1 | Action outputs | Downstream steps need counts | `action.yml` | Outputs `findings`, `highest-severity`, `exit-code`; documented | S | M0-4 |
| C-2 | SARIF upload example workflow | The most common real use | `examples/workflows/resilint-sarif.yml`, README | Uses `github/codeql-action/upload-sarif` pinned by SHA, with `security-events: write` only on that job | S | C-1 |
| C-3 | Action self-test workflow | Prevent a broken Action release | `.github/workflows/action-test.yml` | Runs `uses: ./` on examples; asserts exit code 1 and the SARIF file exists | S | C-1 |
| C-4 | pre-commit hook | Catch gaps before the PR | `.pre-commit-hooks.yaml`, README | `pre-commit try-repo . resilint --files examples/vendors.yaml` runs | S | M0-1 |
| C-5 | GitLab CI / generic CI recipe | Not all teams use GitHub | `docs/ci.md` | Copy-paste GitLab and Azure Pipelines snippets, tested by hand with the documented commands | S | — |
| C-6 | `resilint init` | Faster onboarding | `cli.py`, template | Writes a commented starter `vendors.yaml` and refuses to overwrite; the output passes `check` with only expected findings | S | H-6 |
| C-7 | `resilint explain RLxxx` | Self-serve fix guidance | `rules.py`, `cli.py` | Prints rule description, fix example, and draft reg refs for all RL001–RL009; unknown id exits 2 | S | — |

### Milestone 3 — v0.9 Docs and API freeze (release candidate)
| ID | Title | Why | Files | Acceptance | Size | Deps |
|---|---|---|---|---|---|---|
| D-1 | `docs/` site content | README is overloaded | `docs/{install,usage,rules,schema,ci,drills,roi,faq}.md` | Every CLI flag and rule is documented; links check passes (`lychee` or a script in CI, offline-only for relative links) | M | H-8, C-7 |
| D-2 | Stability policy | v1 needs a contract | `docs/stability.md` | Defines the semver surface (CLI flags, exit codes, JSON/SARIF fields, schema v1, rule IDs) and the deprecation policy | S | D-1 |
| D-3 | JSON output schema + snapshot tests | Auditors depend on the format | `schema/report.v1.json`, golden-file tests | JSON output validates against the schema; golden snapshots for text/md/json/sarif/regmap | M | H-1 |
| D-4 | Legal disclaimer consistency | Regulatory mappings are drafts | README, docs, report footers | "Draft, not legal advice" appears in README, regmap, md, and RoI outputs; a test asserts it | S | D-1 |
| D-5 | Deprecate/remove anything not in the freeze | Clean v1 surface | `cli.py`, CHANGELOG | Lists removed/deprecated items; warnings tested | S | D-2 |
| D-6 | CONTRIBUTING + issue/PR templates | Outside users | `CONTRIBUTING.md`, `.github/ISSUE_TEMPLATE/*`, `PULL_REQUEST_TEMPLATE.md` | Templates include the gate commands and the "fictional data only" rule | S | — |

### Milestone 4 — Packaging and release automation
| ID | Title | Why | Files | Acceptance | Size | Deps |
|---|---|---|---|---|---|---|
| P-1 | Build sdist/wheel in CI | Verify packaging | `ci.yml` | `python -m build` + `twine check dist/*` pass; wheel install in a fresh venv runs `resilint --version` | S | M0-1 |
| P-2 | Release workflow (PyPI Trusted Publishing) | `pip install resilint` | `.github/workflows/release.yml` | Triggered on `v*` tag only; OIDC trusted publisher (no API token secret); environment `pypi` with manual approval; uploads to TestPyPI first. **Maintainer configures PyPI and the environment** | M | P-1 |
| P-3 | Provenance + SBOM | Supply-chain trust for a security tool | `release.yml` | `actions/attest-build-provenance` (SHA-pinned) and a CycloneDX SBOM attached to the GitHub release | M | P-2 |
| P-4 | Security scanning in CI | Gate secrets/vulns | `.github/workflows/security.yml` | gitleaks (or `trufflehog --only-verified`) on PRs, `pip-audit -r requirements-lock.txt`, CodeQL python; all pinned by SHA, least-privilege permissions | S | — |
| P-5 | Action version tags policy | Users pin `@v1` | `docs/stability.md`, README | Documents `@v1` moving tag + `@v1.0.0` + SHA pinning advice | S | D-2 |
| P-6 | Install docs switch to PyPI | Real-world install | README, docs | `pip install resilint==X` and `pipx install resilint` are documented; the git install is kept as an alternative | S | P-2 |

### Milestone 5 — v1.0.0 cut
| ID | Title | Why | Acceptance | Size | Deps |
|---|---|---|---|---|---|
| R-1 | v1.0.0-rc1 PR (version bump + CHANGELOG) | Freeze | Versions synced (M0-3 test green), CHANGELOG `[1.0.0-rc1]`, ROADMAP marks v1 | S | all M1–M4 |
| R-2 | Dogfood on a realistic synthetic register | Real-world proof | `examples/large/` (fictional, 500 vendors) runs every format plus baseline/config/drills/export-roi in CI | M | R-1 |
| R-3 | Fresh-machine install test | Catch packaging misses | TestPyPI install on ubuntu/windows/macos runs the quick start verbatim | S | R-1, P-2 |
| R-4 | Final review and security review of the full diff since v0.4.0 | Security tool | Review and security review passed on the RC head SHA | M | R-2, R-3 |
| R-5 | Tag `v1.0.0` + release (maintainer only) | Ship | Release checklist below completed | S | R-4 |

### Release checklist (each release, v0.4.1 → v1.0.0)
- [ ] All milestone PRs merged by the maintainer after review (+ security review for code) on the exact head SHA
- [ ] `pyproject.toml` version == `src/resilint/__init__.py` == CHANGELOG heading (`tests/test_meta.py` green)
- [ ] CHANGELOG: `[Unreleased]` renamed to `[X.Y.Z] - YYYY-MM-DD`; Added/Changed/Security/Fixed filled in; fresh empty `[Unreleased]`
- [ ] README/ROADMAP/SECURITY status and badges reflect the release; Action examples pinned to the new tag
- [ ] `ruff check . && mypy src && pytest -q` green; CI matrix green on `main`
- [ ] `python -m build && twine check dist/*`; fresh-venv install + `resilint --version`
- [ ] Secrets scan clean (gitleaks/trufflehog on full history); `pip-audit` clean; examples contain only fictional data
- [ ] Action self-test green; all `uses:` are full-SHA pinned
- [ ] Tag `vX.Y.Z` created by the maintainer; release notes from CHANGELOG; SBOM + provenance attached; PyPI publish approved in the `pypi` environment
- [ ] For v1: move the `v1` tag; announce the stability policy

### Totals
M0: 4 · M1: 10 · M2: 7 · M3: 6 · M4: 6 · M5: 5 → **38 tasks**

## Non-goals
- No vendor questionnaires
- No scraping or contacting vendors
- No hosted SaaS; it runs locally and offline on your own data
