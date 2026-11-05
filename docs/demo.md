# Terminal demo

The README GIF replays actual output captured from the published `resilint==1.0.0` package on 2026-11-05 UTC, using only its fictional starter register. The animation wraps long lines and adjusts timing for readability.

## What it shows

1. Confirm the version and create `vendors.yaml` with `resilint init`.
2. Check the starter: RL004 flags the missing exit plan, RL005 the missing resilience-test date and RL008 the missing contact-verification date.
3. Explain RL004 to see its meaning, an illustrative fix and draft regulation references.

The version, creation and explanation commands return 0. The default check returns **1**, because the starter has a high finding. The animation ends with RL004's explanation and draft references.

## Run it yourself

Use Python 3.10 or newer and an isolated environment as described in the [installation guide](install.md). Install the published version, then run in an empty directory:

```bash
python -m pip install "resilint==1.0.0"
resilint --version
resilint init vendors.yaml
resilint check vendors.yaml
resilint explain RL004
```

If you put these commands in a script that stops on nonzero status, handle the check's expected exit 1 before continuing. The check and explanation leave the starter unchanged. Creation refuses to overwrite an existing file.

Installation can access PyPI; the checks and explanation run locally and offline. Replace fictional commitments with reviewed evidence for operational use, and keep real vendor data out of public demos.

## Text alternative

The [written README demo](../README.md#demo) provides another fictional register and captured text output. [Rule descriptions](rules.md) cover RL001–RL009. Regulation references remain draft mapping, not legal advice.

The captions describe each stage; commands and output come from a local capture of the published package. The existing written examples and this guide provide a text alternative to the animation.
