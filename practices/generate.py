# --------------------------------------------------------------------------------
# practices.generate: render the masters into generated/
# --------------------------------------------------------------------------------
# Run it from the clone root: uv run --locked python -m practices.generate
# --------------------------------------------------------------------------------

import sys
from functools import partial
from pathlib import Path

from practices.command.command_runner import REPO_DIR, run_command
from practices.command.usage_error import UsageError
from practices.generated.generated_folder import GENERATED_FOLDER, write_generated_folder
from practices.masters.masters_reader import read_masters
from practices.rendering.renderer import render_all


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

_COMMAND_NAME = "practices.generate"


# --------------------------------------------------------------------------------
# The command
# --------------------------------------------------------------------------------
# The whole map renders first, so a broken master stops the run before
# anything under generated/ is touched.
# --------------------------------------------------------------------------------

def main(argument_list: list[str], repo_dir: Path = REPO_DIR) -> int:
    return run_command(_COMMAND_NAME, partial(_generate, argument_list, repo_dir))


# --------------------------------------------------------------------------------

def _generate(argument_list: list[str], repo_dir: Path) -> None:
    if argument_list:
        raise UsageError("")

    masters = read_masters(repo_dir)
    generated_file_by_path_map = render_all(masters, repo_dir)

    write_generated_folder(repo_dir, generated_file_by_path_map)

    print(f"{_COMMAND_NAME}: wrote {len(generated_file_by_path_map)} files under {GENERATED_FOLDER}/")


# --------------------------------------------------------------------------------
# Main / Entry Point
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
