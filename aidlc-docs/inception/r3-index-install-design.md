# R-3 fresh TestPyPI installation: design and plan

Planning only until R-1 and P-2 are genuinely complete. One R-3 PR adds a read-only, manually dispatched workflow with Linux/Windows/macOS on Python 3.12, plus a portable bounded smoke helper and tests. The regular source CI retains the Python 3.10/3.12/3.13 matrix. Do not introduce privileged follow-up events, settings, protected publisher credentials or new persistent account access.

Validate the requested normalized version against a strict release grammar and the checked-out project/runtime version. Create a new temporary venv, install exact hashed runtime requirements from PyPI, then install only the exact resilint version from TestPyPI with no dependencies, no mixed indexes and bounded propagation retries/timeouts. Run outside the checkout in an empty working directory with isolated Python. Assert distribution version and installed module/resource byte hashes match the reviewed source, so an editable/source-tree import or different artifact cannot masquerade as an index install.

Exercise the documented init/check/explain quick start, expected starter findings and exit status, and source/resource preservation. Keep all generated files in the temporary workspace; print only useful public version/outcome summaries. No real vendor data or credentials. Helpers should use argument arrays rather than shell interpolation, validate inputs before package-index commands and reject invalid/mismatched versions.

After prerequisites and candidate upload exist, record the construction decision, implement one task PR, run full local gates and relevant helper tests/security review, require all immutable-head hosted source checks, merge if passing, then dispatch the actual three-platform index install and inspect every result. Source tests/mocks do not count as a real index install. Completion metadata must follow accepted live results in the same task when possible; do not claim R-3 complete before all three platforms pass. Re-run the install matrix for the stable version before production PyPI approval when it is available on TestPyPI.

Preserve immutable tags/versions, existing environment approvals and all original task criteria. Do not publish or rebuild distributions in this smoke workflow; preserve older drafts/artifacts and use ordinary commits only.

## Construction refinements to retain

Add ordinary PR path triggers limited to the new smoke workflow/helper so the first three-platform index test can run before the R-3 PR merges. Keep manual dispatch for later releases; source version-only changes must not trigger an index install before their version is published. No privileged workflow_run or PR-target event is needed.

Download the exact TestPyPI wheel without installing it, reject unexpected archive paths/files, and compare packaged Python/template bytes with the reviewed source before executing any installed package code. Validate distribution identity, the expected console entry point and RECORD membership/hashes; reject installer hook paths such as .pth or .data/scripts. Then install the verified local wheel with its computed SHA-256, no dependency resolution or mixed index, and run the isolated quick start. This reduces reliance on a post-import source comparison and preserves the actual index-download/install requirement. Validate malformed versions and tampered/extra wheel files with synthetic fixtures.

## Portable source identity and installation refinements

Compare wheel files against canonical tracked Git blob bytes rather than working-tree line endings, so Windows checkout conversion cannot cause a false identity mismatch. Reject archive installer hooks, paths outside the exact source/metadata allowlist, duplicate/symlink/oversized members, unexpected identity/entry points and invalid RECORD hashes before package installation or application imports.

The helper is release tooling, not part of the offline CLI. Clear inherited pip/Python override variables for child processes, disable pip configuration with PIP_CONFIG_FILE=os.devnull, set one explicit HTTPS index for each download stage, require binary/hash-locked runtime packages, and install the preverified local project wheel with no index/dependency resolution. See official [pip configuration](https://pip.pypa.io/en/stable/topics/configuration/#pip-config-file) and [secure installs](https://pip.pypa.io/en/stable/topics/secure-installs/) for these controls.

Document an exact four-command candidate quick start (version, init, JSON check with critical threshold, explain). Execute those installed console commands outside the checkout; assert normalized distribution version, raw CLI version, starter findings RL004/RL005/RL008 and installed source/resource bytes. Synthetic unit tests validate rejection/control paths; they do not substitute for actual TestPyPI installs on all three operating systems.
