# --------------------------------------------------------------------------------
# Helpers shared by several test files
# --------------------------------------------------------------------------------

from pathlib import Path

from practices.model import OutputFile
from practices.reader import read_masters
from practices.render import render_all


def render_repo(repo_dir: Path) -> dict[str, OutputFile]:
    return render_all(read_masters(repo_dir), repo_dir)
