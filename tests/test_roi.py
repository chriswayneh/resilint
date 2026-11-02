"""Tests for resilint roi."""

from pathlib import Path

import pytest

from resilint.cli import main
from resilint.loader import load, normalize
from tests.helpers import _write, good_vendor


def test_export_roi(tmp_path):
    out = tmp_path / "roi"
    out.mkdir()
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(out)]) == 0
    before = (out / "README.txt").read_text()
    (out / "b_06_01_functions.csv").write_text("mine")
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(out)]) == 2
    assert (out / "b_06_01_functions.csv").read_text() == "mine"
    assert (out / "README.txt").read_text() == before
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(out), "--force"]) == 0
    names = sorted(p.name for p in out.iterdir())
    assert names == ["README.txt", "b_02_02_links.csv", "b_05_01_providers.csv",
                     "b_06_01_functions.csv"]
    prov = (out / "b_05_01_providers.csv").read_text().splitlines()
    assert prov[0].startswith("provider_id,lei,legal_name")
    assert any(line.startswith("example-cloud-wms,") for line in prov)
    assert "not legal advice" in (out / "README.txt").read_text()
    assert "order-fulfilment,Order fulfilment,Yes,4" in (out / "b_06_01_functions.csv").read_text()


def test_export_roi_csv_injection_neutralized():
    from resilint.roi import export
    reg = normalize({"vendors": [good_vendor(name="=HYPERLINK(1)", id="@v")]})
    prov = export(reg)["b_05_01_providers.csv"]
    assert "'=HYPERLINK(1)" in prov and "'@v" in prov
    assert "\n=" not in prov and ",=" not in prov


def test_export_roi_bad_out_dir(tmp_path, symlink_supported):
    assert main(["export-roi", "examples/vendors.yaml",
                 "--out-dir", str(tmp_path / "missing")]) == 2
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(link)]) == 2
    assert not list(real.iterdir())
    bad = _write(tmp_path, "bad.yaml", "vendors: notalist")
    assert main(["export-roi", str(bad), "--out-dir", str(real)]) == 2


def test_export_roi_respects_output_root(tmp_path, monkeypatch):
    ws = tmp_path / "ws"
    ws.mkdir()
    other = tmp_path / "other"
    other.mkdir()
    monkeypatch.setenv("RESILINT_OUTPUT_ROOT", str(ws))
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(other)]) == 2
    assert not list(other.iterdir())


def test_roi_critical_or_important_mapping():
    from resilint.roi import export
    procs = [{"id": "a", "criticality": "critical"}, {"id": "b", "criticality": "high"},
             {"id": "c", "criticality": "medium"}, {"id": "d", "criticality": "low"}, {"id": "e"}]
    out = export(normalize({"vendors": [good_vendor()], "processes": procs}))
    rows = out["b_06_01_functions.csv"].splitlines()[1:]
    got = {r.split(",")[0]: r.split(",")[2] for r in rows}
    assert got == {"a": "Yes", "b": "Yes", "c": "No", "d": "No", "e": "Assessment not performed"}
    assert "Contractual arrangements - specific information" in out["README.txt"]
    assert "partial column set" in out["README.txt"]


def test_export_roi_trailing_slash_symlink_refused(tmp_path, symlink_supported):
    p = tmp_path / "p"
    real = tmp_path / "real"
    p.mkdir()
    real.mkdir()
    (p / "l").symlink_to(real, target_is_directory=True)
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(p / "l") + "/"]) == 2
    assert not list(real.iterdir())


@pytest.mark.parametrize("val", [" =cmd|x!A0", " \t@x", "\r=1+1", "\n=1+1", "\uff1d1+1",
                                 "-1", "+44 20", "|x", "%x", "\u3000=1"])
def test_cell_formula_variants_neutralized(val):
    from resilint.roi import _cell
    out = _cell(val)
    assert out.startswith("'")
    assert "\r" not in out and "\n" not in out


def test_cell_plain_values_untouched():
    from resilint.roi import _cell
    assert _cell("Example Co") == "Example Co"
    assert _cell(4.0) == "4"


def test_cell_keeps_original_text_when_safe_or_prefixed():
    from resilint.roi import _cell
    assert _cell("Ｅｘａｍｐｌｅ Ｃｏ") == "Ｅｘａｍｐｌｅ Ｃｏ"
    assert _cell("ﬁnance") == "ﬁnance"
    assert _cell("＝1+1") == "'＝1+1"


def test_export_force_validates_all_targets_before_writing(tmp_path, symlink_supported):
    from resilint.roi import export
    reg = load("examples/vendors.yaml")
    names = list(export(reg))
    out = tmp_path / "roi"
    out.mkdir()
    for n in names[:-1]:
        (out / n).write_text("old")
    victim = tmp_path / "victim.txt"
    victim.write_text("keep")
    (out / names[-1]).symlink_to(victim)
    assert main(["export-roi", "examples/vendors.yaml", "--out-dir", str(out), "--force"]) == 2
    assert victim.read_text() == "keep"
    assert all((out / n).read_text() == "old" for n in names[:-1])


def test_export_force_refuses_input_as_target_before_writing(tmp_path):
    from resilint.roi import export
    names = list(export(load("examples/vendors.yaml")))
    out = tmp_path / "roi"
    out.mkdir()
    for n in names[:-1]:
        (out / n).write_text("old")
    reg = out / names[-1]
    reg.write_bytes(Path("examples/vendors.yaml").read_bytes())
    assert main(["export-roi", str(reg), "--out-dir", str(out), "--force"]) == 2
    assert all((out / n).read_text() == "old" for n in names[:-1])
