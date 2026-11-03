# README presentation alignment: execution plan

1. Branch `docs/readme-presentation` from current `main`; leave all other branches and draft PRs untouched.
2. Add banner, restructure README, move detail to `docs/reference.md`, fix internal links and anchors.
3. Re-verify the demo output against the v0.4.0 tag using fictional data only.
4. Run required gates: `ruff check .`, `mypy src`, `pytest -q`, `python scripts/check_links.py`, `git diff --check`.
5. Review the full diff for scope, secrets, PII/PHI and misleading release claims.
6. Open one draft PR. Merge, tags and releases stay with the user.
