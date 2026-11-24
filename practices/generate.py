# --------------------------------------------------------------------------------
# practices.generate: render the masters into generated/
# --------------------------------------------------------------------------------
# Run it from the clone root: uv run --locked python -m practices.generate
# --------------------------------------------------------------------------------

import sys
from functools import partial
from pathlib import Path

from practices.cli import REPO_DIR, run_command
from practices.errors import UsageError
from practices.output import GENERATED_FOLDER, write_output
from practices.reader import read_masters
from practices.render import render_all


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

def _generate(argument_list: list[str], repo_dir: Path) -> None:
    if argument_list:
        raise UsageError("")

    masters = read_masters(repo_dir)
    output_by_path_map = render_all(masters, repo_dir)

    write_output(repo_dir, output_by_path_map)

    print(f"{_COMMAND_NAME}: wrote {len(output_by_path_map)} files under {GENERATED_FOLDER}/")


# --------------------------------------------------------------------------------

def main(argument_list: list[str], repo_dir: Path = REPO_DIR) -> int:
    return run_command(_COMMAND_NAME, partial(_generate, argument_list, repo_dir))


# --------------------------------------------------------------------------------
# Main / Entry Point
# --------------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
