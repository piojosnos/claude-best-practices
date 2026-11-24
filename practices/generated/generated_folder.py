# --------------------------------------------------------------------------------
# The generated folder: write generated/ from the rendered map and read it back
# --------------------------------------------------------------------------------
# generated/ is replaced whole, so a removed master loses its files; the new tree
# is built beside it and swapped in, so a failed write keeps the old one.
# --------------------------------------------------------------------------------

import shutil
import tempfile
from pathlib import Path

from practices.error.practices_error import PracticesError
from practices.filesystem.file_mode import is_executable
from practices.generated.generated_file import GeneratedFile


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

GENERATED_FOLDER = "generated"
_EXECUTABLE_MODE = 0o755
_PLAIN_MODE = 0o644


# --------------------------------------------------------------------------------
# Writing
# --------------------------------------------------------------------------------

def write_generated_folder(repo_dir: Path, generated_file_by_path_map: dict[str, GeneratedFile]) -> None:
    generated_dir = repo_dir / GENERATED_FOLDER

    _check_generated_dir(repo_dir, generated_dir)

    work_dir = Path(tempfile.mkdtemp(prefix=f".{GENERATED_FOLDER}-", dir=repo_dir))

    try:
        new_dir = work_dir / "new"

        new_dir.mkdir()

        for generated_path in sorted(generated_file_by_path_map):
            _write_file(new_dir / generated_path, generated_file_by_path_map[generated_path])

        _swap_in(generated_dir, new_dir, work_dir / "old")
    finally:
        shutil.rmtree(work_dir)


# --------------------------------------------------------------------------------

def _check_generated_dir(repo_dir: Path, generated_dir: Path) -> None:
    _refuse_generated_link(generated_dir)

    if generated_dir.resolve() != repo_dir.resolve() / GENERATED_FOLDER:
        raise PracticesError(
            f"{GENERATED_FOLDER} does not resolve to {repo_dir / GENERATED_FOLDER}; refusing to delete it"
        )


# --------------------------------------------------------------------------------

def _refuse_generated_link(generated_dir: Path) -> None:
    if generated_dir.is_symlink():
        raise PracticesError(f"{GENERATED_FOLDER} is a link; {GENERATED_FOLDER}/ must be a plain folder")


# --------------------------------------------------------------------------------

def _swap_in(generated_dir: Path, new_dir: Path, old_dir: Path) -> None:
    if generated_dir.exists():
        generated_dir.replace(old_dir)

    try:
        new_dir.replace(generated_dir)
    except OSError:
        if old_dir.exists():
            old_dir.replace(generated_dir)

        raise


# --------------------------------------------------------------------------------

def _write_file(target: Path, generated_file: GeneratedFile) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(generated_file.content)
    target.chmod(_EXECUTABLE_MODE if generated_file.executable else _PLAIN_MODE)


# --------------------------------------------------------------------------------
# Reading back
# --------------------------------------------------------------------------------

def read_generated_folder(repo_dir: Path) -> dict[str, GeneratedFile]:
    generated_dir = repo_dir / GENERATED_FOLDER
    generated_file_by_path_map = {}

    _refuse_generated_link(generated_dir)

    if not generated_dir.is_dir():
        return generated_file_by_path_map

    for entry in sorted(generated_dir.rglob("*"), key=Path.as_posix):
        generated_path = entry.relative_to(generated_dir).as_posix()

        if entry.is_symlink():
            raise PracticesError(
                f"{GENERATED_FOLDER}/{generated_path} is a link; "
                f"{GENERATED_FOLDER}/ holds only files the generator writes"
            )

        if entry.is_file():
            executable = is_executable(entry)
            generated_file_by_path_map[generated_path] = GeneratedFile(entry.read_bytes(), executable)

    return generated_file_by_path_map
