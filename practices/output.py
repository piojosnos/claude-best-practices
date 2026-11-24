# --------------------------------------------------------------------------------
# The output tree: write generated/ from the rendered map and read it back
# --------------------------------------------------------------------------------
# generated/ is owned by the generator: a write removes it whole, so a removed
# master loses its output. Nothing outside it is ever touched.
# --------------------------------------------------------------------------------

import shutil
from pathlib import Path

from practices.cli import PracticesError
from practices.model import OutputFile


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

GENERATED_FOLDER = "generated"
_EXECUTABLE_MODE = 0o755
_PLAIN_MODE = 0o644
_OWNER_EXEC_BIT = 0o100


# --------------------------------------------------------------------------------
# Writing
# --------------------------------------------------------------------------------

def write_output(repo_dir: Path, output_by_path_map: dict[str, OutputFile]) -> None:
    generated_dir = repo_dir / GENERATED_FOLDER

    _check_generated_dir(repo_dir, generated_dir)

    if generated_dir.exists():
        shutil.rmtree(generated_dir)

    for output_path in sorted(output_by_path_map):
        _write_file(generated_dir / output_path, output_by_path_map[output_path])


def _check_generated_dir(repo_dir: Path, generated_dir: Path) -> None:
    if generated_dir.is_symlink() or generated_dir.resolve() != repo_dir.resolve() / GENERATED_FOLDER:
        raise PracticesError(f"{GENERATED_FOLDER}: must be a real folder inside {repo_dir}")


def _write_file(target: Path, output_file: OutputFile) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(output_file.content)
    target.chmod(_EXECUTABLE_MODE if output_file.executable else _PLAIN_MODE)


# --------------------------------------------------------------------------------
# Reading back
# --------------------------------------------------------------------------------

def read_output_tree(repo_dir: Path) -> dict[str, OutputFile]:
    generated_dir = repo_dir / GENERATED_FOLDER
    output_by_path_map = {}

    if not generated_dir.is_dir():
        return output_by_path_map

    for entry in sorted(generated_dir.rglob("*"), key=Path.as_posix):
        if entry.is_file() and not entry.is_symlink():
            executable = bool(entry.stat().st_mode & _OWNER_EXEC_BIT)
            output_by_path_map[entry.relative_to(generated_dir).as_posix()] = OutputFile(
                entry.read_bytes(), executable
            )

    return output_by_path_map
