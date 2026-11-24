# --------------------------------------------------------------------------------
# practices.check: does generated/ match what the masters render to?
# --------------------------------------------------------------------------------
# Run it from the clone root: uv run --locked python -m practices.check
# --------------------------------------------------------------------------------

import sys
from functools import partial
from pathlib import Path

from practices.command.command_runner import REPO_DIR, run_command
from practices.command.usage_error import UsageError
from practices.error.practices_error import PracticesError
from practices.generated.drift_finder import find_drift
from practices.generated.generated_folder import GENERATED_FOLDER, read_generated_folder


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

_COMMAND_NAME = "practices.check"


# --------------------------------------------------------------------------------
# The command
# --------------------------------------------------------------------------------

def main(argument_list: list[str], repo_dir: Path = REPO_DIR) -> int:
    return run_command(_COMMAND_NAME, partial(_check_tree, argument_list, repo_dir))


# --------------------------------------------------------------------------------

def _check_tree(argument_list: list[str], repo_dir: Path) -> None:
    if argument_list:
        raise UsageError("")

    drift_list = find_drift(repo_dir)

    for drift_line in drift_list:
        print(drift_line)

    if drift_list:
        raise PracticesError(
            f"{len(drift_list)} generated files differ from the masters; "
            "run: uv run --locked python -m practices.generate"
        )

    print(f"{_COMMAND_NAME}: {GENERATED_FOLDER}/ matches the masters ({len(read_generated_folder(repo_dir))} files)")


# --------------------------------------------------------------------------------
# Main / Entry Point
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
