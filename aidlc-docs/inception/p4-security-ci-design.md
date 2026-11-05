# P-4 security CI technical design

Status: inception proposal only. No construction, push, scanner execution, privileged upload or settings change is authorized. Live main is unchanged at 0c82503ce1fa737276be6c70c0230335c8b8406f. Main has 28/38 completed tasks; PRs #47 and #48 remain separate drafts. Read AGENTS, roadmap/working guide and actual audit records. P-4 has no declared dependencies. Preserve draft 7f38e941ddd535cbddebace13c0cfe1211802c2f as reference only; its inherited history must not be published.

## Observations and access limits

Read-only GitHub responses show a public repository, Actions enabled with all actions allowed, default CodeQL setup not-configured, and native secret scanning/push protection enabled. Listing code-scanning analyses returned HTTP 404, no analysis found; this is not evidence of zero vulnerabilities. The workflow-permissions endpoint emitted a missing admin:repo_hook scope warning alongside a read-default/no-PR-approval body. Treat that configuration as incompletely verified. Do not refresh scopes, retry the restricted query or change settings. Fork approval settings and advanced-upload eligibility have not been proved. Public visibility and Actions availability satisfy documented general eligibility, not an actual upload test. No default-setup toggle is proposed.

## Proposed files and delivery boundary

After approval, isolate P-4 on a new main-based branch, leaving all original branches, stash, generated artifacts and private records unchanged. Proposed files: .github/workflows/security.yml; requirements-security-lock.txt for scanner tooling; scripts/check_security_lock.py and tests/test_security_ci.py; docs/security-ci.md; CONTRIBUTING.md; CHANGELOG.md; P-4 inception/audit records. Roadmap metadata changes only when acceptance is genuinely fulfilled. Runtime requirements-lock.txt, application dependencies/version and unrelated task definitions stay unchanged.

Recommended staged delivery: first prepare and independently review secret/dependency checks with read-only tokens. Keep CodeQL's privileged configuration as documentation until specific activation confirmation and remaining evidence are resolved. P-4 stays planned if CodeQL is deferred. A future approved full implementation can include CodeQL, but merely pushing a workflow on pull_request can execute it; draft status is not an execution barrier. No workflow is constructed or pushed under this inception request.

## Triggers, trust and permissions

Propose push on main only and pull_request targeting main (opened, synchronize, reopened, ready_for_review). No tags, schedule, workflow_dispatch, pull_request_target or workflow_run bridge. Use GitHub-hosted Ubuntu, separate jobs, 10-minute secret/dependency timeouts and a 20-minute CodeQL timeout. Default token contents: read; no secrets, PAT, OIDC, environment credentials, comments or repository writes. SHA-pin actions and disable checkout credential persistence. Pass event values through quoted environment variables if needed, never direct shell interpolation.

Treat fork and same-repository PR content as untrusted. No application install, build, tests or repository hooks in scanner jobs. Existing CI independently executes tests; this proposal does not change it. Scanner parsers still consume adversarial files and have residual vulnerability risk. Workflow/tool-lock changes themselves need exact-diff review; a malicious replacement workflow cannot be made trustworthy by tests inside that same PR. Honor existing fork approval requirements; do not change settings or elevate a fork token. If upload is unavailable, report it instead of adding secrets or switching events.

## Secret scanner

Use Gitleaks 8.30.1, full fetched Git history with git --log-opts=--all and --redact=100. Scope is reachable history actually fetched, not deleted/unreachable server objects. Force an explicit reviewed default-rule configuration so repository auto-discovery cannot silently suppress checks; configuration/ignore changes require review. Do not enable verbose diagnostics, reports, PR comments or artifact uploads. Output can still reveal file paths, commit metadata and finding descriptions; redaction is not a confidentiality guarantee. Only synthetic leak fixtures may be used for validation.

Official release API verified Linux archive SHA-256: 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb. Verify before extraction/execution; checksum mismatch fails closed. Default rules are version-bound; explicitly supplied rules must have reviewed provenance. Do not suppress historical findings merely to obtain green CI.

## Dependency scanner

Audit the existing runtime lock, currently PyYAML 6.0.3 with SHA-256 hashes. Use pip-audit 2.10.1 with --require-hashes --disable-pip --no-deps and explicit PyPI advisory service. Before audit, validate a constrained lock grammar: exact named versions and SHA-256 continuations only; reject URLs, VCS/editable/local paths, nested requirements/constraints, index/options and malformed or missing hashes. This prevents the proposed audit path from resolving/installing PR-supplied packages. Validate compatibility of these options with the pinned tool before accepting implementation.

