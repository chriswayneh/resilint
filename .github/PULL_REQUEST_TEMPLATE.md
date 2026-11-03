## Problem and behavior

Task ID:

Describe the concrete trigger, resulting behavior and any compatibility effect. Use fictional data only; exclude real vendor contracts, contacts, credentials PHI, PII and personal data.

## Validation

Paste relevant results for:

```bash
ruff check .
mypy src
pytest -q
git diff --check
python scripts/check_links.py
```

Record the exact reviewed head, acceptance results and any material limitations. CI coverage must remain at least 90%; review the final matrix and hosted Action self-test. Code changes require an exact-head security review.

## Documentation and scope

- [ ] Design/plan and actual stage decisions recorded; delegated review is attributed to its actual reviewer.
- [ ] One roadmap task; changelog and behavior docs updated where applicable.
- [ ] Roadmap status and completion PR recorded for merge.
- [ ] New examples/tests contain fictional data only.
- [ ] Snapshot changes reviewed rather than accepted blindly.

See [CONTRIBUTING.md](https://github.com/chriswayneh/resilint/blob/main/CONTRIBUTING.md) and the [working guide](https://github.com/chriswayneh/resilint/blob/main/roadmap/README.md).

Follow [AGENTS.md](https://github.com/chriswayneh/resilint/blob/main/AGENTS.md) and the [workflow records](https://github.com/chriswayneh/resilint/blob/main/aidlc-docs/README.md). Stage review does not grant user-owned GitHub approval, merge, release or settings authority.
