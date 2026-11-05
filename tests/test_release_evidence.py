"""Release evidence must exclude local inventory and reject artifact substitution."""

import copy
import hashlib
import json
import runpy
from pathlib import Path

import pytest

helpers = runpy.run_path(str(Path(__file__).resolve().parents[1]
                             / "scripts/release_evidence.py"))


def raw_sbom():
    return {"metadata": {"component": {"name": "resilint", "version": "1.0.0-rc1",
                                       "bom-ref": "root"}, "private": "synthetic-local"},
            "components": [{"name": "PyYAML", "version": "6.0.3", "bom-ref": "yaml",
                            "properties": [{"name": "local-path", "value": "/synthetic"}]},
                           {"name": "pip", "version": "1", "bom-ref": "pip"}],
            "dependencies": [{"ref": "root", "dependsOn": ["yaml"]},
                             {"ref": "yaml"}, {"ref": "pip"}]}


def test_sbom_is_minimal_runtime_inventory():
    raw = raw_sbom()
    before = copy.deepcopy(raw)
    sbom = helpers["runtime_sbom"](raw, "1.0.0rc1", [("PyYAML", "6.0.3")])
    assert raw == before
    assert [item["name"] for item in sbom["components"]] == ["PyYAML"]
    assert sbom["metadata"]["component"]["version"] == "1.0.0rc1"
    text = json.dumps(sbom)
    for excluded in ("synthetic", "properties", '"pip"', "private"):
        assert excluded not in text


@pytest.mark.parametrize("change", ["missing", "version", "duplicate", "graph", "root",
                                   "extra-package", "extra-dependency", "disconnected"])
def test_sbom_rejects_incomplete_or_mismatched_identity(change):
    raw = raw_sbom()
    if change == "missing":
        raw["components"] = []
    elif change == "version":
        raw["components"][0]["version"] = "0"
    elif change == "duplicate":
        raw["components"].append(copy.deepcopy(raw["components"][0]))
    elif change == "graph":
        raw["dependencies"] = []
    elif change == "extra-package":
        raw["components"].append({"name": "unexpected", "version": "1", "bom-ref": "x"})
    elif change == "extra-dependency":
        raw["dependencies"][0]["dependsOn"].append("pip")
    elif change == "disconnected":
        raw["dependencies"][0]["dependsOn"] = []
    else:
        raw["metadata"]["component"]["name"] = "other"
    with pytest.raises(ValueError):
        helpers["runtime_sbom"](raw, "1.0.0rc1", [("PyYAML", "6.0.3")])


def artifact_tree(path):
    names = helpers["expected_names"]("1.0.0")
    for name in names:
        (path / name).write_bytes(b"synthetic release fixture")
    (path / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256((path / name).read_bytes()).hexdigest()}  {name}\n"
        for name in sorted(names)), encoding="utf-8")


@pytest.mark.parametrize("change", [None, "bytes", "extra", "missing", "duplicate", "path"])
def test_downloaded_artifacts_require_exact_membership_and_bytes(tmp_path, change):
    artifact_tree(tmp_path)
    manifest = tmp_path / "SHA256SUMS"
    if change == "bytes":
        (tmp_path / "resilint.cdx.json").write_bytes(b"substituted")
    elif change == "extra":
        (tmp_path / "unexpected.txt").write_text("synthetic")
    elif change == "missing":
        manifest.write_text("", encoding="utf-8")
    elif change == "duplicate":
        manifest.write_text(manifest.read_text() * 2, encoding="utf-8")
    elif change == "path":
        manifest.write_text("a" * 64 + "  ../outside\n", encoding="utf-8")
    if change is None:
        helpers["verify"](tmp_path, "1.0.0")
    else:
        with pytest.raises(ValueError):
            helpers["verify"](tmp_path, "1.0.0")


def test_release_evidence_keeps_publication_permissions_isolated():
    import re

    import yaml

    root = Path(__file__).resolve().parents[1]
    workflow = yaml.load((root / ".github/workflows/release.yml").read_text(
        encoding="utf-8"), Loader=yaml.BaseLoader)
    assert workflow["on"] == {"push": {"tags": ["v*"]}}
    assert workflow["permissions"] == {"contents": "read"}
    jobs = workflow["jobs"]
    assert jobs["testpypi"]["needs"] == ["build", "attest"]
    assert jobs["attest"]["permissions"] == {
        "contents": "read", "id-token": "write", "attestations": "write"}
    assert jobs["github-release"]["permissions"] == {
        "contents": "write", "attestations": "read"}
    assert jobs["github-release"]["needs"] == ["build", "attest", "verify-testpypi", "pypi"]
    condition = jobs["github-release"]["if"]
    for guard in ("needs.attest.result == 'success'", "needs.verify-testpypi.result == 'success'",
                  "needs.pypi.result == 'success'", "needs.build.outputs.stable != 'true'"):
        assert guard in condition
    for job in jobs.values():
        for step in job["steps"]:
            if "uses" in step:
                assert re.fullmatch(r"[\w-]+/[\w-]+@[0-9a-f]{40}", step["uses"])
                if "checkout@" in step["uses"]:
                    assert step["with"]["persist-credentials"] == "false"
    self_test = yaml.load((root / ".github/workflows/release-evidence.yml").read_text(
        encoding="utf-8"), Loader=yaml.BaseLoader)
    assert self_test["permissions"] == {"contents": "read"}
    assert "permissions" not in self_test["jobs"]["evidence"]
    assert "environment" not in self_test["jobs"]["evidence"]
