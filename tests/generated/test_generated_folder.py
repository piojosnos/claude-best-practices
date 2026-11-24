# --------------------------------------------------------------------------------
# The generated folder: layout, stable order, idempotent runs and the safe rewrite
# --------------------------------------------------------------------------------

from pathlib import Path

import pytest

from practices import generate
from practices.error.practices_error import PracticesError
from practices.generated.generated_file import GeneratedFile
from practices.generated.generated_folder import read_generated_folder, write_generated_folder
from tests.helpers import snapshot_generated


# --------------------------------------------------------------------------------
# Layout and order
# --------------------------------------------------------------------------------

def test_layout_mirrors_each_agent_config_folder(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)

    assert list(snapshot_generated(fixture_repo)) == [
        "claude/rules/a.md",
        "claude/rules/b.md",
        "claude/skills/a/SKILL.md",
        "claude/skills/a/extra1.txt",
        "cursor/rules/a.mdc",
        "cursor/rules/b.mdc",
        "cursor/skills/a/SKILL.md",
        "cursor/skills/a/extra1.txt",
    ]


# --------------------------------------------------------------------------------

def test_two_generate_runs_are_idempotent(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)
    first_snapshot = snapshot_generated(fixture_repo)

    generate.main([], fixture_repo)

    assert snapshot_generated(fixture_repo) == first_snapshot


# --------------------------------------------------------------------------------
# The safe rewrite
# --------------------------------------------------------------------------------

def test_a_write_that_fails_midway_leaves_generated_and_the_repo_as_they_were(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)
    before_snapshot = snapshot_generated(fixture_repo)
    before_name_list = _name_list(fixture_repo)
    clashing_generated_file_by_path_map = {
        "a1.txt": GeneratedFile(b"a1\n", False),
        "b1": GeneratedFile(b"b1\n", False),
        "b1/c1.txt": GeneratedFile(b"c1\n", False),
    }

    with pytest.raises(OSError):
        write_generated_folder(fixture_repo, clashing_generated_file_by_path_map)

    assert snapshot_generated(fixture_repo) == before_snapshot
    assert _name_list(fixture_repo) == before_name_list


# --------------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------------

def test_reading_refuses_a_link_under_generated(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)

    (fixture_repo / "generated/claude/rules/l1.md").symlink_to(fixture_repo / "generated/claude/rules/a.md")

    with pytest.raises(PracticesError) as raised:
        read_generated_folder(fixture_repo)

    assert "generated/claude/rules/l1.md is a link" in str(raised.value)


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _name_list(folder: Path) -> list[str]:
    name_list = []

    for entry in folder.iterdir():
        name_list.append(entry.name)

    return sorted(name_list)
