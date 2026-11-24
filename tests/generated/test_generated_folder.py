# --------------------------------------------------------------------------------
# The generated folder: layout, stable order, idempotent runs and the safe rewrite
# --------------------------------------------------------------------------------

from pathlib import Path

import pytest

from practices import check, generate
from practices.generated.generated_file import GeneratedFile
from practices.generated.generated_folder import write_generated_folder
from tests.helpers import render_repo, snapshot_generated, write_master


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

def test_output_keys_are_sorted_whatever_the_creation_order(fixture_repo: Path) -> None:
    write_master(fixture_repo, "z1.md", "# R1\n\nText r1.\n")
    write_master(fixture_repo, "c1.md", "# R1\n\nText r1.\n")

    output_path_list = list(render_repo(fixture_repo))

    assert output_path_list == sorted(output_path_list)
    assert "claude/rules/c1.md" in output_path_list


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

def test_check_refuses_generated_when_it_is_a_link(fixture_repo: Path, capsys) -> None:
    generate.main([], fixture_repo)
    capsys.readouterr()

    (fixture_repo / "generated").rename(fixture_repo / "real_gen1")
    (fixture_repo / "generated").symlink_to(fixture_repo / "real_gen1")

    assert check.main([], fixture_repo) == 1

    captured = capsys.readouterr()

    assert captured.out == ""
    assert "generated is a link" in captured.err


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _name_list(folder: Path) -> list[str]:
    name_list = []

    for entry in folder.iterdir():
        name_list.append(entry.name)

    return sorted(name_list)
