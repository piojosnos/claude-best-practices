# --------------------------------------------------------------------------------
# The skill output: exact bytes per agent, extra files and the real skill masters
# --------------------------------------------------------------------------------
# The expected text is written from the format, never copied from a generator run.
# --------------------------------------------------------------------------------

from pathlib import Path

import pytest
import yaml

from practices import generate
from practices.cli import REPO_DIR
from practices.render import render_all

AGENT_NAME_LIST = ["claude", "cursor"]
EXPECTED_SKILL_A = (
    "---\n"
    "name: a\n"
    'description: "Skill a1 does \\"a1\\" work. Use when a1."\n'
    "---\n"
    "<!-- GENERATED from skills/a/SKILL.md; edit that file and regenerate -->\n"
    "\n"
    "# A1 workflow\n"
    "\n"
    "Step a1.\n"
)


# --------------------------------------------------------------------------------
# Fixture skill
# --------------------------------------------------------------------------------

@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_the_skill_file_is_the_frontmatter_the_header_and_the_body(fixture_repo: Path, agent_name: str) -> None:
    assert _output_text(fixture_repo, f"{agent_name}/skills/a/SKILL.md") == EXPECTED_SKILL_A


@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_the_skill_frontmatter_round_trips_through_yaml(fixture_repo: Path, agent_name: str) -> None:
    frontmatter = _frontmatter(_output_text(fixture_repo, f"{agent_name}/skills/a/SKILL.md"))

    assert frontmatter == {"name": "a", "description": 'Skill a1 does "a1" work. Use when a1.'}


@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_an_extra_file_is_copied_byte_for_byte_without_a_header(fixture_repo: Path, agent_name: str) -> None:
    output_file = render_all(fixture_repo)[f"{agent_name}/skills/a/extra1.txt"]

    assert output_file.content == b"extra a1\n"
    assert output_file.executable is False


def test_an_executable_extra_file_keeps_its_exec_bit_on_disk(fixture_repo: Path) -> None:
    tool_file = fixture_repo / "skills" / "a" / "tool1"

    tool_file.write_bytes(b"#!/bin/sh\n")
    tool_file.chmod(0o755)

    assert generate.main([], fixture_repo) == 0

    for agent_name in AGENT_NAME_LIST:
        output_file = render_all(fixture_repo)[f"{agent_name}/skills/a/tool1"]

        assert output_file.content == b"#!/bin/sh\n"
        assert output_file.executable is True
        assert (fixture_repo / "generated" / agent_name / "skills" / "a" / "tool1").stat().st_mode & 0o100


# --------------------------------------------------------------------------------
# Real skill masters
# --------------------------------------------------------------------------------

@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_every_real_skill_keeps_its_name_and_description_for_each_agent(agent_name: str) -> None:
    output_by_path_map = render_all(REPO_DIR)
    skill_dir_list = _real_skill_dir_list()

    assert skill_dir_list

    for skill_dir in skill_dir_list:
        master_frontmatter = _frontmatter((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
        output_text = output_by_path_map[f"{agent_name}/skills/{skill_dir.name}/SKILL.md"].content.decode("utf-8")

        assert _frontmatter(output_text) == {
            "name": master_frontmatter["name"],
            "description": master_frontmatter["description"],
        }


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _output_text(repo_dir: Path, output_path: str) -> str:
    return render_all(repo_dir)[output_path].content.decode("utf-8")


def _frontmatter(text: str) -> dict:
    block = text.split("\n---\n")[0].removeprefix("---\n")

    return yaml.safe_load(block)


def _real_skill_dir_list() -> list[Path]:
    skill_dir_list = []

    for entry in sorted((REPO_DIR / "skills").iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            skill_dir_list.append(entry)

    return skill_dir_list
