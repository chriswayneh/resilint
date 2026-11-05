# Publishing a release

Release publication is delegated only to the maintainer or an explicitly authorized delegate. Complete the [release checklist](../roadmap/README.md#release-checklist) first. Source changes and tagged artifacts must be reviewed before publication.

## One-time setup

After verifying the signed-in account and project ownership, obtain specific action-time user confirmation of the project, repository, workflow and environment before creating persistent publisher trust. General release permission or sign-in alone does not authorize registration. Configure a [pending publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) in both package-index accounts, or add a publisher to the existing project:

| Field | PyPI | TestPyPI |
| --- | --- | --- |
| Project | `resilint` | `resilint` |
| Owner | `chriswayneh` | `chriswayneh` |
| Repository | `resilint` | `resilint` |
| Workflow filename | `release.yml` | `release.yml` |
| Environment | `pypi` | `testpypi` |

The accounts are separate and require their own sign-in and two-factor setup. Do not put passwords, API tokens or recovery codes in GitHub or chat. The workflow requests short-lived OIDC credentials; no PyPI API-token secret is used.

The matching GitHub environments already exist; inspect their protection and tag policies without changing settings. Any settings changes require separate user authorization. Restrict deployments to version tags (`v*`), with no branches allowed. Require the maintainer's manual approval on `pypi`; inspect the tag, commit and preceding verification jobs before approving. Routine design/implementation review does not authorize environment approval, activating merges, tags or publication; verify the actual user authorization and any expiry at action time. Keep the approval gate enabled.

## Candidate and stable publication

The workflow runs only on pushed `v*` tags. The moving Action alias `v1` is ignored. Its build job rejects tags other than `vX.Y.Z` or `vX.Y.Z-rcN`, mismatched package/runtime/changelog versions, and commits outside merged `main` history. Version tags are immutable: never move or recreate them.

1. Merge the version/changelog PR and require all platform and security checks to pass on `main`.
2. Tag that reviewed commit, for example `v1.0.0-rc1`, and push the tag.
3. The workflow runs lint, types, coverage and links, builds once, checks both distributions, and uploads them as a workflow artifact.
4. TestPyPI receives the distributions first. A separate clean environment installs dependencies from the hash-locked PyPI requirements, then installs only `resilint` from TestPyPI using `--no-deps`. It runs the packaged starter quick start outside the source checkout. Index propagation retries are bounded.
5. Candidates stop after TestPyPI verification. For a stable version, approve the protected `pypi` job only after verification passes. It publishes the same build artifact to PyPI without rebuilding it.

The source spelling `1.0.0-rc1` becomes `1.0.0rc1` in normalized Python distribution metadata and index installs. Stable versions retain `1.0.0` spelling.

If a job fails, inspect its logs and rerun failed jobs after correcting the external condition. A whole-workflow rerun may attempt a duplicate upload; duplicate versions fail rather than silently skipping files. Never replace a published version with different bytes. If a source change is necessary after publication, use a new candidate/patch version and review it again.

The first end-to-end run needs both publisher registrations and environment setup. A merged workflow alone is not evidence that publication works. See the [stability policy](stability.md) for compatibility expectations.

Publisher registration and protected-environment configuration are recorded in the [audit](../aidlc-docs/audit.md). A pending publisher does not reserve a project name. Configuration and workflow validation do not prove a successful OIDC upload or installation from an index; verify those during the candidate release.

## SBOM, provenance and artifact identity

The build prepares one wheel and one sdist, then generates a CycloneDX 1.6 runtime SBOM from a fresh environment containing the installed wheel and hash-locked runtime dependencies. SBOM tooling has its own hash-locked requirements, separate from that environment and the CLI's dependencies. The public inventory contains the project, locked runtime package names/versions, PURLs and dependency edges. Bootstrap installers are excluded; unexpected packages or unlocked runtime edges fail. Local paths, environment properties and tool inventory are omitted. This minimal inventory does not claim component-license completeness or absence of vulnerabilities.

The release evidence self-test runs the same preparation step on Linux/Python 3.12 for PRs and main pushes. It builds real distributions, generates and validates the SBOM, and has only a read-only token. It executes repository workflow code like the existing tests, and does not attest, publish, upload artifacts or use protected environments. Hosted evidence must be checked on the final PR commit.

`SHA256SUMS` covers the wheel, sdist, SBOM and release notes. Subsequent jobs reject missing/extra files or byte changes before using downloaded build artifacts. A separate job with `id-token: write` and `attestations: write` signs the wheel, sdist and SBOM using the pinned GitHub provenance action. It preserves the Sigstore bundle; no distribution is rebuilt for publication.

After protected TestPyPI verification, and production PyPI success for stable versions, a separate release-attachment job verifies each subject against the bundle, repository, exact source ref, source commit and workflow identity before creating the GitHub release. It has contents-write and attestation-read permissions, with no OIDC grant. Candidate releases are marked prerelease. Existing tags, package versions and GitHub releases are never replaced automatically.

Release assets include both distributions, `resilint.cdx.json`, `SHA256SUMS`, `release-notes.md` and `provenance.sigstore.json`. The bundle is generated after the checksum manifest and is verified cryptographically rather than included in that manifest. Attestation identity and provenance metadata are published through GitHub/Sigstore; all attached evidence is public. No register data is included. Package-index and GitHub environment approval gates remain in place.

Local SBOM/schema/checksum tests and PR self-tests demonstrate preparation readiness. Real hosted signing, protected index upload, clean index installation and final release attachment must additionally be verified during the candidate/stable release sequence. Do not treat readiness evidence as a completed publication or skip those release checks.
