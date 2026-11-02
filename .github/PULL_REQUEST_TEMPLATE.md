## Problem and behavior

Task ID:

Describe the concrete trigger, resulting behavior and any compatibility effect. Use fictional data only; exclude real vendor contracts, contacts, credentials and personal data.

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

- [ ] One roadmap task; changelog and behavior docs updated where applicable.
- [ ] Roadmap status and completion PR recorded for merge.
- [ ] New examples/tests contain fictional data only.
- [ ] Snapshot changes reviewed rather than accepted blindly.

See [CONTRIBUTING.md](https://github.com/chriswayneh/resilint/blob/main/CONTRIBUTING.md) and the [working guide](https://github.com/chriswayneh/resilint/blob/main/roadmap/README.md).
