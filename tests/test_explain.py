"""Every public rule has CLI guidance without needing a register or config."""

import pytest

from resilint.cli import main
from resilint.rules import GUIDANCE, REG_NOTE, RULES


@pytest.mark.parametrize("rule_id", sorted(RULES))
def test_explain_rule(rule_id, tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".resilint.yaml").write_text("invalid config: [")
    assert main(["explain", rule_id]) == 0
    out = capsys.readouterr()
    name, severity, refs = RULES[rule_id]
    assert rule_id in out.out and name in out.out
    assert f"Severity: {severity}" in out.out
    assert GUIDANCE[rule_id][0] in out.out and GUIDANCE[rule_id][1] in out.out
    assert refs in out.out and REG_NOTE in out.out
    assert not out.err
    assert sorted(p.name for p in tmp_path.iterdir()) == [".resilint.yaml"]


def test_explain_unknown_rule(capsys):
    assert main(["explain", "RL999"]) == 2
    out = capsys.readouterr()
    assert not out.out
    assert out.err.startswith("resilint: error: <cli>:0: unknown rule")
