# --------------------------------------------------------------------------------
# The gate: steps run in order and the first failure stops the run
# --------------------------------------------------------------------------------

import sys
from pathlib import Path

from practices import gate


# --------------------------------------------------------------------------------
# Order and exit code
# --------------------------------------------------------------------------------

def test_the_gate_runs_every_step_in_order_and_passes(tmp_path: Path, capsys) -> None:
    step_list = [_step("s1", 0), _step("s2", 0)]

    assert gate.main([], tmp_path, step_list) == 0
    assert (tmp_path / "ran.txt").read_text() == "s1\ns2\n"
    assert capsys.readouterr().out == "practices.gate: s1\npractices.gate: s2\npractices.gate: every step passed\n"


# --------------------------------------------------------------------------------

def test_the_gate_stops_at_the_first_failing_step(tmp_path: Path, capsys) -> None:
    step_list = [_step("s1", 0), _step("s2", 3), _step("s3", 0)]

    assert gate.main([], tmp_path, step_list) == 1
    assert (tmp_path / "ran.txt").read_text() == "s1\ns2\n"
    assert "practices.gate: s2 failed" in capsys.readouterr().err


# --------------------------------------------------------------------------------

def test_the_gate_refuses_an_argument(capsys) -> None:
    assert gate.main(["extra"]) == 2
    assert capsys.readouterr().err == "Usage: practices.gate\n"


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _step(name: str, exit_code: int) -> tuple[str, list[str]]:
    script = (
        f"import pathlib, sys; "
        f"pathlib.Path('ran.txt').open('a').write('{name}\\n'); "
        f"sys.exit({exit_code})"
    )

    return name, [sys.executable, "-c", script]
