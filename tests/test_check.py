# --------------------------------------------------------------------------------
# The tracer: masters to generated files, and the drift check over them
# --------------------------------------------------------------------------------

from pathlib import Path

from practices import check, generate


def test_generate_writes_both_agents_for_every_master(fixture_repo: Path, capsys) -> None:
    assert generate.main([], fixture_repo) == 0

    assert _generated_path_list(fixture_repo) == [
        "claude/rules/a.md",
        "claude/rules/b.md",
        "claude/skills/a/SKILL.md",
        "claude/skills/a/extra1.txt",
        "cursor/rules/a.mdc",
        "cursor/rules/b.mdc",
        "cursor/skills/a/SKILL.md",
        "cursor/skills/a/extra1.txt",
    ]
    assert capsys.readouterr().out == "practices.generate: wrote 8 files under generated/\n"


def test_generated_files_carry_the_header_and_each_agent_format(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)
    generated_dir = fixture_repo / "generated"
    header = "<!-- GENERATED from rules/b.md; edit that file and regenerate -->\n"

    assert (generated_dir / "claude/rules/a.md").read_text() == (
        "<!-- GENERATED from rules/a.md; edit that file and regenerate -->\n\n# A1\n\nText a1.\n"
    )
    assert (generated_dir / "claude/rules/b.md").read_text() == (
        '---\npaths:\n  - "**/*.b1"\n  - "**/b2*.txt"\n---\n' + header + "\n# B1\n\nText b1.\n"
    )
    assert (generated_dir / "cursor/rules/a.mdc").read_text() == (
        "---\nalwaysApply: true\n---\n"
        "<!-- GENERATED from rules/a.md; edit that file and regenerate -->\n\n# A1\n\nText a1.\n"
    )
    assert (generated_dir / "cursor/rules/b.mdc").read_text() == (
        "---\nglobs: **/*.b1, **/b2*.txt\nalwaysApply: false\n---\n" + header + "\n# B1\n\nText b1.\n"
    )


def test_check_passes_on_fresh_output(fixture_repo: Path, capsys) -> None:
    generate.main([], fixture_repo)
    capsys.readouterr()

    assert check.main([], fixture_repo) == 0
    assert capsys.readouterr().out == "practices.check: generated/ matches the masters (8 files)\n"


def test_check_names_a_hand_edited_file(fixture_repo: Path, capsys) -> None:
    generate.main([], fixture_repo)
    capsys.readouterr()

    with (fixture_repo / "generated/cursor/rules/b.mdc").open("a") as edited:
        edited.write("hand edit\n")

    assert check.main([], fixture_repo) == 1

    captured = capsys.readouterr()

    assert "changed file: generated/cursor/rules/b.mdc\n" in captured.out
    assert "+hand edit\n" in captured.out
    assert "1 generated files differ from the masters" in captured.err


def test_check_names_a_deleted_output_and_a_stale_extra_file(fixture_repo: Path, capsys) -> None:
    generate.main([], fixture_repo)
    capsys.readouterr()

    (fixture_repo / "generated/cursor/skills/a/SKILL.md").unlink()
    (fixture_repo / "generated/claude/rules/z9.md").write_text("stale z9\n")

    assert check.main([], fixture_repo) == 1

    captured = capsys.readouterr()

    assert "missing file: generated/cursor/skills/a/SKILL.md\n" in captured.out
    assert "extra file: generated/claude/rules/z9.md\n" in captured.out
    assert "2 generated files differ from the masters" in captured.err


def test_check_names_a_changed_executable_bit(fixture_repo: Path, capsys) -> None:
    generate.main([], fixture_repo)
    capsys.readouterr()

    (fixture_repo / "generated/claude/rules/a.md").chmod(0o755)

    assert check.main([], fixture_repo) == 1
    assert "changed mode: generated/claude/rules/a.md\n" in capsys.readouterr().out


def test_check_names_a_changed_binary_file_without_a_diff(fixture_repo: Path, capsys) -> None:
    generate.main([], fixture_repo)
    capsys.readouterr()

    (fixture_repo / "generated/claude/skills/a/extra1.txt").write_bytes(b"\xff\xfe")

    assert check.main([], fixture_repo) == 1
    assert capsys.readouterr().out == "changed file: generated/claude/skills/a/extra1.txt\n"


def test_check_refuses_a_link_under_generated(fixture_repo: Path, capsys) -> None:
    generate.main([], fixture_repo)
    capsys.readouterr()

    (fixture_repo / "generated/claude/rules/l1.md").symlink_to(fixture_repo / "generated/claude/rules/a.md")

    assert check.main([], fixture_repo) == 1
    assert "generated/claude/rules/l1.md is a link" in capsys.readouterr().err


def test_check_without_generated_names_every_expected_file_as_missing(fixture_repo: Path, capsys) -> None:
    assert check.main([], fixture_repo) == 1

    captured = capsys.readouterr()

    assert captured.out.count("missing file: generated/") == 8
    assert "8 generated files differ from the masters" in captured.err


def test_check_with_a_broken_master_prints_the_reader_message(fixture_repo: Path, capsys) -> None:
    (fixture_repo / "rules" / "a.md").write_text("---\npath: x\n---\n\n# A1\n\nText a1.\n")

    assert check.main([], fixture_repo) == 1

    captured = capsys.readouterr()

    assert captured.out == ""
    assert "rules/a.md: unknown frontmatter key 'path'" in captured.err


def test_check_refuses_an_argument(fixture_repo: Path, capsys) -> None:
    assert check.main(["extra"], fixture_repo) == 2
    assert capsys.readouterr().err == "Usage: practices.check\n"


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
