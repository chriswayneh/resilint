"""The draft disclaimer remains visible even in reports with no findings."""

from pathlib import Path

import pytest

from resilint.loader import normalize
from resilint.report import markdown, regmap
from resilint.roi import export
from resilint.rules import DISCLAIMER


@pytest.mark.parametrize("render", [markdown, regmap])
def test_disclaimer_in_empty_report(render):
    assert DISCLAIMER in render([], normalize({"vendors": []}))


def test_disclaimer_in_export_and_readme():
    assert DISCLAIMER in export(normalize({"vendors": []}))["README.txt"]
    readme = Path(__file__).resolve().parents[1] / "README.md"
    assert DISCLAIMER in readme.read_text(encoding="utf-8")
