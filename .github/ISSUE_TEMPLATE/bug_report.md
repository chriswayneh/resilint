---
name: Bug report
about: Report a reproducible CLI or integration problem using fictional data
title: ''
---

Use fictional data only. Remove vendor contracts, real contacts, credentials and personal data. Report security issues privately using [SECURITY.md](https://github.com/chriswayneh/resilint/blob/main/SECURITY.md).

## Environment

- resilint version and install method:
- Python version and operating system:
- Command and relevant configuration (redacted, fictional):

## Reproduction

Provide the smallest fictional register, exact command, expected behavior, actual exit code and diagnostic. State whether the input was YAML or CSV and include the delimiter when relevant.

## Validation for a proposed fix

Contributors run `ruff check .`, `mypy src`, `pytest -q`, `git diff --check` and `python scripts/check_links.py`. Include results if proposing a patch; reporting a bug does not require a development setup. See [CONTRIBUTING.md](https://github.com/chriswayneh/resilint/blob/main/CONTRIBUTING.md).
