# P-1 execution plan

1. Obtain and record actual routine inception approval of the [design](p1-package-design.md) before reconciling the existing draft. Preserve all branches, existing untracked planning files and generated artifacts.
2. After D-6 is merged, integrate main into ci/P-1-package-build through a normal merge. Resolve documentation additions without losing either side. Do not rewrite history or bundle later packaging drafts.
3. Reconcile only the approved P-1 job, build metadata, generated-file ignore entries and supporting docs. Verify its read-only permission inheritance and exact shell behavior.
4. Run Ruff, mypy, full pytest, Markdown link checks and whitespace checks. Validate workflow syntax. Build sdist/wheel into a fresh temporary directory, Twine-check exactly those artifacts, inspect distribution contents/license metadata and install the new wheel into a fresh venv outside the checkout for version/init/check smoke tests. Do not delete or overwrite retained repository build/dist artifacts.
5. Inspect the complete exact-head patch for secrets, input/shell handling, least privilege, dependencies, offline runtime and public-safe records. Open one P-1 draft PR with truthful validation and prospective task metadata; require all hosted matrix/coverage/Action/package jobs.
6. Return the immutable complete diff and evidence for separate implementation review. Record actual review before advancing; audit-only additions require new-head hosted checks. Merge only with the user's scope and time window valid at action time. This plan grants no publishing or persistent access permission.

Rollback: ordinary reviewed commits limited to P-1 changes. Preserve history, original task definitions, other drafts and generated artifacts. No cleanup, force push, rebase, tag, release or repository settings changes.
