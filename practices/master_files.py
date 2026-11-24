# --------------------------------------------------------------------------------
# Master files: the plain-file checks every master reader shares
# --------------------------------------------------------------------------------

from pathlib import Path

from practices.errors import PracticesError


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
