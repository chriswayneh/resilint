# v1.0.0 release verification

Published stable release: [GitHub v1.0.0](https://github.com/chriswayneh/resilint/releases/tag/v1.0.0), [production PyPI 1.0.0](https://pypi.org/project/resilint/1.0.0/). GitHub publication time: 2026-11-05T05:29:58Z. The stable release is non-draft, non-prerelease and the latest GitHub release.

## Completed release checklist

- [x] Candidate tasks and full-range review accepted; [R-4 review](r4-final-candidate-review.md) covered all 136 changed paths with zero reportable findings. Stable metadata/docs delta received complete incremental security/privacy review.
- [x] Package/runtime/changelog versions agree at 1.0.0; dated stable notes and empty Unreleased sections were prepared before publication, preserving candidate history.
- [x] Local gates passed: Ruff, mypy on 11 modules, 413 tests with 17 documented platform/tool skips, links and whitespace.
- [x] Exact PR #62 head passed 28 checks; merged source main passed all nine platform/coverage jobs, packaging, Action, secret-history, dependency/control, CodeQL and release-evidence gates. Main CodeQL analysis 2100847326 had zero results, 50 rules and no error; open alerts were zero.
- [x] Immutable annotated v1.0.0 was created by Codex under the user's explicit owner delegation, at merged source `d5aa0b6223ed930adc753fe94aa212a9ba686c43`. No tag/history force or settings change.
- [x] Release run [41973668135](https://github.com/chriswayneh/resilint/actions/runs/41973668135) passed build, attest, TestPyPI, index quick start, protected production PyPI and GitHub release attachment. Both normal environment reviews were performed by Codex under actual user delegation, retaining the approval gates.
- [x] Before production approval, [actual source-bound install run 41974046411](https://github.com/chriswayneh/resilint/actions/runs/41974046411) passed Linux, Windows and macOS for exactly 1.0.0 at the stable source. All three installed quick-start markers were verified.
- [x] Downloaded all six public assets. Exact manifest membership/hashes passed; every public asset equals the original signed build/bundle, and all server asset digests agree. Wheel, sdist and SBOM provenance independently passed expected repository, release workflow, immutable tag ref and source commit.
- [x] TestPyPI and production PyPI wheel/sdist digests equal signed build digests. An actual production-index binary wheel was source/resource/license/metadata/RECORD-verified before installation into a fresh isolated environment; installed bytes/version and all four documented outside-checkout commands passed. Expected RL004/RL005/RL008 and unchanged starter bytes were confirmed.
- [x] Initial `v1` Action alias was normally created and remotely verified at the exact published stable source. Alias object `bc03ea338e03ea5cea9c10b939756193d243e57c`; immutable version-tag object `d300609a20512c18d87be3e795dbac26e3f628d8`. Alias-triggered release run 41974697178 was skipped as designed; it did not publish another version.

## Distribution identity

| File | SHA-256 |
| --- | --- |
| resilint-1.0.0-py3-none-any.whl | d8f17f4a164a7a74d5ca3394916b819b21461fed7a49f87930a1e5aa412af185 |
| resilint-1.0.0.tar.gz | 0da9844d042bfd36b396c90bec5455c690515e0c0728bb0a3f1a798932496b7a |

Public assets also include `resilint.cdx.json`, `SHA256SUMS`, `release-notes.md` and `provenance.sigstore.json`. Retained local evidence includes original/public downloads, signature receipts, index digests and actual install outputs. Public records omit private paths, raw transcripts and internal coordination identifiers.

The [v1 stability policy](../../docs/stability.md) now applies. Draft regulatory/RoI mappings, trusted filesystem parents, existing ordinary-file modes, Windows ACL behavior and optional SARIF disclosure keep their documented limits. These finite checks do not guarantee absence of all defects or regulatory compliance. v2/v3 remain deferred.
