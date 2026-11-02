# Roadmap

Where resilint is going, and what is ready to work on.

**Current release:** [v0.4.0](https://github.com/chriswayneh/resilint/releases/tag/v0.4.0). **Next release:** v0.4.1 maintenance. Milestones and scope may change.

- [Milestones](#milestones)
- [v0.4.1: Maintenance](#v041-maintenance)
- [v0.5: Real-world data](#v05-real-world-data)
- [v0.6: CI integration and developer experience](#v06-ci-integration-and-developer-experience)
- [v0.9: Documentation and API freeze](#v09-documentation-and-api-freeze)
- [Packaging and release automation](#packaging-and-release-automation)
- [v1.0: Stable release](#v10-stable-release)
- [Principles](#principles)

---

## Milestones

| Milestone | Theme | Status | Tasks |
| --- | --- | --- | :---: |
| v0.1–v0.4 | Core checks, reporting and drill records | ✅ Released | — |
| [v0.4.1](#v041-maintenance) | Maintenance | ✅ Complete (4/4 merged; unreleased) | 4 |
| [v0.5](#v05-real-world-data) | Real-world data | ✅ Complete (10/10 merged; unreleased) | 10 |
| [v0.6](#v06-ci-integration-and-developer-experience) | CI integration and developer experience | In progress (2/7 merged) | 7 |
| [v0.9](#v09-documentation-and-api-freeze) | Documentation and API freeze | Planned | 6 |
| [Before v1.0](#packaging-and-release-automation) | Packaging and release automation | Planned | 6 |
| [v1.0](#v10-stable-release) | Stable release | Planned | 5 |

**38 tasks: 16 complete, 22 planned.** Completed work is merged; v0.4.1 is not released yet.

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

**Status: complete (10/10 merged).** Test hardening, CSV/schema support, stable diagnostics, rule configuration, baselines and platform parity are in place. **Next: `C-3`**, hosted Action self-test.

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
| `C-3` | Action self-test workflow |
| `C-4` | pre-commit hook |
| `C-5` | GitLab CI / generic CI recipe |
| `C-6` | `resilint init` |
| `C-7` | `resilint explain RLxxx` |

---

## v0.9: Documentation and API freeze

Document the supported interfaces and settle the compatibility contract.

| ID | Task |
| --- | --- |
| `D-1` | `docs/` site content |
| `D-2` | Stability policy |
| `D-3` | JSON output schema + snapshot tests |
| `D-4` | Legal disclaimer consistency |
| `D-5` | Deprecate/remove anything not in the freeze |
| `D-6` | CONTRIBUTING + issue/PR templates |

---

## Packaging and release automation

Build, verify and publish reproducible release artifacts before v1.0.

| ID | Task |
| --- | --- |
| `P-1` | Build sdist/wheel in CI |
| `P-2` | Release workflow (PyPI Trusted Publishing) |
| `P-3` | Provenance + SBOM |
| `P-4` | Security scanning in CI |
| `P-5` | Action version tags policy |
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

## Principles

- Run locally and offline: no network calls, vendor contact, scraping, hosted SaaS or telemetry.
- Check recorded commitments; do not add vendor questionnaires.
- Use fictional data only in examples and tests.
- Keep each task in a small PR, with its acceptance criteria verified before merge.
