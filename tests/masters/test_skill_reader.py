# --------------------------------------------------------------------------------
# The skill reader: typed skills, extra files and the strict skill dialect
# --------------------------------------------------------------------------------
# Real skill folders written under tmp_path; a broken master must stop the run with
# a message that starts with the master's path.
# --------------------------------------------------------------------------------

from pathlib import Path

import pytest

from practices.error.practices_error import PracticesError
from practices.masters.masters_model import ExtraFile, Skill
from practices.masters.skill_reader import read_skill_list
from tests.helpers import write_skill


SKILL_NAME_RULE_TEXT = (
    "the name '{name}' breaks the skill name rule: lowercase letters and digits "
    "in words joined by single hyphens, at most 64 characters"
)
DESCRIPTION_RULE_TEXT = "description must be text of 1 to 1024 characters"
LONG_DESCRIPTION_TEXT = "d" * 1025

BROKEN_SKILL_MASTER_LIST = [
    ("bp-x1", None, "skills/bp-x1: has no SKILL.md"),
    (
        "bp-x1",
        "---\nname: bp-x1\ndescription: d1\nlicense: l1\n---\n\n# X1\n\nText x1.\n",
        "skills/bp-x1/SKILL.md: unknown frontmatter key 'license'; "
        "a skill allows only: description, disable-model-invocation, name",
    ),
    (
        "bp-x1",
        "---\ndescription: d1\n---\n\n# X1\n\nText x1.\n",
        "skills/bp-x1/SKILL.md: name must equal the folder name 'bp-x1'",
    ),
    (
        "bp-x1",
        "---\nname: bp-y1\ndescription: d1\n---\n\n# X1\n\nText x1.\n",
        "skills/bp-x1/SKILL.md: name must equal the folder name 'bp-x1'",
    ),
    (
        "bp-X1",
        "---\nname: bp-X1\ndescription: d1\n---\n\n# X1\n\nText x1.\n",
        "skills/bp-X1/SKILL.md: " + SKILL_NAME_RULE_TEXT.format(name="bp-X1"),
    ),
    (
        "bp-x--1",
        "---\nname: bp-x--1\ndescription: d1\n---\n\n# X1\n\nText x1.\n",
        "skills/bp-x--1/SKILL.md: " + SKILL_NAME_RULE_TEXT.format(name="bp-x--1"),
    ),
    (
        "bp-x1",
        "---\nname: bp-x1\n---\n\n# X1\n\nText x1.\n",
        "skills/bp-x1/SKILL.md: " + DESCRIPTION_RULE_TEXT,
    ),
    (
        "bp-x1",
        '---\nname: bp-x1\ndescription: ""\n---\n\n# X1\n\nText x1.\n',
        "skills/bp-x1/SKILL.md: " + DESCRIPTION_RULE_TEXT,
    ),
    (
        "bp-x1",
        "---\nname: bp-x1\ndescription: 5\n---\n\n# X1\n\nText x1.\n",
        "skills/bp-x1/SKILL.md: " + DESCRIPTION_RULE_TEXT,
    ),
    (
        "bp-x1",
        f"---\nname: bp-x1\ndescription: {LONG_DESCRIPTION_TEXT}\n---\n\n# X1\n\nText x1.\n",
        "skills/bp-x1/SKILL.md: " + DESCRIPTION_RULE_TEXT,
    ),
    (
        "bp-x1",
        "---\nname: bp-x1\ndescription: d1\n---\n",
        "skills/bp-x1/SKILL.md: the master has no text",
    ),
    (
        "bp-x1",
        "---\nname: bp-x1\ndescription: d1\ndisable-model-invocation: maybe\n---\n\n# X1\n\nText x1.\n",
        "skills/bp-x1/SKILL.md: disable-model-invocation must be true or false",
    ),
    (
        "bp-x1",
        "---\nname: bp-x1\ndescription: d1\ndisable-model-invocation: 1\n---\n\n# X1\n\nText x1.\n",
        "skills/bp-x1/SKILL.md: disable-model-invocation must be true or false",
    ),
    (
        "x1",
        "---\nname: x1\ndescription: d1\n---\n\n# X1\n\nText x1.\n",
        "skills/x1/SKILL.md: the name must start with bp- (bp-exp- for an experimental practice)",
    ),
]


# --------------------------------------------------------------------------------
# The typed model and the walk
# --------------------------------------------------------------------------------

def test_reader_returns_a_typed_skill_of_the_fixture_master(fixture_repo: Path) -> None:
    assert read_skill_list(fixture_repo) == [
        Skill(
            "bp-a",
            "skills/bp-a/SKILL.md",
            'Skill a1 does "a1" work. Use when a1.',
            "# A1 workflow\n\nStep a1.",
            [ExtraFile("extra1.txt", b"extra a1\n", False)],
        )
    ]


