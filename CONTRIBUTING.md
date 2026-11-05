# Contributing

Use fictional data only in examples, tests, screenshots, issues and pull requests. Never submit real vendor contracts, contact details, secrets, PHI, PII or personal data. Report suspected vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

resilint runs locally and offline. Keep changes focused on recorded commitments; vendor contact, scraping, telemetry and hosted services are outside scope. The active release target is v1.0; later major versions are deferred.

Read [AGENTS.md](AGENTS.md), the [roadmap](ROADMAP.md) and [workflow records](aidlc-docs/README.md) before substantive work. Establish a technical design and execution plan before implementation; record actual stage decisions in the audit before advancing. Dot’s delegated routine review must be attributed to dot, never represented as personal user approval.

## Development setup

Use Python 3.10 or newer and install the development dependencies in a virtual environment:

```bash
python -m venv .venv
```

Activate the environment first or invoke its Python directly; see [installation](docs/install.md). Then install:

```bash
python -m pip install -e ".[dev]"
```

Keep one roadmap task per small branch/PR against `main`, using `<type>/<task-id>-slug`. Preserve history: fix review feedback with new commits rather than force-pushing or rebasing. Include the task ID, behavior change, acceptance results and relevant changelog/docs updates. See the [roadmap working guide](roadmap/README.md).

## Required checks

Run and record these gate commands:

```bash
ruff check .
mypy src
pytest -q
git diff --check
python scripts/check_links.py
```

CI also requires `pytest -q --cov=src/resilint --cov-report=term-missing --cov-fail-under=90`, the Linux/Windows/macOS × Python 3.10/3.12/3.13 matrix, and the hosted Action self-test. Local Windows runs can skip symlink tests only when the OS denies that privilege; hosted CI must exercise them.

Write tests for changed behavior and meaningful regressions. Review report snapshots before updating them; see the [report contract](docs/reports.md). The link checker validates local inline Markdown links and ATX heading fragments, ignoring fenced examples and external URLs; it performs no network requests.

## Review and releases

Review the exact head before merging; code changes also receive security review. GitHub PR approval, merging, tags, releases and repository settings remain user-owned unless the user explicitly authorizes a scoped exception. A routine design or implementation-stage review is not a formal GitHub approval or permission for reserved actions; verify any bounded authorization at action time. Keep the roadmap's completion record in the same PR so it becomes true at merge. Release only after the [release checklist](roadmap/README.md#release-checklist) passes. The [stability policy](docs/stability.md) defines the v1 compatibility contract and deprecation requirements.

## Proposed security checks

The P-4 draft adds read-only secret-history and explicit runtime-lock audits. CodeQL is deferred, so P-4 remains incomplete. See [security CI scope and limits](docs/security-ci.md) before reviewing or authorizing execution. Scanner results do not replace security review; only fictional detector fixtures belong in tests.
