# P-2 trusted-publishing design

Status: proposed for routine inception review only. Preserve pre-adoption draft 050f917ab58b7957d7219a7c1ce998cca101e47e; no retrospective approval. P-1 must be merged before P-2 integration. v1 is the active scope.

## Repository construction scope

Add .github/workflows/release.yml, scripts/release_metadata.py, focused tests, docs/releasing.md, changelog and inception/audit records. Preserve runtime version, dependencies and behavior. Reconcile the existing draft with adopted governance and current user-owned action boundaries. This plan authorizes no external setup or actual publication.

The workflow triggers only on pushed v* tags and ignores the moving v1 alias. Validate a strict vX.Y.Z or vX.Y.Z-rcN tag against package/runtime versions and a dated changelog; require the tagged commit to be an ancestor of origin/main. Pass the ref via an environment variable and quoted argument, never direct untrusted shell interpolation. Run existing lint/types/coverage/link gates before building and Twine validation. Build once and retain the distribution artifact for 14 days. Use pinned checkout/setup/upload/download/publishing actions; checkout must not persist credentials. Serialize each tag without canceling an in-progress release.

Separate protected TestPyPI and PyPI jobs download the same distributions without rebuilding. Only publisher jobs request id-token: write; default token contents access is read-only. No API token secret. TestPyPI comes first for both candidates and stable versions. A clean verification venv installs hash-locked runtime dependencies from PyPI, then the exact normalized resilint version from TestPyPI with --no-deps and bounded retries. Outside checkout, verify installed version, init resource and expected synthetic JSON findings. Stable PyPI publication depends on successful TestPyPI verification; candidates never publish to production PyPI. Existing environment manual approval remains enabled. Tag and package versions are immutable; duplicate uploads fail rather than silently skipping artifacts. Document failed-job recovery without moving tags or replacing published bytes.

## External setup and completion boundary

Read-only inspection shows both pypi and testpypi GitHub environments already have required-reviewer protection and custom deployment policy. Verify exact tag policies before any release; do not change settings. Publisher registrations, account ownership/project-name availability, account verification and 2FA are not verified. Signing in or broad release permission does not authorize creating persistent publisher trust. Registering either publisher requires specific action-time user confirmation of owner/repository/workflow/environment/project. No such registration or environment mutation is included in routine construction approval.

Publisher coordinates to present for separate confirmation: project resilint; repository chriswayneh/resilint; workflow release.yml; environment pypi on PyPI and testpypi on TestPyPI. Never collect passwords, MFA, recovery codes or API tokens in chat. Preserve user-owned environment approval gates and check actual release authorization at action time.

Keep P-2 planned until its acceptance criteria, including maintainer configuration, are evidenced. A reviewed workflow PR may land while configuration remains blocked, but must not falsely claim task completion, successful OIDC upload or end-to-end installation. Do not mark dependent release prerequisites satisfied from local simulation. P-3 provenance and later release tasks retain separate stage reviews.

## Validation and risk

Run all local and hosted gates, syntax validation and meaningful metadata tests for stable/candidate normalization, malformed tags/injection strings, version mismatch and missing dated release entry. Verify dependency ordering and permissions from the complete diff, retain exact-head security review and request independent implementation review. Add an explicit installed-version assertion to the existing TestPyPI verification smoke so logs alone do not prove identity. Locally validate the release helper with synthetic temporary trees and confirm the current unreleased version fails the publication identity gate where appropriate.

No production end-to-end run is possible before protected account setup and a separately authorized release tag. Document that limitation. OIDC trust and publication are security-sensitive; preserve least privilege, no credential persistence, immutable artifacts and manual approval. No new runtime networking, SQL or vendor data. Build tooling is index-resolved, not a hermetic/reproducible-build guarantee. Material scope changes return to design review.

See [execution plan](p2-publishing-plan.md).
