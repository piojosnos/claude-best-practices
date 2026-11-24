# --------------------------------------------------------------------------------
# The drift finder: changed, missing and extra files under generated/
# --------------------------------------------------------------------------------

from pathlib import Path

import pytest

from practices import generate
from practices.error.practices_error import PracticesError
from practices.generated.drift_finder import find_drift


# --------------------------------------------------------------------------------
# Changed files
# --------------------------------------------------------------------------------

def test_drift_names_a_hand_edited_file(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)

    with (fixture_repo / "generated/cursor/rules/b.mdc").open("a") as edited:
        edited.write("hand edit\n")

    drift_list = find_drift(fixture_repo)

    assert len(drift_list) == 1
    assert drift_list[0].startswith("changed file: generated/cursor/rules/b.mdc\n")
    assert "+hand edit" in drift_list[0].split("\n")


# --------------------------------------------------------------------------------

def test_drift_names_a_changed_executable_bit(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)

    (fixture_repo / "generated/claude/rules/a.md").chmod(0o755)

    assert "changed mode: generated/claude/rules/a.md" in find_drift(fixture_repo)


# --------------------------------------------------------------------------------

def test_drift_names_a_changed_binary_file_without_a_diff(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)

    (fixture_repo / "generated/claude/skills/a/extra1.txt").write_bytes(b"\xff\xfe")

    assert find_drift(fixture_repo) == ["changed file: generated/claude/skills/a/extra1.txt"]


# --------------------------------------------------------------------------------
# Missing and extra files
# --------------------------------------------------------------------------------

def test_drift_names_a_deleted_output_and_a_stale_extra_file(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)

    (fixture_repo / "generated/cursor/skills/a/SKILL.md").unlink()
    (fixture_repo / "generated/claude/rules/z9.md").write_text("stale z9\n")

    drift_list = find_drift(fixture_repo)

    assert "missing file: generated/cursor/skills/a/SKILL.md" in drift_list
    assert "extra file: generated/claude/rules/z9.md" in drift_list
    assert len(drift_list) == 2


# --------------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------------

def test_drift_refuses_a_link_under_generated(fixture_repo: Path) -> None:
    generate.main([], fixture_repo)

    (fixture_repo / "generated/claude/rules/l1.md").symlink_to(fixture_repo / "generated/claude/rules/a.md")

    with pytest.raises(PracticesError) as raised:
        find_drift(fixture_repo)

    assert "generated/claude/rules/l1.md is a link" in str(raised.value)
