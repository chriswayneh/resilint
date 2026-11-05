# P-6 PyPI installation documentation: design and plan

P-2 is merged and both pending publishers/protected environments are verified. Prepare one documentation-only P-6 PR with stable PyPI version pinning, pipx isolation and the Git-based alternative. Preserve the current README layout and truthful status: v0.4.0 is the latest published Git release; no production PyPI upload is claimed. Label v1 commands as available after publication until the release step updates status.

Keep Python 3.10+ support, virtual-environment/PowerShell instructions and index-versus-offline runtime boundaries. Do not recommend mixed package indexes or token creation. The candidate TestPyPI install belongs to release validation, not the normal user install.

Run the required repository gates and link/whitespace checks, review every documentation change for version drift, misleading availability, unsafe copy/paste and privacy, then require hosted CI/Action/security/CodeQL on the immutable final head. Preserve all original acceptance criteria and count P-6 complete only on merge. No source/dependency/workflow/account/settings change. Actual index installation remains part of R-3.
