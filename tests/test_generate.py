# --------------------------------------------------------------------------------
# practices.generate: the masters written to generated/ for both agents
# --------------------------------------------------------------------------------

from pathlib import Path

from practices import check, generate
from tests.helpers import snapshot_generated


# --------------------------------------------------------------------------------
# Writing the generated files
# --------------------------------------------------------------------------------

def test_generate_writes_both_agents_for_every_master(fixture_repo: Path, capsys) -> None:
    assert generate.main([], fixture_repo) == 0

    assert _generated_path_list(fixture_repo) == [
        "claude/rules/bp-a.md",
        "claude/rules/bp-b.md",
        "claude/skills/bp-a/SKILL.md",
        "claude/skills/bp-a/extra1.txt",
        "cursor/rules/bp-a.mdc",
        "cursor/rules/bp-b.mdc",
        "cursor/skills/bp-a/SKILL.md",
        "cursor/skills/bp-a/extra1.txt",
    ]
    assert capsys.readouterr().out == "practices.generate: wrote 8 files under generated/\n"


# --------------------------------------------------------------------------------

def test_generated_files_carry_the_header_and_each_agent_format(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)
    generated_dir = fixture_repo / "generated"
    header = "<!-- GENERATED from rules/bp-b.md; edit that file and regenerate -->\n"

    assert (generated_dir / "claude/rules/bp-a.md").read_text() == (
        "<!-- GENERATED from rules/bp-a.md; edit that file and regenerate -->\n\n# A1\n\nText a1.\n"
    )
    assert (generated_dir / "claude/rules/bp-b.md").read_text() == (
        '---\npaths:\n  - "**/*.b1"\n  - "**/b2*.txt"\n---\n' + header + "\n# B1\n\nText b1.\n"
    )
    assert (generated_dir / "cursor/rules/bp-a.mdc").read_text() == (
        "---\nalwaysApply: true\n---\n"
        "<!-- GENERATED from rules/bp-a.md; edit that file and regenerate -->\n\n# A1\n\nText a1.\n"
    )
    assert (generated_dir / "cursor/rules/bp-b.mdc").read_text() == (
        "---\nglobs: **/*.b1, **/b2*.txt\nalwaysApply: false\n---\n" + header + "\n# B1\n\nText b1.\n"
    )


# --------------------------------------------------------------------------------
# Removed and broken masters
# --------------------------------------------------------------------------------

def test_a_removed_master_loses_its_output(fixture_repo: Path, capsys) -> None:
    generate.main([], fixture_repo)
    (fixture_repo / "rules" / "bp-b.md").unlink()
    capsys.readouterr()

    assert check.main([], fixture_repo) == 1
    assert "extra file: generated/claude/rules/bp-b.md\n" in capsys.readouterr().out

    assert generate.main([], fixture_repo) == 0
    assert not (fixture_repo / "generated/claude/rules/bp-b.md").exists()
    assert not (fixture_repo / "generated/cursor/rules/bp-b.mdc").exists()
    assert check.main([], fixture_repo) == 0


# --------------------------------------------------------------------------------

def test_a_broken_master_leaves_generated_untouched(fixture_repo: Path, capsys) -> None:
    generate.main([], fixture_repo)
    before_snapshot = snapshot_generated(fixture_repo)
    (fixture_repo / "rules" / "bp-a.md").write_text('---\npath:\n  - "**/*.a1"\n---\n\n# A1\n\nText a1.\n')
    capsys.readouterr()

    assert generate.main([], fixture_repo) == 1
    assert "rules/bp-a.md: unknown frontmatter key 'path'" in capsys.readouterr().err
    assert snapshot_generated(fixture_repo) == before_snapshot


# --------------------------------------------------------------------------------
# Refusals
# --------------------------------------------------------------------------------

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

def _generated_path_list(repo_dir: Path) -> list[str]:
    generated_dir = repo_dir / "generated"
    path_list = []

    for entry in sorted(generated_dir.rglob("*")):
        if entry.is_file():
            path_list.append(entry.relative_to(generated_dir).as_posix())

    return path_list
