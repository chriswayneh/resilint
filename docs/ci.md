# CI integration

Run resilint in a trusted project checkout with Python 3.10 or newer. The examples below use Python 3.12 and a pinned development commit; package-index installation will replace this source install once the v1 package is published. Installing dependencies needs network access. Checking registers is offline.

## Generic CI

Install in your CI environment, then use the check's status directly:

```bash
python -m pip install "resilint @ https://github.com/chriswayneh/resilint/archive/0f0f6d5ab9ea14546bbc475fb9f38c9e3e1fedeb.tar.gz"
resilint check vendors.yaml --fail-on high --format json --output resilint.json
```

Exit 0 passes, exit 1 means findings reached the threshold, and exit 2 means an input/output error. A valid check writes its report before returning 0 or 1. Do not discard the status with `|| true` when this is your gate. Configuration defaults and ignores come from the checkout's [`.resilint.yaml`](config.md); explicit CLI thresholds override that file. Add `--baseline baseline.json` to gate only new identities, or `--drills drills.yaml` to apply recorded drill results.

Replace `vendors.yaml` with your register. For a local smoke test in this repository, use `examples/vendors.yaml`: it intentionally returns 1 and writes a report containing high findings. A register containing `vendors: []` returns 0; a missing register returns 2 without creating a report.

## GitLab CI

Add this job to `.gitlab-ci.yml`:

```yaml
resilience:
  image: python:3.12
  script:
    - python -m pip install "resilint @ https://github.com/chriswayneh/resilint/archive/0f0f6d5ab9ea14546bbc475fb9f38c9e3e1fedeb.tar.gz"
    - resilint check vendors.yaml --fail-on high --format json --output resilint.json
  artifacts:
    when: always
    paths:
      - resilint.json
    expire_in: 7 days
```

The job retains its failing check status while making an existing report available after threshold findings. Invalid input may produce no artifact. Reports contain vendor identifiers and findings; configure artifact access and retention for your register data. See [GitLab's artifact documentation](https://docs.gitlab.com/ci/jobs/job_artifacts/).

## Azure Pipelines

Add this to `azure-pipelines.yml`:

```yaml
trigger:
  - main
pool:
  vmImage: ubuntu-latest
steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.12'
  - script: python -m pip install "resilint @ https://github.com/chriswayneh/resilint/archive/0f0f6d5ab9ea14546bbc475fb9f38c9e3e1fedeb.tar.gz"
    displayName: Install resilint
  - script: resilint check vendors.yaml --fail-on high --format json --output resilint.json
    displayName: Check vendor resilience
```

The check step fails on either threshold findings or invalid input. The report remains in the agent workspace when generated; this recipe does not publish it. Python selection follows [Microsoft's Python pipeline guidance](https://learn.microsoft.com/en-us/azure/devops/pipelines/ecosystems/python?view=azure-devops).

## GitHub Actions

See the [SHA-pinned SARIF upload workflow](../examples/workflows/resilint-sarif.yml) and the [Action inputs and outputs](reference.md#github-action). The upload example grants `security-events: write` only to its upload job, sends completed reports to GitHub Code Scanning, and then enforces the original threshold status. Review repository access before uploading register-derived data.
