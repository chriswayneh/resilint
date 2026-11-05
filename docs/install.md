# Installation

These guides describe the source prepared for `v1.0.0-rc1`. See [Releases](https://github.com/chriswayneh/resilint/releases) for published candidate builds. The latest published stable release is v0.4.0; `init`, `explain`, configuration, baselines and Action outputs are included in candidate source and remain unavailable in that older stable release.

Use Python 3.10 or newer. CI covers Python 3.10, 3.12 and 3.13 on Linux, Windows and macOS. Installation can access package indexes; checks and exports run offline.

## PyPI installation after stable v1 publication

The first production PyPI release is planned as `1.0.0`. These commands become usable after that version is published; until then, use the Git-release alternative below. The release candidate is tested separately through TestPyPI and is not a production PyPI release.

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
python -m pip install "git+https://github.com/chriswayneh/resilint.git@v0.4.0"
resilint --version
```

This source installation needs Git and currently installs the published v0.4.0 release. It remains an alternative when you need a reviewed tag or commit from the source repository; it does not include development-only features until a new tag is published.

## Development checkout

```bash
git clone https://github.com/chriswayneh/resilint.git
cd resilint
python -m pip install -e ".[dev]"
resilint --help
```

The version number remains the latest release until the release-candidate bump; the working tree includes unreleased changes. Pin a reviewed commit for CI rather than relying on a moving branch. See [CI recipes](ci.md), [usage](usage.md) and the [contributor working guide](../roadmap/README.md).
