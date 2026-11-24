# --------------------------------------------------------------------------------
# Shared fixtures of the generator tests
# --------------------------------------------------------------------------------

import shutil
from pathlib import Path

import pytest

from practices.cli import REPO_DIR


# --------------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------------

@pytest.fixture
def fixture_repo(tmp_path: Path) -> Path:
    repo_dir = tmp_path / "repo1"

    shutil.copytree(Path(__file__).parent / "fixtures" / "repo", repo_dir)
    shutil.copytree(REPO_DIR / "templates", repo_dir / "templates")

    return repo_dir
