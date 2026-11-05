# P-3 release evidence design and execution plan

Status: proposed, local design only. No implementation-stage approval is claimed. P-2 is the dependency; its workflow may be reviewed locally while external publisher setup remains unverified. Preserve the older provenance branch as historical work, rather than transplanting its obsolete roadmap or governance files.

## Scope and acceptance

One P-3 PR adds a CycloneDX SBOM and SHA-pinned GitHub build provenance for the exact distributions produced by the release build. Attach the SBOM, provenance bundle and checksums to the matching GitHub release. Preserve the current presentation and the P-2 release identity, protected environments, TestPyPI-first verification and build-once distribution flow. Keep P-3 planned until its required release evidence is actually demonstrated.

## Construction decisions to review

- Generate the runtime SBOM from a fresh environment containing hash-locked runtime dependencies and the built wheel. Keep developer/scanner tooling out of that environment; document unavoidable environment inventory and avoid claiming the SBOM proves absence of vulnerabilities.
- Resolve SBOM tooling into a separate pinned, hashed tool lock. Validate CycloneDX output and its package identity/version against the built distribution. A version-only tool pin does not fully lock its transitive dependencies.
- Reuse the same build artifacts for attestation, TestPyPI and PyPI. Produce checksums for distributions and the SBOM, then retain the attestation bundle. Check artifact membership and reject missing or unexpected distribution files before publication.
- Isolate provenance permissions to the attestation job: contents read, id-token write and attestations write. Publisher jobs retain only their existing OIDC grant and protected environments. Grant contents write only to a separate release-attachment job. No repository settings or persistent trust changes.
- Require successful provenance and TestPyPI verification before release attachment. Candidate releases remain prereleases; stable releases also require successful production publication. Avoid treating skipped publisher jobs as success. Fail rather than silently replacing assets or mutable version tags.
- Use validated tag/version values via quoted environment variables. Preserve ancestry checks, bounded execution, safe artifact paths and immutable release identity. No runtime CLI networking or vendor data.

## Verification and review

1. Reconcile with merged main using ordinary commits after P-2 integration; preserve prior audit records and all unrelated work.
2. Record actual design review before implementation. Implement only the P-3 workflow, helpers, focused tests, lock and documentation; update its roadmap status only when the stated completion boundary is satisfied.
3. Test malformed/mismatched metadata, missing/extra artifacts, SBOM identity, checksum membership, candidate/stable job ordering and permission isolation. Exercise real local SBOM generation using synthetic package fixtures and inspect the complete output for private paths or inventory leaks before any public upload.
4. Run Ruff, mypy, full pytest, links and whitespace checks, plus relevant workflow validation and the existing hosted platform/coverage/Action/security gates on the final commit.
5. Review the complete final diff for secrets, unsafe interpolation, dependency safety, least privilege and artifact substitution. Clearly distinguish local artifact tests from a real hosted OIDC attestation and signed release upload.
6. Present the immutable patch and remaining limits for review, then apply only within the user's actual authorization. No signing, publisher registration, tag push, environment approval or settings change follows merely from this design.

## Release dependencies and rollback

P-2 still needs verified PyPI/TestPyPI publisher coordinates and protected-environment configuration. P-4 still needs its separately reviewed CodeQL continuation. P-6 follows genuinely satisfied P-2; R-1 follows all prerequisite milestones. Do not bypass those dependencies by changing their acceptance criteria. Roll back with ordinary commits; preserve existing branches, worktrees, packages, version tags and build artifacts.
