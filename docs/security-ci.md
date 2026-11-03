# Security CI draft: read-only scanners

This P-4 implementation covers secret and runtime-dependency checks only. CodeQL is deferred, and P-4 remains planned. These files have not yet been authorized for push or hosted execution. A draft PR can execute workflows immediately; local preparation is not activation approval.

## Execution boundary

The proposed workflow runs on pushes to main and pull requests targeting main (opened, synchronize, reopened and ready_for_review), with separate ten-minute Ubuntu jobs. It uses contents: read, SHA-pinned checkout/setup actions and disabled checkout credential persistence. It has no secrets, OIDC, environment credentials, write permissions, application installation/build/hooks, artifact uploads or PR comments. Existing platform/package/Action tests remain separate and unchanged. Fork approval restrictions remain in force; no pull_request_target or privileged follow-up event is used.

PR files, workflow definitions and scanner tool-lock edits require review. Scanner parsers process untrusted content; read-only tokens and isolation reduce consequences but do not prove arbitrary PR code safe. A PR can change its own workflow, so self-reported green checks do not replace exact-diff review.

## Secret history

Gitleaks 8.30.1 is downloaded from its official release and checked before extraction against Linux archive SHA-256 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb. An explicit temporary configuration extends the binary's version-bound default rules. An explicit empty ignore file and disabled inline allow comments prevent repository-discovered suppressions. No custom exclusions are added to obtain green checks.

The scan covers all reachable history fetched by the full-depth checkout, including removed files, not unreachable/deleted server objects. --redact=100 masks detected secrets, but filenames, commit metadata and descriptions may still appear in GitHub Actions logs. Logs in this public repository must be treated as public. No separate finding report, debug trace or uploaded artifact is produced. Synthetic detector fixtures only; actual secrets require private handling under SECURITY.md.

## Runtime dependencies and scanner supply chain

requirements-lock.txt remains the runtime audit input, separate from requirements-security-lock.txt. The latter pins 28 scanner-tool packages, including pip-audit 2.10.1, with hashes verified against PyPI metadata for wheel-only Python 3.12 Linux resolution and local Windows verification. Python/runner tooling itself is not made immutable by these pins. A dependency/tool update needs renewed review and hash verification.

The lock validator permits exact named versions and SHA-256 hashes only, rejecting URLs, editable/VCS/local paths, nested requirement files, index directives, other options, duplicates, malformed hashes, symlinks and oversized files. Scanner installation permits hashed wheels only. The audit uses --strict --require-hashes --disable-pip --no-deps with the PyPI advisory service and a 15-second request timeout; it does not resolve or install the audited packages. No --fix or extra index is used. PyPI receives package names, versions and ordinary network metadata. GitHub hosts job logs. No vendor register data is submitted.

Coverage is known advisories for explicitly locked runtime packages, not every development/build dependency, malicious package behavior or unknown vulnerability. pip-audit normally can execute code during dependency resolution; the no-resolution options and constrained input are essential. Hashes identify expected bytes, not trustworthy behavior. Missing hashes/wheels, vulnerable dependencies and advisory failures must fail rather than silently skip. Real online results and simulated failure tests are reported separately.

## Deferred CodeQL

No executable CodeQL job, SARIF/database upload or security-events write permission is included. Exact CodeQL bundle/query provenance, residual payload behavior and fork/upload support still need evidence. Default CodeQL setup was observed not-configured; no analysis was returned. A read-only workflow-permissions query warned about missing admin:repo_hook scope; no scope expansion or retry is authorized.

Any future CodeQL activation needs a separately reviewed change and specific user confirmation of job-scoped security-events write and SARIF transmission to GitHub code scanning, including possible public PR annotations. Database uploads must be explicitly disabled. No skipped/deferred CodeQL check counts toward P-4 completion. No service/default-setup/fork/access changes are granted here.

## Verification

Run the normal contributor gates and workflow syntax validation. Scanner acceptance additionally requires a verified Gitleaks executable for temporary clean/deleted-history/redaction fixtures and verified pip-audit for real advisory and controlled failure-path checks. Tests that lack a verified scanner path report a skip; that skip is not acceptance evidence. Review all actual findings. A green analysis process alone is not a security approval.

See the [P-4 design](../aidlc-docs/inception/p4-security-ci-design.md), [execution plan](../aidlc-docs/inception/p4-security-ci-plan.md), [pip-audit security model](https://github.com/pypa/pip-audit/blob/v2.10.1/README.md), and [Gitleaks options](https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md).
