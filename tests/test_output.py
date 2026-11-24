# --------------------------------------------------------------------------------
# The output tree: layout, stable order, idempotent runs and the safe rewrite
# --------------------------------------------------------------------------------

from pathlib import Path

import pytest

from practices import check, generate
from practices.model import OutputFile
from practices.output import write_output
from tests.helpers import render_repo


# --------------------------------------------------------------------------------
# Layout and order
# --------------------------------------------------------------------------------

def test_layout_mirrors_each_agent_config_folder(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)

    assert list(_snapshot(fixture_repo)) == [
        "claude/rules/a.md",
        "claude/rules/b.md",
        "claude/skills/a/SKILL.md",
        "claude/skills/a/extra1.txt",
        "cursor/rules/a.mdc",
        "cursor/rules/b.mdc",
        "cursor/skills/a/SKILL.md",
        "cursor/skills/a/extra1.txt",
    ]


def test_output_keys_are_sorted_whatever_the_creation_order(fixture_repo: Path) -> None:
    _write_rule(fixture_repo, "z1.md")
    _write_rule(fixture_repo, "c1.md")

    output_path_list = list(render_repo(fixture_repo))

    assert output_path_list == sorted(output_path_list)
    assert "claude/rules/c1.md" in output_path_list


def test_two_generate_runs_are_idempotent(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)
    first_snapshot = _snapshot(fixture_repo)

    generate.main([], fixture_repo)

    assert _snapshot(fixture_repo) == first_snapshot


# --------------------------------------------------------------------------------
# Removed and broken masters
# --------------------------------------------------------------------------------

def test_a_removed_master_loses_its_output(fixture_repo: Path, capsys) -> None:
    generate.main([], fixture_repo)
    (fixture_repo / "rules" / "b.md").unlink()
    capsys.readouterr()

    assert check.main([], fixture_repo) == 1
    assert "extra file: generated/claude/rules/b.md\n" in capsys.readouterr().out

    assert generate.main([], fixture_repo) == 0
    assert not (fixture_repo / "generated/claude/rules/b.md").exists()
    assert not (fixture_repo / "generated/cursor/rules/b.mdc").exists()
    assert check.main([], fixture_repo) == 0


def test_a_broken_master_leaves_generated_untouched(fixture_repo: Path, capsys) -> None:
    generate.main([], fixture_repo)
    before_snapshot = _snapshot(fixture_repo)
    (fixture_repo / "rules" / "a.md").write_text('---\npath:\n  - "**/*.a1"\n---\n\n# A1\n\nText a1.\n')
    capsys.readouterr()

    assert generate.main([], fixture_repo) == 1
    assert "rules/a.md: unknown frontmatter key 'path'" in capsys.readouterr().err
    assert _snapshot(fixture_repo) == before_snapshot


def test_a_write_that_fails_midway_leaves_generated_and_the_repo_as_they_were(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)
    before_snapshot = _snapshot(fixture_repo)
    before_name_list = _name_list(fixture_repo)
    clashing_output_map = {
        "a1.txt": OutputFile(b"a1\n", False),
        "b1": OutputFile(b"b1\n", False),
        "b1/c1.txt": OutputFile(b"c1\n", False),
    }

    with pytest.raises(OSError):
        write_output(fixture_repo, clashing_output_map)

    assert _snapshot(fixture_repo) == before_snapshot
    assert _name_list(fixture_repo) == before_name_list


def test_generate_refuses_a_generated_link(fixture_repo: Path, tmp_path: Path, capsys) -> None:
    elsewhere_dir = tmp_path / "elsewhere1"
    elsewhere_dir.mkdir()
    (elsewhere_dir / "canary1.txt").write_text("canary c1\n")
    (fixture_repo / "generated").symlink_to(elsewhere_dir)

    assert generate.main([], fixture_repo) == 1
    assert "generated is a link" in capsys.readouterr().err
    assert (elsewhere_dir / "canary1.txt").read_text() == "canary c1\n"


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _snapshot(repo_dir: Path) -> dict[str, tuple[bytes, int]]:
    generated_dir = repo_dir / "generated"
    snapshot_by_path_map = {}

    for entry in sorted(generated_dir.rglob("*")):
        if entry.is_file():
            snapshot_by_path_map[entry.relative_to(generated_dir).as_posix()] = (
                entry.read_bytes(),
                entry.stat().st_mode,
            )

    return snapshot_by_path_map


def _write_rule(repo_dir: Path, file_name: str) -> None:
    (repo_dir / "rules" / file_name).write_text("# R1\n\nText r1.\n")


def _name_list(folder: Path) -> list[str]:
    name_list = []

    for entry in folder.iterdir():
        name_list.append(entry.name)

    return sorted(name_list)
