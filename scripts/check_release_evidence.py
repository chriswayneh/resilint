"""Exercise the release evidence step on Linux without attesting or publishing."""

import os
import runpy
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    workflow = yaml.load((ROOT / ".github/workflows/release.yml").read_text(
        encoding="utf-8"), Loader=yaml.BaseLoader)
    steps = [step for step in workflow["jobs"]["build"]["steps"]
             if step.get("name") == "Generate and validate runtime-only release evidence"]
    if len(steps) != 1:
        raise SystemExit("Expected one release evidence preparation step")
    release = runpy.run_path(str(ROOT / "scripts/release_metadata.py"))
    project = release["tomllib"].loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    tag = "v" + project["project"]["version"]
    version, _stable = release["metadata"](ROOT, tag)
    # This deliberately executes repository workflow code with the same read-only
    # PR boundary as the existing tests. It never invokes publication jobs.
    subprocess.run(["bash", "-eo", "pipefail", "-c", steps[0]["run"]], cwd=ROOT,
                   env={**os.environ, "RELEASE_TAG": tag, "RELEASE_VERSION": version},
                   check=True)


if __name__ == "__main__":
    main()
