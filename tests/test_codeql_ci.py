"""Keep the CodeQL write/upload boundary separate from read-only scanners."""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_codeql_has_only_required_repository_permissions():
    text = (ROOT / ".github/workflows/codeql.yml").read_text(encoding="utf-8")
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    assert workflow["permissions"] == {"contents": "read"}
    assert set(workflow["on"]) == {"push", "pull_request"}
    assert workflow["on"]["push"] == {"branches": ["main"]}
    assert workflow["on"]["pull_request"] == {
        "branches": ["main"],
        "types": ["opened", "synchronize", "reopened", "ready_for_review"],
    }
    assert set(workflow["jobs"]) == {"python"}
    job = workflow["jobs"]["python"]
    assert job["permissions"] == {"contents": "read", "security-events": "write"}
    assert job["timeout-minutes"] == "20"
    assert "environment" not in job
    for step in job["steps"]:
        assert "run" not in step
        assert re.fullmatch(
            r"(?:actions/checkout|github/codeql-action/(?:init|analyze))@[0-9a-f]{40}",
            step["uses"],
        )
    for forbidden in ("id-token", "secrets.", "pull_request_target", "workflow_run",
                      "upload-artifact", "${{"):
        assert forbidden not in text


def test_codeql_uses_bundled_queries_and_disables_database_upload():
    workflow = yaml.load((ROOT / ".github/workflows/codeql.yml").read_text(
        encoding="utf-8"), Loader=yaml.BaseLoader)
    checkout, initialize, analyze = workflow["jobs"]["python"]["steps"]
    assert checkout["with"] == {"persist-credentials": "false"}
    assert initialize["uses"].split("@", 1)[1] == analyze["uses"].split("@", 1)[1]
    assert initialize["with"] == {
        "languages": "python", "build-mode": "none", "tools": "linked",
        "dependency-caching": "false", "queries": "security-extended",
    }
    assert analyze["with"] == {
        "category": "/language:python", "upload": "always",
        "upload-database": "false", "wait-for-processing": "true",
    }
