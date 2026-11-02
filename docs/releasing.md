# Publishing a release

Release publication is delegated only to the maintainer or an explicitly authorized delegate. Complete the [release checklist](../roadmap/README.md#release-checklist) first. Source changes and tagged artifacts must be reviewed before publication.

## One-time setup

Configure a [pending publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/) in both package-index accounts, or add a publisher to the existing project:

| Field | PyPI | TestPyPI |
| --- | --- | --- |
| Project | `resilint` | `resilint` |
| Owner | `chriswayneh` | `chriswayneh` |
| Repository | `resilint` | `resilint` |
| Workflow filename | `release.yml` | `release.yml` |
| Environment | `pypi` | `testpypi` |

The accounts are separate and require their own sign-in and two-factor setup. Do not put passwords, API tokens or recovery codes in GitHub or chat. The workflow requests short-lived OIDC credentials; no PyPI API-token secret is used.

Create the GitHub environments with the matching names. Restrict deployments to version tags (`v*`), with no branches allowed. Require the maintainer's manual approval on `pypi`; inspect the tag, commit and preceding verification jobs before approving. An authorized delegate can act within the maintainer's existing release authorization. Keep the approval gate enabled.

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