# --------------------------------------------------------------------------------

@pytest.mark.parametrize("text, expected", [("true", True), ("false", False)])
def test_reader_reads_the_disable_model_invocation_flag_of_a_skill(
    fixture_repo: Path, text: str, expected: bool
) -> None:
    write_skill(
        fixture_repo,
        "bp-x1",
        f"---\nname: bp-x1\ndescription: d1\ndisable-model-invocation: {text}\n---\n\n# X1\n\nText x1.\n",
    )

    skill_by_name_map = {skill.name: skill for skill in read_skill_list(fixture_repo)}

    assert skill_by_name_map["bp-x1"].disable_model_invocation is expected
    assert skill_by_name_map["bp-a"].disable_model_invocation is None


# --------------------------------------------------------------------------------

def test_a_skill_extra_file_in_a_subfolder_keeps_its_relative_path_and_exec_bit(fixture_repo: Path) -> None:
    tool_file = fixture_repo / "skills" / "bp-a" / "scripts1" / "tool1"

    tool_file.parent.mkdir()
    tool_file.write_bytes(b"#!/bin/sh\n")
    tool_file.chmod(0o755)

    assert read_skill_list(fixture_repo)[0].extra_file_list == [
        ExtraFile("extra1.txt", b"extra a1\n", False),
        ExtraFile("scripts1/tool1", b"#!/bin/sh\n", True),
    ]


# --------------------------------------------------------------------------------

def test_skills_come_back_sorted_by_name(fixture_repo: Path) -> None:
    write_skill(fixture_repo, "bp-z1", "---\nname: bp-z1\ndescription: d1\n---\n\n# Z1\n\nText z1.\n")
    write_skill(fixture_repo, "bp-c1", "---\nname: bp-c1\ndescription: d1\n---\n\n# C1\n\nText c1.\n")

    skill_name_list = []

    for skill in read_skill_list(fixture_repo):
        skill_name_list.append(skill.name)

    assert skill_name_list == ["bp-a", "bp-c1", "bp-z1"]


# --------------------------------------------------------------------------------

def test_an_experimental_skill_passes_the_name_prefix_check(fixture_repo: Path) -> None:
    write_skill(fixture_repo, "bp-exp-x1", "---\nname: bp-exp-x1\ndescription: d1\n---\n\n# X1\n\nText x1.\n")

    skill_name_list = []

    for skill in read_skill_list(fixture_repo):
        skill_name_list.append(skill.name)

    assert skill_name_list == ["bp-a", "bp-exp-x1"]


# --------------------------------------------------------------------------------

def test_hidden_entries_in_skills_are_skipped(fixture_repo: Path) -> None:
    (fixture_repo / "skills" / "bp-a" / ".DS_Store").write_bytes(b"junk")
    (fixture_repo / "skills" / ".cache1").mkdir()
    (fixture_repo / "skills" / ".cache1" / "SKILL.md").write_text("not a skill", encoding="utf-8")

    skill_list = read_skill_list(fixture_repo)

    assert len(skill_list) == 1
    assert skill_list[0].extra_file_list == [ExtraFile("extra1.txt", b"extra a1\n", False)]


# --------------------------------------------------------------------------------
# Rejections
# --------------------------------------------------------------------------------

@pytest.mark.parametrize("folder, content, message", BROKEN_SKILL_MASTER_LIST)
def test_reader_rejects_a_broken_skill_master(
    fixture_repo: Path, folder: str, content: str | None, message: str
) -> None:
    if content is None:
        (fixture_repo / "skills" / folder).mkdir()
    else:
        write_skill(fixture_repo, folder, content)

    with pytest.raises(PracticesError) as raised:
        read_skill_list(fixture_repo)

    assert str(raised.value) == message


# --------------------------------------------------------------------------------

def test_reader_rejects_a_file_directly_in_skills(fixture_repo: Path) -> None:
    (fixture_repo / "skills" / "notes1.txt").write_text("Text n1.\n", encoding="utf-8")

    with pytest.raises(PracticesError) as raised:
        read_skill_list(fixture_repo)

    assert str(raised.value) == "skills/notes1.txt: skills/ holds only skill folders"


# --------------------------------------------------------------------------------

def test_reader_rejects_a_link_in_a_skill(fixture_repo: Path, tmp_path: Path) -> None:
    outside_file = tmp_path / "outside1.txt"
    outside_file.write_text("outside o1\n", encoding="utf-8")
    (fixture_repo / "skills" / "bp-a" / "link1").symlink_to(outside_file)

    with pytest.raises(PracticesError) as raised:
        read_skill_list(fixture_repo)

    assert str(raised.value) == "skills/bp-a/link1: is a link; a master is a plain file"
