"""Tests for resilint drills."""

from datetime import date

import pytest

from resilint.cli import main
from resilint.loader import load
from resilint.rules import check
from tests.helpers import TODAY, good_vendor


def _reg(tmp_path, **kw):
    import yaml
    p = tmp_path / "reg.yaml"
    p.write_text(yaml.safe_dump({"vendors": [good_vendor(last_tested="2024-01-01", **kw)],
                                 "processes": [{"id": "p1", "rto_hours": 4}]}))
    return p


def _rec(reg, log, *extra):
    return main(["drill", "record", str(reg), "--vendor", "v1", "--log", str(log), *extra])


def test_drill_pass_updates_last_tested(tmp_path, capsys):
    reg, log = _reg(tmp_path), tmp_path / "drills.yaml"
    assert main(["check", str(reg), "--fail-on", "medium"]) == 1
    assert _rec(reg, log, "--kind", "tabletop", "--result", "pass",
                "--date", date.today().isoformat()) == 0
    assert "last-tested date updated" in capsys.readouterr().out
    assert main(["check", str(reg), "--drills", str(log), "--fail-on", "medium"]) == 0


def test_drill_fail_raises_rl009_and_keeps_last_tested(tmp_path, capsys):
    from resilint.drills import apply, load_log
    reg, log = _reg(tmp_path), tmp_path / "drills.yaml"
    assert _rec(reg, log, "--kind", "test", "--result", "pass", "--date", "2026-05-01") == 0
    assert _rec(reg, log, "--kind", "test", "--result", "fail", "--date", "2026-09-01") == 0
    r = load(reg)
    apply(r, load_log(log))
    assert r["vendors"][0]["last_tested"] == date(2026, 5, 1)
    ids = [f.rule_id for f in check(r, today=TODAY)]
    assert "RL009" in ids and "RL005" not in ids


def test_drill_latest_wins_regardless_of_log_order(tmp_path):
    from resilint.drills import apply, load_log
    reg, log = _reg(tmp_path), tmp_path / "drills.yaml"
    _rec(reg, log, "--kind", "test", "--result", "pass", "--date", "2026-09-01")
    _rec(reg, log, "--kind", "test", "--result", "fail", "--date", "2026-01-01")
    r = load(reg)
    apply(r, load_log(log))
    assert "RL009" not in [f.rule_id for f in check(r, today=TODAY)]


def test_drill_register_untouched(tmp_path):
    reg = _reg(tmp_path)
    before = reg.read_bytes()
    _rec(reg, tmp_path / "d.yaml", "--kind", "test", "--result", "pass")
    assert reg.read_bytes() == before


def test_drill_default_log_next_to_register(tmp_path):
    reg = _reg(tmp_path)
    assert main(["drill", "record", str(reg), "--vendor", "v1", "--kind", "test",
                 "--result", "partial"]) == 0
    assert (tmp_path / "drills.yaml").is_file()


@pytest.mark.parametrize("extra", [
    ["--vendor", "nope"], ["--date", "2026-13-01"], ["--notes", "x" * 501],
])
def test_drill_record_rejects_bad_input(tmp_path, extra):
    reg = _reg(tmp_path)
    args = ["drill", "record", str(reg), "--vendor", "v1", "--kind", "test", "--result", "pass",
            "--log", str(tmp_path / "d.yaml")]
    assert main(args + extra) == 2
    assert not (tmp_path / "d.yaml").exists()


def test_drill_log_refuses_symlink_and_register(tmp_path, symlink_supported):
    reg = _reg(tmp_path)
    target = tmp_path / "victim.txt"
    target.write_text("keep")
    (tmp_path / "link.yaml").symlink_to(target)
    assert _rec(reg, tmp_path / "link.yaml", "--kind", "test", "--result", "pass") == 2
    assert target.read_text() == "keep"
    assert _rec(reg, reg, "--kind", "test", "--result", "pass") == 2


def test_drill_log_respects_output_root(tmp_path, monkeypatch):
    reg = _reg(tmp_path)
    root = tmp_path / "root"
    root.mkdir()
    monkeypatch.setenv("RESILINT_OUTPUT_ROOT", str(root))
    assert _rec(reg, tmp_path / "d.yaml", "--kind", "test", "--result", "pass") == 2


@pytest.mark.parametrize("text", [
    "drills: &a [*a]",
    "drills: [{vendor: v1, date: 2026-01-01, kind: test, result: maybe}]",
    "drills: [{vendor: v1, date: 2026-01-01, kind: test, result: pass, notes: [1]}]",
    "drills: [{vendor: ghost, date: 2026-01-01, kind: test, result: pass}]",
    "- just a list",
])
def test_drill_log_invalid(tmp_path, text):
    reg = _reg(tmp_path)
    log = tmp_path / "d.yaml"
    log.write_text(text)
    assert main(["check", str(reg), "--drills", str(log)]) == 2


def test_drill_log_size_cap(tmp_path):
    reg = _reg(tmp_path)
    log = tmp_path / "d.yaml"
    log.write_bytes(b"#" * (5 * 1024 * 1024 + 1))
    assert main(["check", str(reg), "--drills", str(log)]) == 2


