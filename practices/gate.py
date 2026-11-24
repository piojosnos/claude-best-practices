# --------------------------------------------------------------------------------
# practices.gate: the one command that must pass before a change is committed
# --------------------------------------------------------------------------------
# Run it from the clone root: uv run --locked python -m practices.gate
# It runs the linter, the drift check and the tests in order and stops at the
# first step that fails.
# --------------------------------------------------------------------------------

import subprocess
import sys
from functools import partial
from pathlib import Path

from practices.cli import REPO_DIR, run_command
from practices.errors import PracticesError, UsageError


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

COMMAND_NAME = "practices.gate"
GATE_STEP_LIST = [
    ("ruff", [sys.executable, "-m", "ruff", "check", "."]),
    ("practices.check", [sys.executable, "-m", "practices.check"]),
    ("pytest", [sys.executable, "-m", "pytest", "-q"]),
]


# --------------------------------------------------------------------------------
# The command
# --------------------------------------------------------------------------------

def _run_gate(argument_list: list[str], repo_dir: Path, step_list: list[tuple[str, list[str]]]) -> None:
    if argument_list:
        raise UsageError("")

    for step_name, command_list in step_list:
        print(f"{COMMAND_NAME}: {step_name}", flush=True)

        if subprocess.run(command_list, cwd=repo_dir, check=False).returncode != 0:
            raise PracticesError(f"{step_name} failed")

    print(f"{COMMAND_NAME}: every step passed")


def main(
    argument_list: list[str],
    repo_dir: Path = REPO_DIR,
    step_list: list[tuple[str, list[str]]] = GATE_STEP_LIST,
) -> int:
    return run_command(COMMAND_NAME, partial(_run_gate, argument_list, repo_dir, step_list))


# --------------------------------------------------------------------------------
# Main / Entry Point
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
