# --------------------------------------------------------------------------------
# practices.check: does generated/ match what the masters render to?
# --------------------------------------------------------------------------------
# Run it from the clone root: uv run --locked python -m practices.check
# --------------------------------------------------------------------------------

import sys
from functools import partial
from pathlib import Path

from practices.cli import REPO_DIR, PracticesError, UsageError, run_command
from practices.output import GENERATED_FOLDER, read_output_tree
from practices.render import render_all


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

COMMAND_NAME = "practices.check"


# --------------------------------------------------------------------------------
# Finding drift
# --------------------------------------------------------------------------------

def find_drift(repo_dir: Path) -> list[str]:
    expected_by_path_map = render_all(repo_dir)
    actual_by_path_map = read_output_tree(repo_dir)
    drift_list = []

    for output_path in sorted(set(expected_by_path_map) | set(actual_by_path_map)):
        if output_path not in actual_by_path_map:
            drift_list.append(f"missing file: {GENERATED_FOLDER}/{output_path}")
        elif output_path not in expected_by_path_map:
            drift_list.append(f"extra file: {GENERATED_FOLDER}/{output_path}")
        elif expected_by_path_map[output_path] != actual_by_path_map[output_path]:
            drift_list.append(f"changed file: {GENERATED_FOLDER}/{output_path}")

    return drift_list


# --------------------------------------------------------------------------------
# The command
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

    print(f"{COMMAND_NAME}: {GENERATED_FOLDER}/ matches the masters ({len(read_output_tree(repo_dir))} files)")


def main(argument_list: list[str], repo_dir: Path = REPO_DIR) -> int:
    return run_command(COMMAND_NAME, partial(_check_tree, argument_list, repo_dir))


# --------------------------------------------------------------------------------
# Main / Entry Point
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
