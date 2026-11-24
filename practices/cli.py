# --------------------------------------------------------------------------------
# What every practices command shares: refusals, usage errors and the exit codes
# --------------------------------------------------------------------------------
# A refusal prints "<command>: <text>" on stderr and exits 1; a usage error
# prints one "Usage:" line on stderr and exits 2. An OS error is a refusal too,
# and Ctrl-C prints "interrupted" and exits 130; neither shows a traceback.
# --------------------------------------------------------------------------------

import sys
from pathlib import Path
from typing import Callable

from practices.errors import PracticesError, UsageError


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

REPO_DIR = Path(__file__).resolve().parent.parent
_USAGE_EXIT_CODE = 2
_REFUSAL_EXIT_CODE = 1
_INTERRUPT_EXIT_CODE = 130


# --------------------------------------------------------------------------------
# Running a command
# --------------------------------------------------------------------------------

def _print_notice(command_name: str, text: str) -> None:
    print(f"{command_name}: {text}", file=sys.stderr)


def run_command(command_name: str, action: Callable[[], None]) -> int:
    try:
        action()
    except UsageError as e:
        suffix = f" {e.args_text}" if e.args_text else ""
        print(f"Usage: {command_name}{suffix}", file=sys.stderr)

        return _USAGE_EXIT_CODE
    except PracticesError as e:
        _print_notice(command_name, str(e))

        return _REFUSAL_EXIT_CODE
    except OSError as e:
        _print_notice(command_name, str(e))

        return _REFUSAL_EXIT_CODE
    except KeyboardInterrupt:
        _print_notice(command_name, "interrupted")

        return _INTERRUPT_EXIT_CODE

    return 0
