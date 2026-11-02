# Frequently asked questions

## Does a passing check prove compliance?

No. resilint checks recorded commitments and consistency. Regulation references and RoI exports are draft mapping, not legal advice. A passing threshold can still include lower-severity findings, and configured ignores/baselines can suppress known findings.

## Does it contact vendors or upload my register?

The CLI runs offline. Installation downloads dependencies. The optional CI recipes can publish reports to GitHub Code Scanning or CI artifacts; those reports contain register-derived data, so review the chosen service's access and retention settings.

## Why did an old finding disappear?

Review [config ignores](config.md), [baseline identities](baseline.md), criticality, and any [drill overlay](drills.md). Baseline identity excludes message/value changes, so a known issue can remain filtered after its measured value changes.

## Why does the example fail?

Examples deliberately contain gaps. Exit 1 means the check completed and findings reached the threshold. Exit 2 means input or output failed. The [starter](usage.md#create-a-register-and-understand-a-finding) intentionally has RL004, RL005 and RL008.

## Why is my CSV rejected?

Check UTF-8 encoding, the chosen delimiter, required columns, unique normalized headers and consistent row lengths. Physical CSV line numbers identify the end of a failing row, including multiline records. See [schema](schema.md).

## Why was an output refused?

Check that parent directories exist, the target is not a symlink or loaded input, and `RESILINT_OUTPUT_ROOT` permits it. `init` always refuses existing files. RoI export needs `--force` to replace existing targets. See [usage](usage.md) and [RoI exports](roi.md).

## Where do I change policy or learn a rule?

Use [`.resilint.yaml`](config.md) for project settings and `resilint explain RL004` for offline guidance. All nine rules are documented in the [rule guide](rules.md). Record actual evidence when applying an example.
