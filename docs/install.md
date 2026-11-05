# Installation

The commands below target `1.0.0`. Published-version availability is listed on [PyPI](https://pypi.org/project/resilint/) and [Releases](https://github.com/chriswayneh/resilint/releases). The separately published [rc1 candidate on TestPyPI](https://test.pypi.org/project/resilint/1.0.0rc1/) is retained for release-validation reproduction.

Use Python 3.10 or newer. CI covers Python 3.10, 3.12 and 3.13 on Linux, Windows and macOS. Installation can access package indexes; checks and exports run offline.

## PyPI installation

Use the exact published stable version for a controlled install. TestPyPI candidates are separate from production PyPI releases.

For a pinned install in your virtual environment:

```bash
python -m pip install "resilint==1.0.0"
resilint --version
```

For an isolated CLI installation with [pipx](https://pipx.pypa.io/stable/installation/):

```bash
pipx install resilint
resilint --version
```

`pipx install resilint` selects the latest stable version on PyPI. Use `pipx install "resilint==1.0.0"` when a fixed version is required. After reviewing a later release, use `pipx upgrade resilint` for an unpinned install, or deliberately install the newly selected pinned version. No Git checkout is needed for a PyPI install.

Prefer a dedicated virtual environment for pip installations:

```bash
python -m venv .venv
# Linux/macOS:
. .venv/bin/activate
```

On Windows PowerShell, use `.venv\Scripts\Activate.ps1` or run `.venv\Scripts\python.exe` directly if activation is restricted. Using that interpreter's `-m pip` installs into the intended environment.

## Git-release alternative

```bash
python -m pip install "git+https://github.com/chriswayneh/resilint.git@v1.0.0"
resilint --version
```

This source installation needs Git and selects the immutable stable version tag once published. You can also pin its full reviewed commit SHA for controlled adoption.

## Installed quick start

After installing the selected release in an isolated environment, run these commands in an empty directory outside the source checkout:

```bash
resilint --version
resilint init vendors.yaml
resilint check vendors.yaml --format json --fail-on critical
resilint explain RL004
```

The fictional starter intentionally reports RL004, RL005 and RL008. This example uses the critical failure threshold, so the check returns 0 while retaining those findings. The default high threshold returns 1. Replace fictional data with reviewed commitments before operational use.

The read-only [index-install workflow](../.github/workflows/index-install.yml) runs this exact quick start against a real TestPyPI download on Linux, Windows and macOS. It verifies the wheel against the reviewed Git source before installation, then checks installed package/resource identity. Its version input must match the checked-out release metadata; passing source tests or mocked downloads do not substitute for those three actual index installs.

## Development checkout

```bash
git clone https://github.com/chriswayneh/resilint.git
cd resilint
python -m pip install -e ".[dev]"
resilint --help
```

Development checkouts may contain unreleased changes beyond the version identifier. Pin a reviewed commit for CI rather than relying on a moving branch. See [CI recipes](ci.md), [usage](usage.md) and the [contributor working guide](../roadmap/README.md).
