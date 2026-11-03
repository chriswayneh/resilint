# D-6 execution plan

1. Record actual routine approval of the [design](d6-contributor-design.md) before reconciling the pre-existing draft. Preserve existing branches, local records and all generated artifacts.
2. Bring reviewed merged main into the D-6 branch without rewriting history. Do not include unmerged D-5 changes in a D-6 PR; wait for D-5 or isolate only the existing D-6 commit on an authorized base.
3. Reconcile CONTRIBUTING wording with adopted policy and add workflow/AGENTS links. Retain existing setup, gates, security reporting and fictional-data requirements. Review templates and the README/changelog additions as one D-6 task.
4. Validate template frontmatter and links, gate-command coverage, policy consistency and public privacy. Run Ruff, mypy, full pytest, link checks and git diff --check; retain hosted coverage/platform/Action gates.
5. Review the complete exact-head diff for security and scope, record evidence, and present one PR for actual implementation-stage review. No formal GitHub approval is submitted on anyone's behalf.
6. Advance only after stage review and exact-head CI pass, checking any user merge/publication authorization and its expiry at action time. Update only D-6 completion metadata, effective on merge.

Rollback: correct or withdraw only D-6 documentation changes through ordinary commits. Preserve existing user work and history. No cleanup, access/settings changes, force-push, rebase, tag or release is part of D-6.
