# --------------------------------------------------------------------------------
# practices.check: does generated/ match what the masters render to?
# --------------------------------------------------------------------------------
# Run it from the clone root: uv run --locked python -m practices.check
# --------------------------------------------------------------------------------

import difflib
import sys
from functools import partial
from pathlib import Path

from practices.cli import REPO_DIR, run_command
from practices.errors import PracticesError, UsageError
from practices.model import OutputFile
from practices.output import GENERATED_FOLDER, read_output_tree
from practices.reader import read_masters
from practices.render import render_all


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

_COMMAND_NAME = "practices.check"


# --------------------------------------------------------------------------------
# Finding drift
# --------------------------------------------------------------------------------
# One list entry per file: its drift line, then for a changed text file the diff.
# --------------------------------------------------------------------------------

def find_drift(repo_dir: Path) -> list[str]:
    masters = read_masters(repo_dir)
    expected_by_path_map = render_all(masters, repo_dir)
    actual_by_path_map = read_output_tree(repo_dir)
    drift_list = []

    for output_path in sorted(set(expected_by_path_map) | set(actual_by_path_map)):
        if output_path not in actual_by_path_map:
            drift_list.append(f"missing file: {GENERATED_FOLDER}/{output_path}")
        elif output_path not in expected_by_path_map:
            drift_list.append(f"extra file: {GENERATED_FOLDER}/{output_path}")
        else:
            expected = expected_by_path_map[output_path]
            actual = actual_by_path_map[output_path]

            if expected.content != actual.content:
                drift_list.append(_describe_changed_file(output_path, expected, actual))
            elif expected.executable != actual.executable:
                drift_list.append(f"changed mode: {GENERATED_FOLDER}/{output_path}")

    return drift_list


# --------------------------------------------------------------------------------

def _describe_changed_file(output_path: str, expected: OutputFile, actual: OutputFile) -> str:
    drift_line = f"changed file: {GENERATED_FOLDER}/{output_path}"

    try:
        expected_line_list = expected.content.decode("utf-8").splitlines()
        actual_line_list = actual.content.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return drift_line

    diff_line_list = difflib.unified_diff(
        expected_line_list,
        actual_line_list,
        fromfile=f"expected {output_path}",
        tofile=f"{GENERATED_FOLDER}/{output_path}",
        n=3,
        lineterm="",
    )

    return "\n".join([drift_line, *diff_line_list])


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

    print(f"{_COMMAND_NAME}: {GENERATED_FOLDER}/ matches the masters ({len(read_output_tree(repo_dir))} files)")


# --------------------------------------------------------------------------------

def main(argument_list: list[str], repo_dir: Path = REPO_DIR) -> int:
    return run_command(_COMMAND_NAME, partial(_check_tree, argument_list, repo_dir))


# --------------------------------------------------------------------------------
# Main / Entry Point
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
