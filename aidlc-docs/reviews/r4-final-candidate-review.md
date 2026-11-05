# R-4 final v1 candidate change review

## Scope and result

The immutable review covered v0.4.0 `7e1a9f95169286afd64879a8fa6ccbcf66e89ccd` through accepted candidate-validation head `51656c048bc7aac8239c8c2352e4ff22bf23f51e`. All 136 changed paths were reviewed, including the deleted baseline test file: 32 primary source files and 104 supporting tests, synthetic fixtures, documentation, policy and static assets. The reviewed package source, packaged starter and license match published rc1 source `a9795f888646708228316ec294509f557875d187`.

The app-backed security diff review completed on 2026-11-05 at 05:04:23 UTC with complete coverage, zero reportable findings and no deferred source-review items. A fresh repository threat model and independent architecture review preceded non-overlapping file review. Capability preflight passed. The original authoritative scan, canonical model, candidate disposition, coverage, report and SARIF are retained locally; public records omit private storage paths and coordination identifiers.

## Evaluated release-index concern

One candidate concerned `.github/workflows/release.yml:161`: the legacy tag-release verification job installs a version from TestPyPI without binding its bytes to the reviewed build before executing it. The version and quick-start assertions are self-reported by installed code.

Static validation confirmed that behavior, then suppressed the candidate under the security policy because exploitation requires privileged TestPyPI project publication and no meaningful privilege escalation or downstream artifact substitution was established. The verification job has read-only contents authority, no declared secrets or OIDC, no persisted checkout credentials, synthetic inputs, no outputs and no artifact upload. Signing precedes it in a separate job. Protected production publication consumes original build artifacts, and GitHub release attachment additionally verifies checksums and signed source/workflow identity. No speculative cross-job artifact-token attack is asserted.

This remains a validation-hardening opportunity. For stable release acceptance, additionally require the independent source-bound index-install matrix on all three platforms before approving production publication. That verifier inspects wheel members, package/resource/license bytes, metadata and RECORD before installing and executing the project.

## Supporting evidence and limits

- Actual rc1 release run 41967446442 passed build, signing, TestPyPI publication, index quick start and GitHub prerelease attachment; production PyPI was skipped correctly.
- R-3 PR #60 passed all 31 final-head checks, including actual source-bound TestPyPI installation on Linux, Windows and macOS. Published manifest subjects and provenance were independently verified.
- Runtime review traced bounded safe parsing, schema/config/baseline trust, output protection and privacy, drill locking/atomic replacement, report escaping, CSV formula protection and computed Action outputs. CI/release review traced least privilege, pinned actions, locks, secret/dependency controls and source identity.
- Static review is not an exhaustive proof of absence of vulnerabilities. Trusted output parents, existing ordinary-file permissions and Windows ACL limits remain documented. External account/runner configuration and arbitrary provider compromise were not audited. No new adversarial runtime package execution was needed to resolve the privileged-precondition candidate.
- The scan host reported 25,089,566 total tokens, including 24,452,480 cached input tokens; these are measured rollout-aggregate counters, not a cost estimate.

R-4 acceptance is supported for this immutable range. R-5 still requires the stable metadata delta review, final local/hosted gates, immutable tag, real protected index publication, three-platform install validation, public asset/provenance verification and stable Action alias. See the [release checklist](../../roadmap/README.md#release-checklist).
