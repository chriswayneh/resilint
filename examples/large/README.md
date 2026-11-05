# Fictional 500-vendor validation register

All identities, contacts and drill events here are synthetic. Contacts use the reserved `example.test` domain. Do not treat this register, policy or drill log as actual resilience evidence or operational advice.

The register has 500 unique vendors, evenly split across four criticality levels, and four shared critical processes. It deliberately includes missing commitments, recovery/RTO mismatches, concentration and missing evidence. Historical drill fixtures exercise failure/partial overlays; missing dates keep expectations independent of the current date.

From the repository root, using the candidate/development CLI:

```bash
resilint check examples/large/vendors.yaml --drills examples/large/drills.yaml --format json --output report.json
resilint check examples/large/vendors.yaml --drills examples/large/drills.yaml --config examples/large/config.yaml --format md --output report.md
```

The first command deliberately exits 1 because high findings exist. The explicit example configuration raises the failure threshold and concentration limit, so the second exits 0 while retaining the other findings. It is named `config.yaml` to avoid implicitly changing checks run from this directory.

Copy the three YAML inputs into a temporary workspace before experimenting with a baseline or recording additional fictional drills. Create a separate empty directory for `export-roi --out-dir`; exported tables retain their draft/not-legal-advice disclaimer. Do not overwrite the checked-in fixtures with operational records.

`tests/test_large_register.py` exercises every report format and all nine rules, JSON schema/SARIF parity, config, baseline/new identities, failed-to-passing drill overlay, RoI counts and input-byte preservation in the existing platform matrix. The separate 10,000-vendor performance gate remains unchanged.

To deliberately regenerate only the synthetic register after reviewing the generator:

```bash
python examples/large/generate.py
```
