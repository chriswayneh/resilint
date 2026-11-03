# Security CI draft: read-only scanners

This P-4 implementation covers secret and runtime-dependency checks only. CodeQL is deferred, and P-4 remains planned. [PR #49](https://github.com/chriswayneh/resilint/pull/49) is a published draft at head `0006e5b5d3a80b98769663f6d3c305a15adecc9a`; main remains 28/38 tasks complete. The local documentation corrections have not been pushed and have no remote exact-head checks. The [audit correction](../aidlc-docs/audit.md#p-4--correction-unverified-approval-and-publication-authority-claims) supersedes the earlier unverified publication-authority claim. Subsequent approval of the scanner-only correction/validation does not retroactively authorize the earlier publication.

At that published head, all three jobs in [Security run 41564699043](https://github.com/chriswayneh/resilint/actions/runs/41564699043), [CI run 41564699055](https://github.com/chriswayneh/resilint/actions/runs/41564699055) and [Action run 41564699077](https://github.com/chriswayneh/resilint/actions/runs/41564699077) passed. The [scanner-controls job](https://github.com/chriswayneh/resilint/actions/runs/41564699043/job/125683289153) ran on Ubuntu 24.04.5 with Python 3.12.15: six cases passed, including collection and every setup/call/teardown phase. These hosted results establish Linux execution for the published head, not approval to merge or checks of the unpushed documentation head.

## Execution boundary

The draft workflow runs on pushes to main and pull requests targeting main (opened, synchronize, reopened and ready_for_review), with two separate ten-minute production scanner jobs and a fifteen-minute Linux/Python 3.12 scanner-control test job. It uses contents: read, SHA-pinned checkout/setup actions and disabled checkout credential persistence. It has no secrets, OIDC, environment credentials, write permissions, artifact uploads or PR comments. The two production scanner jobs perform no application installation/build/hooks. The separate scanner-controls job executes repository tests, conftest.py and the runner. Existing platform/package/Action tests remain separate and unchanged. Fork approval restrictions remain in force; no pull_request_target or privileged follow-up event is used.

PR files, workflow definitions and scanner tool-lock edits require review. Scanner parsers process untrusted content; read-only tokens and isolation reduce consequences but do not prove arbitrary PR code safe. A PR can change its own workflow, so self-reported green checks do not replace exact-diff review.

## Secret history

Gitleaks 8.30.1 is downloaded from its official release and checked before extraction against Linux archive SHA-256 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb. An explicit temporary configuration extends the binary's version-bound default rules. An explicit empty ignore file and disabled inline allow comments prevent repository-discovered suppressions. No custom exclusions are added to obtain green checks.

The scan covers all reachable history fetched by the full-depth checkout, including removed files, not unreachable/deleted server objects. --redact=100 masks detected secrets, but filenames, commit metadata and descriptions may still appear in GitHub Actions logs. Logs in this public repository must be treated as public. No separate finding report, debug trace or uploaded artifact is produced. Synthetic detector fixtures only; actual secrets require private handling under SECURITY.md.

## Runtime dependencies and scanner supply chain

requirements-lock.txt remains the runtime audit input, separate from requirements-security-lock.txt. The latter pins 29 scanner-tool packages, including pip-audit 2.10.1, with hashes verified against PyPI metadata for wheel-only Python 3.12 Linux resolution and local Windows verification. Python/runner tooling itself is not made immutable by these pins. A dependency/tool update needs renewed review and hash verification.

The lock validator permits exact named versions and SHA-256 hashes only, rejecting URLs, editable/VCS/local paths, nested requirement files, index directives, other options, duplicates, malformed hashes, symlinks and oversized files. Scanner installation permits hashed wheels only. The audit uses --strict --require-hashes --disable-pip --no-deps with the PyPI advisory service and a 15-second request timeout; it does not resolve or install the audited packages. No --fix or extra index is used. PyPI receives package names, versions and ordinary network metadata. GitHub hosts job logs. No vendor register data is submitted.

Coverage is known advisories for explicitly locked runtime packages, not every development/build dependency, malicious package behavior or unknown vulnerability. pip-audit normally can execute code during dependency resolution; the no-resolution options and constrained input are essential. Hashes identify expected bytes, not trustworthy behavior. Missing hashes/wheels, vulnerable dependencies and advisory failures must fail rather than silently skip. Real online results and simulated failure tests are reported separately.

## Deferred CodeQL

No executable CodeQL job, SARIF/database upload or security-events write permission is included. Exact CodeQL bundle/query provenance, residual payload behavior and fork/upload support still need evidence. Default CodeQL setup was observed not-configured; no analysis was returned. A read-only workflow-permissions query warned about missing admin:repo_hook scope; no scope expansion or retry is authorized.

Any future CodeQL activation needs a separately reviewed change and specific user confirmation of job-scoped security-events write and SARIF transmission to GitHub code scanning, including possible public PR annotations. Database uploads must be explicitly disabled. No skipped/deferred CodeQL check counts toward P-4 completion. No service/default-setup/fork/access changes are granted here.

## Verification

Run the normal contributor gates and workflow syntax validation. Scanner acceptance additionally requires a verified Gitleaks executable for temporary clean/deleted-history/redaction fixtures and verified pip-audit for real advisory and controlled failure-path checks. Ordinary matrix tests that lack a verified scanner path report a skip; that skip is not acceptance evidence. The dedicated scanner-controls job provisions the verified paths and requires all six controls through the strict runner. Review all actual findings. A green analysis process alone is not a security approval.

See the [P-4 design](../aidlc-docs/inception/p4-security-ci-design.md), [execution plan](../aidlc-docs/inception/p4-security-ci-plan.md), [pip-audit security model](https://github.com/pypa/pip-audit/blob/v2.10.1/README.md), and [Gitleaks options](https://github.com/gitleaks/gitleaks/blob/v8.30.1/README.md).

## Mandatory scanner-control lane

This separate test lane executes repository test code, conftest.py and the runner; it is not an inert scanner. It uses the same read-only ephemeral token and no-persisted-credentials boundary. Fork approval policy is unchanged. PR tests/workflows can be altered, so independent diff review remains necessary. It installs the existing scanner/runtime locks plus requirements-security-test-lock.txt as hashed wheels in a fresh venv, without installing/building the application. GitHub release storage and PyPI supply tools; controlled advisory cases mock transport. Logs go to GitHub, with no report/artifact uploads or privileged follow-up events.

scripts/check_scanner_controls.py requires all three executable paths, selects six exact test IDs, and requires unique complete collection plus passed setup/call/teardown for every case. Any skip, xfail/xpass, failure, error, missing/duplicate ID, duplicate phase or incomplete outcome fails the job. The six cases cover history/redaction/suppression, clean/vulnerable/missing/outage advisory responses and checksum rejection. Normal matrix and production scanner jobs remain unchanged.

The original 329-test local result applies only to the original P-4 head. Amended-head evidence is recorded separately. Cross-platform wheel installation and metadata checks did not prove Linux runtime execution. The published-head hosted results above provide that separate evidence; they do not apply to the unpushed local documentation head.

## Repeatable local Linux/Python 3.12 verification

Run from the repository root with Python 3.12, Git, Bash, curl, tar and sha256sum available. This creates a new temporary tool directory and retains it; it does not clean existing artifacts. No application install is performed.

```bash
SCANNER_CONTROL_ROOT="$(mktemp -d)"
curl --fail --silent --show-error --location https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_linux_x64.tar.gz --output "$SCANNER_CONTROL_ROOT/gitleaks.tar.gz"
echo "551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb  $SCANNER_CONTROL_ROOT/gitleaks.tar.gz" | sha256sum --check --strict || exit 1
mkdir "$SCANNER_CONTROL_ROOT/bin"
tar -xzf "$SCANNER_CONTROL_ROOT/gitleaks.tar.gz" -C "$SCANNER_CONTROL_ROOT/bin" gitleaks
python3.12 -m venv "$SCANNER_CONTROL_ROOT/venv"
"$SCANNER_CONTROL_ROOT/venv/bin/python" -I -m pip --isolated install --only-binary=:all: --require-hashes --index-url https://pypi.org/simple/ -r requirements-security-lock.txt -r requirements-security-test-lock.txt -r requirements-lock.txt || exit 1
export RESILINT_TEST_GITLEAKS="$SCANNER_CONTROL_ROOT/bin/gitleaks"
export RESILINT_TEST_AUDIT_PYTHON="$SCANNER_CONTROL_ROOT/venv/bin/python"
export RESILINT_TEST_BASH="$(command -v bash)"
export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
"$RESILINT_TEST_AUDIT_PYTHON" -I scripts/check_scanner_controls.py
```

For local Windows verification, use the same three hash-locked requirements files in a fresh venv, the official Gitleaks 8.30.1 Windows archive verified against d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e before extraction, and absolute paths to gitleaks.exe, that venv's Scripts/python.exe and Git Bash. This does not replace the Linux/Python 3.12 hosted lane.

## Historical local amendment compatibility blocker

Before the lock correction, the amended local verification installed 33 Linux-target wheels into a separate directory, then evaluated their dependency metadata for Linux/Python 3.12. It found one unresolved dependency: cyclonedx-python-lib 11.12.0 requires typing_extensions >=4.6,<5.0 when Python is below 3.13. The original scanner lock omitted it. Windows/Python 3.13 resolution and the earlier cross-platform dry-run did not establish complete Python 3.12 dependency closure. Both the production dependency job and the new test lane required that correction before hosted acceptance.

At that stage, the lock was outside the approved seven-file amendment scope and was left unchanged. The proposed separate scope correction was typing-extensions==4.16.0, universal-wheel SHA-256 481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8, verified against PyPI metadata. It requires Python >=3.9 and satisfies the missing constraint. The seven-file amendment did not install or add that candidate. Actual Linux execution was unavailable locally at that stage; the local Linux engine was not running. No service was started or settings changed. A cross-target installation is not Linux execution.

## Compatibility correction and subsequent approval

Published head `0006e5b5d3a80b98769663f6d3c305a15adecc9a` includes the verified typing-extensions 4.16.0 wheel in the scanner lock for both production and test jobs. The authenticated user approval at 2026-11-03T02:27:10.264724Z covered the bounded correction/validation request and arrived after draft PR publication at 02:12:49Z; it did not retroactively authorize that publication. The earlier blocker and failed closure evidence remain historical evidence. Corrected dependency closure and the published-head hosted Linux results are recorded separately in the audit. Independent exact-head review remains required before merge.
