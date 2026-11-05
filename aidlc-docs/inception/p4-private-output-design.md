# P-4 follow-up: private output defaults

## Scope, evidence and authority

Base main: `07d90c5f8c380b2aff9cddee64c26e4dd0616414`, after [presentation PR #56](https://github.com/chriswayneh/resilint/pull/56) passed all 28 hosted checks and merged. The user explicitly resumed work toward v1 after formatting; earlier authority covers the v1 fixes and passing merges. Codex records its own design decision, not an independent or personal user design approval.

The completed static investigation of main `ed501a9ddc9f8e55f3a045ccad6a9aee733a1dd9` confirmed CodeQL alerts #3 and #1: explicit drill-log chmod 0644 and new report/export creation mode 0644 can expose sensitive operator data to other local POSIX users with directory traversal access. The empty production/test lock sidecars (#2/#4) contain no sensitive payload for the supplied disclosure claim; align their defaults as defense in depth. No alert dismissal or actual incident is asserted.

Root SECURITY.md covers candidate issues and local output commands; no scoped policy applies. Existing symlink, root, input-identity, size and parser guards stay intact. Trusted parent directories remain a documented assumption.

## Technical design and execution

One P-4 follow-up PR changes file-creation modes from 0644 to 0600 in write_file and _lock, and makes atomic drill replacement chmod 0600 instead of widening its private temporary file. Align the empty-lock test fixture. No permissions are added; intentional cross-user sharing requires the operator's explicit action.

New report/baseline/export/starter files default to owner-only access where POSIX modes apply. Normal writes to pre-existing report/export files retain the operator-selected inode permissions; they are not retroactively made private. Drill replacement always installs a private new inode, including when replacing an existing private or shared log. Document both distinctions, the trusted-parent assumption and Windows ACL limitations in usage/drill docs and an Unreleased security changelog entry.

Before implementation record actual scope/design authority in the audit. Add focused real-filesystem POSIX regressions under umask 022 for each public writer, existing-output mode preservation, and new/existing drill logs under umasks 022/077. Every umask change must restore the previous value even on assertion failure. Use synthetic fixtures, preserve input bytes and retain all existing lock/concurrency/error tests. POSIX permission assertions skip on Windows because those bits cannot verify its ACLs.

Complete Ruff, mypy, full pytest, links and whitespace; inspect the complete exact-head security diff. Require all hosted platform/coverage, package, Action, scanner, CodeQL and release-evidence checks on the PR head. After ordinary accepted merge, inspect the full main analysis/alert state rather than treating zero-new-result PR output as a clean repository. Do not tag the candidate before that succeeds.

Runtime dependency, workflow, version, account/settings and original roadmap acceptance/counts are unchanged. No SQL or network paths are introduced; SQL parameterization is inapplicable. Existing branches, partial R-2/R-3 work and original drafts/artifacts remain preserved. Subsequent R-2/R-3/R-4/R-5 work remains separate.
