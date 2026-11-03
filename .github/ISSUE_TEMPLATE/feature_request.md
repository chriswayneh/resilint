---
name: Feature request
about: Propose a focused improvement to offline resilience checks
title: ''
---

Use fictional data only. Do not include real vendor information, secrets, PHI, PII or personal data.

## Problem and proposed behavior

Describe the user need, a fictional input/command example, the desired output and how the request fits the project's offline scope. Identify a relevant roadmap task when possible. v1 is the active target; later major versions are deferred.

## Compatibility and validation

Explain effects on existing flags, exit codes, rules or output fields. Proposed code changes must pass `ruff check .`, `mypy src`, `pytest -q`, `git diff --check` and `python scripts/check_links.py`. See [CONTRIBUTING.md](https://github.com/chriswayneh/resilint/blob/main/CONTRIBUTING.md) and the [stability policy](https://github.com/chriswayneh/resilint/blob/main/docs/stability.md).