def test_drill_in_regmap_and_sarif(tmp_path, capsys):
    reg, log = _reg(tmp_path), tmp_path / "d.yaml"
    _rec(reg, log, "--kind", "tabletop", "--result", "fail")
    capsys.readouterr()
    main(["check", str(reg), "--drills", str(log), "--format", "regmap"])
    out = capsys.readouterr().out
    assert "RL009" in out and "not legal advice" in out
    main(["check", str(reg), "--drills", str(log), "--format", "sarif"])
    assert "RL009" in capsys.readouterr().out


def test_drill_concurrent_records_lose_nothing(tmp_path):
    import subprocess
    import sys
    reg, log = _reg(tmp_path), tmp_path / "d.yaml"
    cmd = [sys.executable, "-m", "resilint.cli", "drill", "record", str(reg), "--vendor", "v1",
           "--kind", "test", "--result", "pass", "--date", "2026-01-01", "--log", str(log)]
    procs = [subprocess.Popen(cmd + ["--notes", str(i)], stdout=subprocess.DEVNULL,
                              stderr=subprocess.PIPE) for i in range(6)]
    try:
        errors = [p.communicate(timeout=20)[1] for p in procs]
    finally:
        for p in procs:
            if p.poll() is None:
                p.kill()
                p.communicate()
    codes = [p.returncode for p in procs]
    from resilint.drills import load_log
    results = list(zip(codes, errors))
    assert all(c in (0, 2) for c in codes), results
    assert all(b"locked" in err for code, err in results if code == 2), results
    records = load_log(log)
    expected = {str(i) for i, code in enumerate(codes) if code == 0}
    assert len(records) == len(expected) >= 1
    assert {d["notes"] for d in records} == expected


def test_drill_lock_held_fails_cleanly(tmp_path, capsys):
    import os
    reg, log = _reg(tmp_path), tmp_path / "d.yaml"
    fd = os.open(str(log) + ".lock", os.O_RDWR | os.O_CREAT, 0o644)
    if os.name == "nt":
        import msvcrt
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    else:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_EX)
    try:
        assert _rec(reg, log, "--kind", "test", "--result", "pass") == 2
        assert "locked" in capsys.readouterr().err
        assert not log.exists()
    finally:
        os.close(fd)


@pytest.mark.parametrize("invalid_first", [False, True])
def test_drill_lock_released_after_record(tmp_path, invalid_first):
    reg, log = _reg(tmp_path), tmp_path / "d.yaml"
    result = "fail" if invalid_first else "pass"
    vendor = "missing" if invalid_first else "v1"
    assert main(["drill", "record", str(reg), "--vendor", vendor,
                 "--log", str(log), "--kind", "test", "--result", result]) == (
                     2 if invalid_first else 0)
    assert _rec(reg, log, "--kind", "test", "--result", "pass") == 0
    from resilint.drills import load_log
    assert len(load_log(log)) == (1 if invalid_first else 2)


def test_drill_lock_io_error_closes_file(tmp_path, monkeypatch, capsys):
    import errno
    import os

    from resilint import cli

    descriptors = []

    def fail(fd):
        descriptors.append(fd)
        raise OSError(errno.EIO, "lock unavailable")

    monkeypatch.setattr(cli, "_try_lock", fail)
    reg, log = _reg(tmp_path), tmp_path / "d.yaml"
    assert _rec(reg, log, "--kind", "test", "--result", "pass") == 2
    assert "cannot lock" in capsys.readouterr().err
    assert not log.exists()
    assert len(descriptors) == 1
    with pytest.raises(OSError) as error:
        os.fstat(descriptors[0])
    assert error.value.errno == errno.EBADF


def test_drill_future_date_rejected(tmp_path):
    from datetime import timedelta
    reg, log = _reg(tmp_path), tmp_path / "d.yaml"
    future = (date.today() + timedelta(days=1)).isoformat()
    assert _rec(reg, log, "--kind", "test", "--result", "pass", "--date", future) == 2
    log.write_text(f"drills: [{{vendor: v1, date: '{future}', kind: test, result: pass}}]")
    assert main(["check", str(reg), "--drills", str(log)]) == 2


def test_drill_record_validates_existing_log(tmp_path):
    reg, log = _reg(tmp_path), tmp_path / "d.yaml"
    log.write_text("drills: [{vendor: ghost, date: '2026-01-01', kind: test, result: pass}]")
    before = log.read_text()
    assert _rec(reg, log, "--kind", "test", "--result", "pass") == 2
    assert log.read_text() == before


def test_drill_log_same_as_input_names_log_option(tmp_path, capsys):
    reg = _reg(tmp_path)
    assert _rec(reg, reg, "--kind", "test", "--result", "pass") == 2
    assert "--log must not be the input file" in capsys.readouterr().err


def test_drill_no_temp_files_left(tmp_path):
    reg, log = _reg(tmp_path), tmp_path / "d.yaml"
    assert _rec(reg, log, "--kind", "test", "--result", "pass") == 0
    assert not list(tmp_path.glob(".drills-*"))
