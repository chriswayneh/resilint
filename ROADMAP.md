# Roadmap

Where resilint is going, and what is ready to work on.

**Current release:** [v0.4.0](https://github.com/chriswayneh/resilint/releases/tag/v0.4.0). **Next release:** v1.0.0, including the completed maintenance and hardening work. v2/v3 are deferred.

- [Milestones](#milestones)
- [v0.4.1: Maintenance](#v041-maintenance)
- [v0.5: Real-world data](#v05-real-world-data)
- [v0.6: CI integration and developer experience](#v06-ci-integration-and-developer-experience)
- [v0.9: Documentation and API freeze](#v09-documentation-and-api-freeze)
- [Packaging and release automation](#packaging-and-release-automation)
- [v1.0: Stable release](#v10-stable-release)
- [Governance adoption](#governance-adoption)
- [Principles](#principles)

---

## Milestones

| Milestone | Theme | Status | Tasks |
| --- | --- | --- | :---: |
| v0.1–v0.4 | Core checks, reporting and drill records | ✅ Released | — |
| [v0.4.1](#v041-maintenance) | Maintenance | ✅ Complete (4/4 merged; unreleased) | 4 |
| [v0.5](#v05-real-world-data) | Real-world data | ✅ Complete (10/10 merged; unreleased) | 10 |
| [v0.6](#v06-ci-integration-and-developer-experience) | CI integration and developer experience | ✅ Complete (7/7 merged; unreleased) | 7 |
| [v0.9](#v09-documentation-and-api-freeze) | Documentation and API freeze | ✅ Complete (6/6 merged; unreleased) | 6 |
| [Before v1.0](#packaging-and-release-automation) | Packaging and release automation | In progress (3/6 merged) | 6 |
| [v1.0](#v10-stable-release) | Stable release | Planned | 5 |

**38 tasks: 30 complete, 8 planned.** Completed work is merged; v0.4.1 is not released yet.

Full task details, including acceptance criteria and dependencies, are in [`roadmap/issues.yml`](roadmap/issues.yml). Contributor rules, the release checklist and earlier release notes are in the [working guide](roadmap/README.md).

---

## v0.4.1: Maintenance

Finish the maintenance work before the next release.

**Status: complete (4/4 merged).** Windows locking, dependency updates, metadata checks and Action input self-tests are on `main`. v0.4.1 remains unreleased.

| ID | Task | Status |
| --- | --- | --- |
| `M0-1` | Windows locking and release documentation | ✅ Complete — [#9](https://github.com/chriswayneh/resilint/pull/9) |
| `M0-2` | Dependency updates | ✅ Complete — [#2](https://github.com/chriswayneh/resilint/pull/2), [#3](https://github.com/chriswayneh/resilint/pull/3), [#4](https://github.com/chriswayneh/resilint/pull/4) |
| `M0-3` | Version and documentation sync checks | ✅ Complete — [#12](https://github.com/chriswayneh/resilint/pull/12) |
| `M0-4` | Action format description and input validation | ✅ Complete — [#14](https://github.com/chriswayneh/resilint/pull/14) |

---

## v0.5: Real-world data

Make large, messy vendor registers easier to validate and adopt.

**Status: complete (10/10 merged).** Test hardening, CSV/schema support, stable diagnostics, rule configuration, baselines and platform parity are in place. **Next: `P-3`**, release provenance and SBOM.

| ID | Task | Status |
| --- | --- | --- |
| `H-1` | Split tests by module | ✅ Complete — [#16](https://github.com/chriswayneh/resilint/pull/16) |
| `H-2` | Coverage gate | ✅ Complete — [#18](https://github.com/chriswayneh/resilint/pull/18) |
| `H-3` | Property/fuzz tests for loader | ✅ Complete — [#20](https://github.com/chriswayneh/resilint/pull/20) |
| `H-4` | Large-register performance | ✅ Complete — [#22](https://github.com/chriswayneh/resilint/pull/22) |
| `H-5` | CSV robustness | ✅ Complete — [#24](https://github.com/chriswayneh/resilint/pull/24) |
| `H-6` | Published JSON Schema for the register | ✅ Complete — [#26](https://github.com/chriswayneh/resilint/pull/26) |
| `H-7` | Stable error messages and codes | ✅ Complete — [#28](https://github.com/chriswayneh/resilint/pull/28) |
| `H-8` | Rule config file | ✅ Complete — [#29](https://github.com/chriswayneh/resilint/pull/29) |
| `H-9` | Baseline mode | ✅ Complete — [#30](https://github.com/chriswayneh/resilint/pull/30) |
| `H-10` | Windows/macOS CLI parity | ✅ Complete — [#31](https://github.com/chriswayneh/resilint/pull/31) |

---

## v0.6: CI integration and developer experience

Make the CLI easier to use in everyday development and CI workflows.

| ID | Task |
| --- | --- |
| `C-1` | Action outputs ✅ — [#32](https://github.com/chriswayneh/resilint/pull/32) |
| `C-2` | SARIF upload example workflow ✅ — [#33](https://github.com/chriswayneh/resilint/pull/33) |
| `C-3` | Action self-test workflow ✅ — [#34](https://github.com/chriswayneh/resilint/pull/34) |
| `C-4` | pre-commit hook ✅ — [#35](https://github.com/chriswayneh/resilint/pull/35) |
| `C-5` | GitLab CI / generic CI recipe ✅ — [#36](https://github.com/chriswayneh/resilint/pull/36) |
| `C-6` | `resilint init` ✅ — [#37](https://github.com/chriswayneh/resilint/pull/37) |
| `C-7` | `resilint explain RLxxx` ✅ — [#38](https://github.com/chriswayneh/resilint/pull/38) |

---

## v0.9: Documentation and API freeze

Document the supported interfaces and settle the compatibility contract.

| ID | Task |
| --- | --- |
| `D-1` | `docs/` site content ✅ — [#39](https://github.com/chriswayneh/resilint/pull/39) |
| `D-2` | Stability policy ✅ — [#40](https://github.com/chriswayneh/resilint/pull/40) |
| `D-3` | JSON output schema + snapshot tests ✅ — [#42](https://github.com/chriswayneh/resilint/pull/42) |
| `D-4` | Legal disclaimer consistency ✅ — [#41](https://github.com/chriswayneh/resilint/pull/41) |
| `D-5` | Deprecate/remove anything not in the freeze ✅ — [#44](https://github.com/chriswayneh/resilint/pull/44) |
| `D-6` | CONTRIBUTING + issue/PR templates ✅ — [#45](https://github.com/chriswayneh/resilint/pull/45) |

---

## Packaging and release automation

Build, verify and publish reproducible release artifacts before v1.0.

| ID | Task |
| --- | --- |
| `P-1` | Build sdist/wheel in CI ✅ — [#46](https://github.com/chriswayneh/resilint/pull/46) |
| `P-2` | Release workflow (PyPI Trusted Publishing) ✅ — [#47](https://github.com/chriswayneh/resilint/pull/47) |
| `P-3` | Provenance + SBOM |
| `P-4` | Security scanning in CI |
| `P-5` | Action version tags policy ✅ — [#48](https://github.com/chriswayneh/resilint/pull/48) |
| `P-6` | Install docs switch to PyPI |

**Maintainer setup:** PyPI and the protected publishing environment are configured by the maintainer (`P-2`).

---

## v1.0: Stable release

Prove the release candidate works from a fresh install, then complete the final reviews.

| ID | Task |
| --- | --- |
| `R-1` | v1.0.0-rc1 PR (version bump + CHANGELOG) |
| `R-2` | Dogfood on a realistic synthetic register |
| `R-3` | Fresh-machine install test |
| `R-4` | Final review and security review of the full diff since v0.4.0 |
| `R-5` | Tag `v1.0.0` + release (maintainer only) |

**Maintainer only:** tags and releases are created by the maintainer (`R-5`), after the [release checklist](roadmap/README.md#release-checklist) is complete.

---

## Governance adoption

This governance task is tracked separately from the original 38 v1 product tasks; it does not expand the product release scope.

| ID | Task | Status |
| --- | --- | --- |
| `ADOPT-01` | Adopt the documented AI-DLC workflow and truthful stage audit | ✅ Complete on merge — [#43](https://github.com/chriswayneh/resilint/pull/43) |

See the [design](aidlc-docs/inception/adopt-01-design.md), [execution plan](aidlc-docs/inception/adopt-01-plan.md) and [audit](aidlc-docs/audit.md).

---

## Principles

- Run locally and offline: no network calls, vendor contact, scraping, hosted SaaS or telemetry.
- Check recorded commitments; do not add vendor questionnaires.
- Use fictional data only in examples and tests.
- Keep each task in a small PR, with its acceptance criteria verified before merge.
