# Project working instructions

Read applicable ancestor/root/nested AGENTS.md, ROADMAP.md and aidlc-docs/ before substantive work. Record missing guidance. Preserve existing work, history and the user's latest scope; v1 is the current product target and later versions are deferred.

## Development stages

1. Establish a repository-specific technical design and execution plan in aidlc-docs/inception/ before implementation.
2. Record each stage decision and actual approval in aidlc-docs/audit.md before advancing. Identify time, actor, task, artifact/commit, decision, conditions, evidence and next permitted action. Never invent or backdate approval.
3. Dot may review routine design and implementation stages under the user's delegation. Attribute that review to dot, not to the user. Record personal user approval only when the user actually supplies it. Material scope changes return to design review.
4. Implement modular changes with exactly one roadmap task per PR. Preserve the acceptance criteria and document behavior changes in the same task.
5. Complete comprehensive tests relevant to the acceptance criteria and the existing repository gates. Review the complete exact-head diff for security before presenting code; resolve blocking findings and state remaining limitations.

GitHub PR approval, merging, tagging, release publication, force-pushing, rebasing and repository visibility/settings remain with the user. Do not change permissions or bypass a denied operation. A routine stage approval does not authorize reserved actions. Publication of an adoption PR requires its separate authorization.

## Continuous security checks

Review secrets, input validation, least privilege, injection and dependency safety. Use synthetic fixtures only; never commit real vendor records, PHI, PII or credentials. Preserve safe parsing, size limits and output protections. Use parameterized queries and allowlisted identifiers if SQL is ever introduced; explain when a control is inapplicable rather than inventing tests. Keep the CLI offline: no vendor contact, scraping, SaaS or telemetry.

Public workflow records must exclude machine inventory, private paths, raw transcripts, internal coordination identifiers and personal details. Review explicit staged paths; never stage local planning directories wholesale.

## Verification and efficiency

Follow the [working guide](roadmap/README.md) and [workflow records](aidlc-docs/README.md). Required local gates are `ruff check .`, `mypy src`, `pytest -q`, `python scripts/check_links.py` and `git diff --check`. Hosted coverage, platform and Action checks remain required; local results do not replace them.

Prefer `rg` for scoped searches. Keep routine output compact, batch independent reads, reuse verified evidence and stop when the authorized outcome is verified. When RTK is available, read the user's supplied local RTK guidance and use it for supported routine Git/test summaries. Use native unfiltered tools for complete source, exact evidence and security review. Do not install hooks or change telemetry settings by inference.

## Communication

Dot owns consolidated proactive user notifications. Keep progress, results, blockers and requests in the existing working thread for dot to read. Do not duplicate those updates through proactive phone, main-chat or email messages, invent a messaging API, or create a notification mechanism. Normal answers in the working thread, required approval cards, app/account notifications and security prompts remain available. This rule grants no additional work or publication authority.
