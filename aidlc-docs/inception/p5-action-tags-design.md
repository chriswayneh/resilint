# P-5 Action tag-policy technical design

Status: proposed inception only; construction, push and PR publication are not approved by this document. v1 is the sole product scope. Live remote main was verified unchanged at 0c82503ce1fa737276be6c70c0230335c8b8406f before preparation. Recheck the base before any authorized construction.

## Prerequisite and evidence

P-5 depends only on D-2, completed in PR #40 and present on the verified main. Its acceptance is documentation of the moving @v1 alias, immutable @v1.0.0 release reference and full-SHA pinning advice. The existing draft commit 702b118cb198c839af4dd781ccd62cb68318511b supplies proposed prose, not stage approval. Its branch also contains unmerged P-2/P-3/P-4 history and must not be published or merged as this task.

Applicable guidance: AGENTS.md, ROADMAP.md, roadmap/README.md, aidlc-docs/README.md and actual audit decisions. Separate task-specific design and execution-plan artifacts are now proposed; no approval is invented or backdated.

## Documentation design

Add an Action version-tags section to docs/stability.md and a short README link. Explain three references: a FUTURE @v1 alias tracking reviewed stable v1 releases only; an exact release reference such as @v1.0.0 kept immutable under project policy; and a full 40-character commit SHA for deliberate adoption. The future alias must not point to a release candidate or another major version. First stable publication and the existing release checklist precede any alias creation.

State that these future references are planned, not currently available. Keep existing usable examples and current release/version statements unchanged. Explain that a SHA pins this repository's code, not runners, network services or every transitive dependency. New minor-version rules may produce new findings, so users should review release notes before updating a pinned reference.

Use the existing roadmap/README.md release-checklist anchor. Do not link to unmerged docs/releasing.md or claim that a deployed release workflow ignores the alias. P-2 remains a separate draft. The policy describes intended behavior and grants no operational authorization; creating or moving tags remains subject to actual user authorization and release gates.

## Files and isolation

Allowed files: README.md, docs/stability.md, CHANGELOG.md, aidlc-docs/inception/p5-action-tags-design.md, aidlc-docs/inception/p5-action-tags-plan.md, P-5 entries appended to aidlc-docs/audit.md, and prospective P-5 metadata in ROADMAP.md and roadmap/issues.yml. Do not alter other task definitions, statuses or governance records. Completion is effective only on merge; no version is marked released. On the verified base, P-5 completion would produce 29/38 complete, but recalculate against the actual reviewed base instead of hardcoding.

After approval, create a separate branch from the reverified main and apply only the three-file P-5 prose change as a starting point, then reconcile it to this design. Do not merge the inherited P-5 branch or include P-2/P-3/P-4 files/commits. Preserve the original draft chain, stash, generated artifacts, private combined records and existing P-2 branch unchanged.

## Acceptance, validation and risks

Review prose against the three required reference types, future availability, immutability as policy, SHA limits, user-owned actions and the existing stability contract. Check links/anchors and verify no dependency on unmerged P-2 documentation. Compare roadmap YAML to prove only P-5 status/completion reference changes; preserve all 38 original task definitions and separate governance tracking.

Run ruff check ., mypy src, pytest -q, python scripts/check_links.py and git diff --check. Require the current hosted platform/coverage, package and Action checks on the exact PR head; local results do not substitute. No new runtime tests are needed for prose-only changes. Review the complete immutable diff for privacy/security, scope and truthful claims, then obtain separate implementation review.

Primary risks are misleading availability/authorization claims and accidentally bundling inherited workflow changes. Mitigate through future-tense wording, existing checklist links, an isolated main-based branch and an explicit changed-file/commit review. No runtime, workflow, dependency, credential, settings, account/access, tag or publication change is in scope. SQL and executable input-handling changes are inapplicable. Public records must exclude private paths, raw coordination records, secrets, PHI and PII.

See [execution plan](p5-action-tags-plan.md). Material scope changes return to inception review. Removing deadline pressure does not expand or renew any expiring authority.
