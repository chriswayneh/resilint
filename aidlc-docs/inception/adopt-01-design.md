# ADOPT-01 technical design

Status: the user explicitly approved this repository-specific proposal for local construction. See the audit for actual approval attribution; publication remains separate.

## Scope

Adopt the reviewed documentation-only AI-DLC methodology in one separate ADOPT-01 PR. Preserve the existing v1 product roadmap, offline CLI, synthetic-data policy, validation requirements, open PR and prepared work. v2/v3 remain deferred. No runtime, dependency, workflow, permission, account, installation or release changes are included.

## Guidance and current boundary

The supplied AGENTS instructions, ROADMAP.md, roadmap working guide and existing inception/audit records were read. No filesystem AGENTS.md was found in the repository or inspected ancestors. Existing local aidlc-docs records describe release work; preserve their history and do not interpret them as adoption approval. They contain local coordination details and are not ready for public staging.

The last verified main has 24 of the original 38 tasks merged. PR #42 is separate D-3 work with all 20 checks passing at its reviewed head; its branch's 25-task completion count is prospective. Candidate metadata and later release work exist locally but no v1 release has been published. Adoption must not alter those facts or bundle those drafts.

## Proposed construction changes, after review

1. Add root AGENTS.md with the reviewed lifecycle policy. Preserve existing user instructions, including concise output, appropriate RTK use and exact evidence when required.
2. Add a concise README methodology paragraph linking the AWS AI-DLC reference and local workflow index. Describe an adapted documentation workflow; do not claim a native AWS runtime is installed.
3. Add aidlc-docs/README.md describing inception, construction, continuous security checks, audit fields and real approval attribution.
4. Retain repository-specific inception and append-only audit records. Prepare public-safe records without machine inventory, private filesystem paths, raw transcripts, internal worker/chat identifiers, credentials or personal details. Preserve original local records separately through a reviewed staging plan; never blindly stage the existing directory.
5. Add ADOPT-01 to ROADMAP.md and roadmap/issues.yml as a separate planned governance task, outside the original 38-task v1 product denominator. Preserve original task IDs, acceptance criteria, completion history and v1-only scope. Mark adoption complete only after the user merges it.
6. Reconcile conflicting delegated-merge/release wording in the roadmap working guide and any contributor guidance present on the selected base. Preserve all unrelated gates and historical facts. Do not modify prepared branches as part of adoption.

## Authority and security

Before each stage, read applicable guidance, establish the design/plan, and record the decision before advancing. Dot may approve routine design and implementation stages under delegated authority; record dot as the actual reviewer only when that review occurs. Never call it personal user approval. GitHub PR approval, merges, tags, force-pushes, rebases, publication decisions and repository visibility/settings remain user-owned.

Each task has one PR and comprehensive, relevant verification plus exact-head security review before presentation. Review secrets, validated input, least privilege, injection and dependency safety; use synthetic data and never publish PHI or PII. SQL injection is inapplicable to this documentation-only change and the existing file-based CLI; future SQL work requires its own design and parameterized queries. Adoption introduces no execution or dependency changes.

## Acceptance and limits

All new relative links and heading anchors resolve; lifecycle/authority clauses are consistent across files; the roadmap's existing product counts remain accurate; no private material is staged; only adoption documentation appears in the PR. Existing lint/type/test/diff and hosted coverage/platform/Action checks remain required. Documentation checks do not replace those gates. No retrospective approvals or claims of release readiness are introduced.

Generic adoption-design review was relayed from dot. The user subsequently approved this repository-specific plan directly; no dot approval of this plan is inferred. The cleanup rejection is independent and does not block local inception preparation.
