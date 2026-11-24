# --------------------------------------------------------------------------------
# practices.check: the drift of generated/ printed, and the exit code
# --------------------------------------------------------------------------------

from pathlib import Path

from practices import check, generate


# --------------------------------------------------------------------------------
# Passing and failing
# --------------------------------------------------------------------------------

def test_check_passes_on_fresh_output(fixture_repo: Path, capsys) -> None:
    generate.main([], fixture_repo)
    capsys.readouterr()

    assert check.main([], fixture_repo) == 0
    assert capsys.readouterr().out == "practices.check: generated/ matches the masters (8 files)\n"


# --------------------------------------------------------------------------------

def test_check_without_generated_names_every_expected_file_as_missing(fixture_repo: Path, capsys) -> None:
    assert check.main([], fixture_repo) == 1

    captured = capsys.readouterr()

    assert captured.out.count("missing file: generated/") == 8
    assert "8 generated files differ from the masters" in captured.err


# --------------------------------------------------------------------------------
# Refusals
# --------------------------------------------------------------------------------

def test_check_with_a_broken_master_prints_the_reader_message(fixture_repo: Path, capsys) -> None:
    (fixture_repo / "rules" / "a.md").write_text("---\npath: x\n---\n\n# A1\n\nText a1.\n")

    assert check.main([], fixture_repo) == 1

    captured = capsys.readouterr()

    assert captured.out == ""
    assert "rules/a.md: unknown frontmatter key 'path'" in captured.err


# --------------------------------------------------------------------------------

def test_check_refuses_an_argument(fixture_repo: Path, capsys) -> None:
    assert check.main(["extra"], fixture_repo) == 2
    assert capsys.readouterr().err == "Usage: practices.check\n"


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
