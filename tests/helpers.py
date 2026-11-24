# --------------------------------------------------------------------------------
# Helpers shared by several test files
# --------------------------------------------------------------------------------

from pathlib import Path

from practices.generated.generated_file import GeneratedFile
from practices.masters.masters_reader import read_masters
from practices.rendering.renderer import render_all


def render_repo(repo_dir: Path) -> dict[str, GeneratedFile]:
    return render_all(read_masters(repo_dir), repo_dir)


# --------------------------------------------------------------------------------

def write_master(repo_dir: Path, relative_name: str, content: str) -> None:
    master_file = repo_dir / "rules" / relative_name

    master_file.parent.mkdir(parents=True, exist_ok=True)
    master_file.write_text(content, encoding="utf-8")


# --------------------------------------------------------------------------------

def write_skill(repo_dir: Path, folder: str, content: str) -> None:
    skill_file = repo_dir / "skills" / folder / "SKILL.md"

    skill_file.parent.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(content, encoding="utf-8")


# --------------------------------------------------------------------------------

def snapshot_generated(repo_dir: Path) -> dict[str, tuple[bytes, int]]:
    generated_dir = repo_dir / "generated"
    snapshot_by_path_map = {}

    for entry in sorted(generated_dir.rglob("*")):
        if entry.is_file():
            snapshot_by_path_map[entry.relative_to(generated_dir).as_posix()] = (
                entry.read_bytes(),
                entry.stat().st_mode,
            )

    return snapshot_by_path_map
