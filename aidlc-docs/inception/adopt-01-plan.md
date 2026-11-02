# ADOPT-01 execution plan

Status: local construction authorized by the user’s explicit approval of this plan; publication and reserved GitHub actions remain separate.

1. Preserve the current D-3 PR, all prepared branches and uncommitted files. No cleanup, permission changes or retry of another task's denied access operation.
2. Obtain actual approval of this exact repository-specific scope from the user or dot under delegated authority. Append the actual actor, date/time, artifact identity, decision, conditions and next permitted action to the audit before advancing. Generic review is not repository-specific approval.
3. After construction authorization, select a separate adoption branch from a verified user-approved base. Do not modify or bundle D-3 or release drafts. Resolve the public staging boundary before copying local audit content.
4. Implement only the six documentation changes in adopt-01-design.md. Record ADOPT-01 separately from the original v1 product tasks. Keep it planned until user merge.
5. Inspect the complete diff for scope and consistency. Check all local Markdown links/anchors, required policy clauses, roadmap parsing/counts and audit attribution. Inspect staged content for private paths, internal identifiers, transcripts, secrets and personal data. Do not publish raw local audit records.
6. Run the repository-required gates: ruff check ., mypy src, pytest -q, python scripts/check_links.py and git diff --check. Record actual results and justified skips. Retain hosted platform coverage and Action self-tests. Add packaging/security checks only if already required by the selected base; this task does not change CI.
7. Perform and record exact-head security review of the documentation diff: no new execution, network behavior, dependencies, permissions or real data; no unsafe instructions or weakened gates. Resolve findings before presentation.
8. Return the reviewed diff and evidence to dot for the implementation-stage decision. Only after separate publication authorization may a single ADOPT-01 PR be opened. The user performs GitHub approval/merge; no tag or release follows from adoption.

Stop conditions: missing repository-stage review, unresolved staging/privacy boundary, unexpected worktree changes, failed checks or security findings. Preserve evidence and request the specific missing decision; do not route around a denial. Revert only newly introduced adoption changes through an explicitly reviewed ordinary change if needed; never rewrite history or remove pre-existing files.

Inception evidence: existing workspace reads and local inception writes succeeded without additional access. Subsequent user approval authorized local construction; its validation and presentation are recorded in the audit.
