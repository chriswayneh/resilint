# P-4 amendment: mandatory scanner-control validation

Status: inception amendment proposed for dot review only. No implementation, executable commit, push or PR is authorized. Applies to Alternative A at local head 2e8fc5a97b6f643ec3212cc5dd2ac4c9bff270b6, based on main 0c82503ce1fa737276be6c70c0230335c8b8406f. The original 329-pass local result remains evidence for that original head only. P-4 remains planned; CodeQL is deferred.

## Gap and bounded change

The current ordinary matrix does not set the three scanner-path variables, so six scanner-control cases skip. Direct scanner jobs do not exercise their adversarial fixtures. Add one separate scanner-controls job in .github/workflows/security.yml, Ubuntu/Python 3.12, 15-minute timeout, under the existing main-push and PR-to-main events. Keep the two production scanner jobs and normal matrix checks intact. The new lane explicitly executes repository test code and tests/conftest.py; production scanner jobs retain their no-application-install/build/hooks boundary.

Proposed file delta: modify .github/workflows/security.yml, tests/test_security_ci.py and docs/security-ci.md; add scripts/check_scanner_controls.py and requirements-security-test-lock.txt; append truthful P-4 audit evidence and this amendment. Existing runtime and scanner tool locks remain unchanged. No unrelated files, workflow permissions, tasks/counts, branches or artifacts change.

## Provisioning

Reuse checkout 3d3c42e5aac5ba805825da76410c181273ba90b1 and setup-python 6d4fd22b20465ccc0f7354476588e8df7c9ca0e0. Disable persisted checkout credentials. Reuse official Gitleaks 8.30.1 Linux archive and verified SHA-256 551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb, checking before extraction. No weaker alternate download path. The existing binary-bound default rules and adversarial suppression coverage stay intact.

Create a fresh test venv under RUNNER_TEMP. Install wheels only with pip --isolated, --require-hashes and explicit https://pypi.org/simple/, supplying requirements-security-lock.txt, requirements-security-test-lock.txt and requirements-lock.txt together. This reuses the verified 28-package scanner lock (including pip-audit 2.10.1) and existing PyYAML 6.0.3 hashes. Do not install the application with -e, build it, or run its setup hooks. The test lane may install runtime dependencies for test imports; this does not change production scanner behavior.

New test-lock packages and universal-wheel SHA-256 values, verified read-only against PyPI version metadata during amendment preparation:

- pytest==9.2.0: 07acdcf88ec174f907dc01af70bf52d49b014bbab03faeeade31c96b18c2e588
- pluggy==1.7.0: 7dd7b0d8832ba3cb632c306926ded123429211b83641b35dc5c41ad2d34f9bec
- iniconfig==2.3.1: 9121e2c1fdb355232495be3194c8dfe87ccc2d5dee45947b78e68f499790d7a7
- colorama==0.4.6: 4f1d9991f5acc0ca119f9d443620b77f9d6b33703e51011c16baf57afb285fc6

The first three require Python >=3.10 and support the selected 3.12 lane. Colorama preserves optional local Windows provisioning; Linux does not require it but the pure wheel is safe to include in this test-tool lock. Pytest's packaging/pygments dependencies already exist in the scanner lock. Python 3.12 does not require pytest's conditional exceptiongroup/tomli backports. Verify actual complete wheel resolution/hash-checked installation after construction approval; metadata inspection alone is not an install test. No live latest-version resolution in CI.

## Exact invocation and fail-on-skip behavior

After provisioning in the separate test job, use this command sequence from repository root:

    export RESILINT_TEST_GITLEAKS="$RUNNER_TEMP/scanner-controls/gitleaks"
    export RESILINT_TEST_AUDIT_PYTHON="$RUNNER_TEMP/scanner-controls-venv/bin/python"
    export RESILINT_TEST_BASH="$(command -v bash)"
    export PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
    "$RESILINT_TEST_AUDIT_PYTHON" -I scripts/check_scanner_controls.py

The short runner requires all three variables to name existing executable files, failing before pytest for missing/invalid paths. It invokes pytest programmatically with a small local plugin, cacheprovider disabled and these six explicit node IDs:

- tests/test_security_ci.py::test_real_gitleaks_history_redaction_and_ignore_resistance
- tests/test_security_ci.py::test_real_audit_cli_with_mocked_advisories[clean-0]
- tests/test_security_ci.py::test_real_audit_cli_with_mocked_advisories[vulnerable-1]
- tests/test_security_ci.py::test_real_audit_cli_with_mocked_advisories[missing-1]
- tests/test_security_ci.py::test_real_audit_cli_with_mocked_advisories[outage-1]
- tests/test_security_ci.py::test_checksum_failure_prevents_acceptance

Require exactly those six collected cases and six successful call reports. Any skip/xfail, missing/renamed test, collection/setup/teardown error, failed case or incomplete run yields a nonzero exit. Normal matrix invocations may keep optional scanner skips; this dedicated mandatory lane supplies the persistent acceptance gate. Do not parse console prose or rely solely on pytest's usual exit status, which permits skipped tests. No JUnit/report artifact or upload is needed.

Document a repeatable local recipe using the same verified Gitleaks extraction, hash-locked three-file venv installation, environment assignments and runner invocation. On Windows, use the verified Windows Gitleaks archive digest d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e and explicit Git Bash path; keep Linux/Python 3.12 the required hosted lane. A path-only command assumes prior verified provisioning and must not be presented as a complete bootstrap recipe.

## Trust boundary and destinations

The test lane executes untrusted PR tests, conftest and runner code in an ephemeral GitHub-hosted runner with contents: read only, no secrets, persisted checkout credentials, environment credentials, OIDC, writes, artifacts/reports/uploads/comments or privileged follow-up events. It uses the same existing PR approval restrictions; no fork-policy changes. This does not claim repository tests are inert or network-isolated. Same-repository and fork PRs can change tests/workflows, so independent exact-diff review remains necessary.

Provisioning contacts GitHub release storage and PyPI for tool wheels. Controlled advisory cases use mocked transport; they are not live vulnerability/outage tests. Logs go to GitHub and may reveal synthetic filenames/metadata. Existing real dependency audit separately contacts PyPI. No CodeQL, SARIF/database upload, security-events write, persistent trust or service/settings change is included.

## Validation and approval sequence

After approval, record actual reviewer/time and implement only this amendment. Test each missing variable and nonexistent/non-executable path produces failure before invoking tests. Exercise the gate against synthetic passing, skipped, xfailed, failed, collection-error and incomplete-count outcomes; ensure setup/teardown skips also fail. Run the real six cases with verified tools and require six passes/zero skips. Inspect resulting provisioning for checksum/hash enforcement and no application installation. Rerun all current local gates, syntax validation and full tests with appropriate verified scanner paths; distinguish real, simulated and skipped results.

Return the complete amended immutable local patch and actual evidence for independent review. Stop before push/PR creation; a future draft PR would execute the workflow and needs separate authorization. Hosted success cannot be claimed before that authorization and actual final-head execution. Preserve original adversarial cases, production scanners, normal matrix, PRs #47/#48, all branches, stash, private records and artifacts. No cleanup, history rewriting or denied-operation retry. Rollback is ordinary reviewed amendment-only commits; no reserved action follows automatically.

Primary pin metadata: https://pypi.org/pypi/pytest/9.2.0/json, https://pypi.org/pypi/pluggy/1.7.0/json, https://pypi.org/pypi/iniconfig/2.3.1/json and https://pypi.org/pypi/colorama/0.4.6/json. Existing scanner provenance remains recorded in the P-4 design and original local audit.
