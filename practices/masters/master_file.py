# --------------------------------------------------------------------------------
# The master file: the plain-file and name checks every master reader shares
# --------------------------------------------------------------------------------

from pathlib import Path

from practices.error.practices_error import PracticesError


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

_NAME_PREFIX = "bp-"


# --------------------------------------------------------------------------------
# Reading a master file
# --------------------------------------------------------------------------------

def refuse_link(entry: Path, master_path: str) -> None:
    if entry.is_symlink():
        raise PracticesError(f"{master_path}: is a link; a master is a plain file")


# --------------------------------------------------------------------------------

def read_text(master_file: Path, master_path: str) -> str:
    try:
        return master_file.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as e:
        raise PracticesError(f"{master_path}: is not UTF-8 text") from e
    except OSError as e:
        raise PracticesError(f"{master_path}: cannot read the file") from e


# --------------------------------------------------------------------------------
# Checking a master name
# --------------------------------------------------------------------------------
# An experimental practice is named bp-exp-<name>, so it passes the same check.
# --------------------------------------------------------------------------------

def check_name_prefix(name: str, master_path: str) -> None:
    if not name.startswith(_NAME_PREFIX):
        raise PracticesError(
            f"{master_path}: the name must start with {_NAME_PREFIX} (bp-exp- for an experimental practice)"
        )
