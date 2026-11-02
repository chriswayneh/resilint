# Installation

These guides describe the development version being prepared for v1. The latest published release is v0.4.0; `init`, `explain`, configuration, baselines and Action outputs are development features until the next release.

Use Python 3.10 or newer. CI covers Python 3.10, 3.12 and 3.13 on Linux, Windows and macOS. Installation can access package indexes; checks and exports run offline.

## Published release

```bash
python -m pip install "git+https://github.com/chriswayneh/resilint.git@v0.4.0"
resilint --version
```

This source installation needs Git. Prefer a dedicated virtual environment:

```bash
python -m venv .venv
# Linux/macOS:
. .venv/bin/activate
```

On Windows PowerShell, use `.venv\Scripts\Activate.ps1` or run `.venv\Scripts\python.exe` directly if activation is restricted.

## Development checkout

```bash
git clone https://github.com/chriswayneh/resilint.git
cd resilint
python -m pip install -e ".[dev]"
resilint --help
```

The version number remains the latest release until the release-candidate bump; the working tree includes unreleased changes. Pin a reviewed commit for CI rather than relying on a moving branch. See [CI recipes](ci.md), [usage](usage.md) and the [contributor working guide](../roadmap/README.md).
