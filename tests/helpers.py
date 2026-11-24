# --------------------------------------------------------------------------------
# Helpers shared by several test files
# --------------------------------------------------------------------------------

from pathlib import Path

from practices.model import OutputFile
from practices.reader import read_masters
from practices.render import render_all


def render_repo(repo_dir: Path) -> dict[str, OutputFile]:
    return render_all(read_masters(repo_dir), repo_dir)


def write_skill(repo_dir: Path, folder: str, content: str) -> None:
    skill_file = repo_dir / "skills" / folder / "SKILL.md"

    skill_file.parent.mkdir(parents=True, exist_ok=True)
    skill_file.write_text(content, encoding="utf-8")
