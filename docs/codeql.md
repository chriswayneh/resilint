# Python CodeQL analysis

The [CodeQL workflow](../.github/workflows/codeql.yml) completes the Python-analysis part of P-4 alongside the separate [secret/dependency scanners](security-ci.md). Local tests alone do not establish hosted analysis or task completion.

## Analysis and transmission boundary

The job runs on main pushes and ordinary PR events, including ready-for-review. It uses SHA-pinned checkout and CodeQL actions, disables checkout credential persistence, analyzes Python without an application build/install, and uses the security-extended suite bundled with the linked CodeQL tools. The pinned action's defaults select bundle 2.27.4. Changing that action pin requires review of the linked tools and queries as well as the JavaScript action.

The workflow defaults to contents read. Only the Python analysis job receives security-events write to submit SARIF to this repository's GitHub code scanning. The submission may include source snippets, repository-relative locations, findings, fingerprints and diagnostic/analysis metadata. Results may be visible in public PR and code-scanning views. GitHub also receives ordinary job logs and the action's operational metadata. No vendor register or private account data is intentionally supplied.

Database upload and dependency caching are explicitly disabled. No environment credentials, secrets, OIDC, PR comments, custom query repositories or additional report artifacts are configured. Disabling database upload does not remove SARIF or operational-metadata transmission. Fork permissions and runner approvals stay under GitHub's existing policy; no privileged PR-target event or access-policy workaround is used.

## Verification and limitations

Run the normal contributor gates and inspect the workflow's complete diff. Regression checks verify permission isolation, pinned actions, bundle selection, absence of application run steps and explicit database-upload disabling. They do not execute CodeQL or prove the service accepts a fork's upload. Real hosted analysis, successful SARIF processing and review of actual findings are required before P-4 is complete. Analysis success is not a claim that the project has no vulnerabilities.

The existing scanner-control lane remains mandatory and unchanged. Future workflow or query changes require the same security and data-handling review. This job does not activate GitHub default setup, change repository settings or widen persistent account access.
