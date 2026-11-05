# P-4 CodeQL continuation: design and execution plan

Status: local preparation under the user's v1 continuation authorization. Activation and SARIF transmission require the specific confirmation described below. No CodeQL completion or hosted execution is claimed.

## Design

Complete the remaining Python-analysis acceptance criterion through a separate CodeQL workflow, preserving the existing three scanner jobs and their controls unchanged. Use main pushes and ordinary PR events; never use pull_request_target, privileged follow-up events, custom query downloads or workflow dispatch.

Pin init/analyze to official github/codeql-action commit 33d7b85da1a04171e211befe2c739303b9a4c066, resolved from v4. Its checked defaults select bundle 2.27.4. Explicit tools: linked ties the CLI and bundled query selection to that action revision; do not claim this replaces an independent audit of the action or release binaries. Use Python build-mode none and the bundled security-extended suite. Do not install the application or execute its setup/build hooks. Disable dependency caching and database uploads.

Default permissions remain contents read. Only the analysis job receives security-events write, for SARIF submission to this repository's GitHub code-scanning service; no id-token, environment, secrets, comments or artifact upload. SARIF can include source snippets, repository-relative paths, findings, fingerprints and diagnostic/analysis metadata. Results may appear in public code-scanning or PR views. Job logs and CodeQL's own operational/diagnostic metadata still reach GitHub; disabling database upload does not eliminate all transmission. Fork permissions and approvals remain platform-controlled; fail or report limitations rather than changing policy.

## Execution and verification

1. Record actual scope/authority before construction. Prepare locally without activating the workflow. Preserve prior audit chronology and the explicit correction of earlier unverified approval claims.
2. Add the separate workflow, boundary documentation and regression checks that keep write permissions isolated, database uploads disabled and action references pinned. Preserve runtime code, locks, examples and presentation.
3. Run Ruff, mypy, full pytest, link/whitespace checks and available workflow validation. Review the complete final diff for secrets, injection, dependency provenance, least privilege and public-record privacy. SQL controls are inapplicable.
4. Before push, obtain specific action-time confirmation to enable job-scoped security-events write and transmit CodeQL SARIF to GitHub. Broad release approval alone is not represented as that confirmation. No default-setup, repository-access or settings mutation is included.
5. After confirmed activation, require successful real hosted analysis and all existing CI/Action/scanner gates on the immutable final commit. Inspect actual findings; process success alone is not a security review. Keep P-4 planned until the missing acceptance evidence is satisfied, updating its roadmap status in the same task PR when justified.
6. Merge only after review and passing gates within actual user authorization. Roll back through ordinary commits; preserve existing worktrees, drafts, artifacts and version history.

References: [pinned init inputs](https://github.com/github/codeql-action/blob/33d7b85da1a04171e211befe2c739303b9a4c066/init/action.yml), [pinned analyze inputs](https://github.com/github/codeql-action/blob/33d7b85da1a04171e211befe2c739303b9a4c066/analyze/action.yml), [pinned bundle defaults](https://github.com/github/codeql-action/blob/33d7b85da1a04171e211befe2c739303b9a4c066/src/defaults.json).