Install scanner tooling separately from application code with a dedicated complete hash-locked tool dependency file, wheels only, from PyPI; fail if a wheel or verified hash is missing. Exact transitive tool pins/hashes are not prepared yet and are a construction verification requirement. They must not be sourced from unreviewed PR instructions. pip-audit's upstream security model warns that ordinary resolution can execute package code; hashes alone do not make malicious packages safe. With resolution disabled, coverage is exactly the explicit complete runtime lock, not every development/build dependency or undisclosed vulnerability. PyPI receives package names/versions and network metadata. No --fix, extra index, advisory upload report or automatic dependency changes.

## CodeQL proposal and activation gate

Candidate action pins: checkout 3d3c42e5aac5ba805825da76410c181273ba90b1; setup-python 6d4fd22b20465ccc0f7354476588e8df7c9ca0e0; CodeQL init/analyze 9b3254085494b55a0f7c4c2b3d2d52cc712ce370. Python source analysis uses build-mode none and built-in security-extended queries; no autobuild, application execution, custom PR queries or dependency installation. Scan repository Python source including tests/scripts; omit only generated/cache directories with reviewed configuration. Disable dependency caching. The action selects a recommended CodeQL bundle by default, so an action SHA alone does not pin every downloaded component. Resolve a verified bundle version/digest and query provenance before full implementation; do not claim all tools immutable while this is unknown.

The reference draft requests contents: read, actions: read and security-events: write in CodeQL only. Determine whether actions: read is necessary for this public repository and omit it unless evidenced. No other job gets write permission. Fork token restrictions and upload support require verification against the final configuration; no privileged fallback.

Pinned analyze/action.yml defaults to upload: always and upload-database: true; add-snippets is deprecated and has no effect. Proposed privileged mode explicitly disables database upload and uploads successful SARIF only. SARIF sent to GitHub code scanning includes findings, rules, source locations/data-flow information, run/tool metadata and potentially source snippets/diagnostics; do not promise snippet removal. Actions also exposes execution logs/status metadata to GitHub. Full alert summaries require write access; PR annotations are visible to readers of this public repository. Database bundles contain source copies and can be distributed via GitHub's database service, hence upload-database: false is required. No separate debug/SARIF/database artifact upload. Exact residual action diagnostics/telemetry behavior and payload fields remain to be verified before activation; no claim that disabling database upload stops all outbound metadata.

Specific user-only activation decision: permit the reviewed security workflow in chriswayneh/resilint to execute CodeQL with job-scoped security-events: write and send SARIF to GitHub code scanning, with public PR annotations possible and database uploads disabled. This is an operational permission/data-publication decision before the first executing push/PR, not routine inception approval. No new persistent PAT/trust is proposed; any later service setting, access expansion or fork-policy change requires separate concrete authorization. Keep this mode unenabled until confirmed.

Alternatives: (A) recommended read-only secret/dependency checks first, CodeQL deferred and P-4 incomplete; (B) after separate confirmation, full CodeQL upload mode with reviewed payload/permissions; (C) separately reviewed local CodeQL analysis with no service upload, useful evidence but not proof of hosted code-scanning acceptance. Do not treat upload: never alone as a guarantee of zero action telemetry.

## Acceptance and review

Require synthetic positive/negative secret tests, full-history detection of a removed synthetic secret, redaction inspection, checksum-failure handling, lock-grammar rejection tests and no-resolution audit behavior. Test clean/vulnerable/offline advisory outcomes without relying exclusively on changing live advisory data. Verify triggers, action pins, permissions, no application execution, no secret/report artifacts and the chosen CodeQL mode structurally. Real scanner results must be distinguished from mocked failure-path tests. Full local gates and all existing exact-head hosted coverage/platform/package/Action gates remain required; no skipped CodeQL job counts as completion. Review actual CodeQL alerts, not just execution success.

Return complete immutable diff and evidence for independent implementation/security review. Keep original 38 task definitions/governance intact. No release, tag, merge, settings change or cleanup. Rollback uses ordinary reviewed commits only; existing uploads cannot be assumed erased by reverting code.

## Primary evidence

- [Pinned CodeQL analyze inputs](https://github.com/github/codeql-action/blob/9b3254085494b55a0f7c4c2b3d2d52cc712ce370/analyze/action.yml) and [init inputs](https://github.com/github/codeql-action/blob/9b3254085494b55a0f7c4c2b3d2d52cc712ce370/init/action.yml).
- [pip-audit 2.10.1 options/security model](https://github.com/pypa/pip-audit/blob/v2.10.1/README.md).
- [Gitleaks 8.30.1 options](https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md) and [release assets](https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1).
- [Code-scanning eligibility](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/configure-code-scanning/configure-code-scanning), [alert visibility](https://docs.github.com/en/code-security/how-tos/manage-security-alerts/manage-code-scanning-alerts/assess-alerts), [database source contents](https://docs.github.com/en/code-security/how-tos/find-and-fix-code-vulnerabilities/scan-from-the-command-line/create-database-bundles), and [workflow permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).

See [execution plan](p4-security-ci-plan.md).
