# Development workflow records

Resilint uses an adapted documentation workflow informed by [AWS AI-DLC](https://github.com/awslabs/aidlc-workflows). No native AWS runtime is installed or required by this adoption.

Start with [AGENTS.md](../AGENTS.md), the [roadmap](../ROADMAP.md) and its [working guide](../roadmap/README.md).

- Inception: establish task scope, technical design, execution plan, risks and acceptance criteria before implementation.
- Construction: implement the reviewed scope in small modules, one roadmap task per PR, with comprehensive relevant tests and the repository's existing gates.
- Continuous guardrails: review secrets, validated input, least privilege, injection, safe dependencies and synthetic-only data before presenting code.
- Audit: append real stage decisions before advancing, naming the actual reviewer and evidence. Dot's delegated reviews are not personal user approvals. User-owned GitHub approvals, merges, tags, releases and settings remain separate.

ADOPT-01 records: [technical design](inception/adopt-01-design.md), [execution plan](inception/adopt-01-plan.md) and [audit](audit.md). Adoption remains planned until user merge; these records do not approve unrelated product work.

Audit entries identify time, actor, task/stage, artifact or commit, decision and conditions, validation, and the next permitted action. Keep superseded decisions and append corrections. Public records contain sanitized summaries, never private machine details, raw transcripts, internal worker identifiers, secrets, PHI or PII.
