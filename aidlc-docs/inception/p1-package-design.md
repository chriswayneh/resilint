# P-1 package-build design

Status: proposed for routine inception review; no new construction approval claimed. Preserve the pre-adoption draft at 3fd4b7394259f17c3c4ff85fc96c8eb05887e625. Its existence and prior author checks are not retrospective stage approval.

## Scope and prerequisite

P-1 adds CI verification that source and wheel distributions build, pass Twine validation and install into a fresh virtual environment with a working CLI. M0-1 is its sole recorded prerequisite and is merged. Integrate current main after D-6 merges so its guidance is inherited without bundling unmerged tasks. v1 alone remains the product target.

Use the existing Ubuntu/Python 3.12 CI context for a separate 15-minute package job. Preserve all existing coverage/platform/Action jobs. Checkout and Python setup remain SHA pinned; checkout credentials are not persisted. Inherit the workflow's read-only token. Build both distribution formats, check metadata with Twine, install the wheel into a new environment and run from a temporary directory outside the checkout. Verify --version, packaged init data and a synthetic JSON check containing precisely RL004, RL005 and RL008; use the existing critical fail threshold so expected high findings do not abort this smoke test.

The existing draft modernizes setuptools build metadata to an MIT SPDX string plus LICENSE inclusion with setuptools >=77.0.3; this preserves the actual license. Verify packaged license metadata and the starter resource rather than relying solely on editable installs. Build and Twine are build/validation tooling, not new runtime dependencies. Keep package/runtime version 0.4.0, runtime dependencies and CLI behavior unchanged.

Files: .github/workflows/ci.yml, pyproject.toml, .gitignore, CHANGELOG.md, roadmap/README.md, task completion metadata and P-1 inception/audit records. Ignore generated build/dist files while retaining existing local artifacts. No publication, artifact upload, tags, release workflow, credentials, publisher registration, settings or cleanup is included.

## Acceptance and risk

Run all repository gates and the complete hosted matrix/Action checks plus the new package job. Locally build into a fresh temporary output directory, run Twine on exactly those new outputs, and verify a fresh wheel installation outside the checkout including version, starter resource, report findings and MIT license metadata. Check both wheel and sdist contents. Validate workflow syntax and complete exact-head diff for security. Build tooling resolves from package indexes during CI, as existing development installation does; this task does not claim hermetic or reproducible builds. Runtime remains offline. No repository secrets or elevated token permissions are needed, and no arbitrary PR content is interpolated into shell commands. Synthetic input and temporary outputs only.

Review compatibility of the build-backend minimum with the supported Python floor. Any need for runtime, publishing, permission or material dependency changes beyond this build-tool scope returns to design review. P-2 publisher setup and R-2 remain separate tasks with their own prerequisites and approvals.

See [execution plan](p1-package-plan.md).
