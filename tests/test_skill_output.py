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
from tests.helpers import render_repo, write_skill


AGENT_NAME_LIST = ["claude", "cursor"]
EXPECTED_SKILL_A = (
    "---\n"
    'name: "a"\n'
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
    frontmatter_map = _frontmatter_map(_output_text(fixture_repo, f"{agent_name}/skills/a/SKILL.md"))

    assert frontmatter_map == {"name": "a", "description": 'Skill a1 does "a1" work. Use when a1.'}


@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_a_numeric_skill_name_stays_a_string_in_the_output(fixture_repo: Path, agent_name: str) -> None:
    write_skill(fixture_repo, "123", '---\nname: "123"\ndescription: d1\n---\n\n# N1\n\nText n1.\n')

    output_text = _output_text(fixture_repo, f"{agent_name}/skills/123/SKILL.md")

    assert _frontmatter_map(output_text)["name"] == "123"


@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_an_extra_file_is_copied_byte_for_byte_without_a_header(fixture_repo: Path, agent_name: str) -> None:
    output_file = render_repo(fixture_repo)[f"{agent_name}/skills/a/extra1.txt"]

    assert output_file.content == b"extra a1\n"
    assert output_file.executable is False


def test_an_executable_extra_file_keeps_its_exec_bit_on_disk(fixture_repo: Path) -> None:
    tool_file = fixture_repo / "skills" / "a" / "tool1"

    tool_file.write_bytes(b"#!/bin/sh\n")
    tool_file.chmod(0o755)

    assert generate.main([], fixture_repo) == 0

    for agent_name in AGENT_NAME_LIST:
        output_file = render_repo(fixture_repo)[f"{agent_name}/skills/a/tool1"]

        assert output_file.content == b"#!/bin/sh\n"
        assert output_file.executable is True
        assert (fixture_repo / "generated" / agent_name / "skills" / "a" / "tool1").stat().st_mode & 0o100


@pytest.mark.parametrize("flag_text", ["true", "false"])
@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_the_disable_model_invocation_flag_is_passed_through_as_a_boolean(
    fixture_repo: Path, agent_name: str, flag_text: str
) -> None:
    skill_file = fixture_repo / "skills" / "a" / "SKILL.md"
    master_text = skill_file.read_text(encoding="utf-8")

    skill_file.write_text(
        master_text.replace("---\n\n", f"disable-model-invocation: {flag_text}\n---\n\n", 1), encoding="utf-8"
    )

    output_text = _output_text(fixture_repo, f"{agent_name}/skills/a/SKILL.md")

    assert output_text == EXPECTED_SKILL_A.replace(
        "---\n<!--", f"disable-model-invocation: {flag_text}\n---\n<!--", 1
    )
    assert _frontmatter_map(output_text)["disable-model-invocation"] is (flag_text == "true")


# --------------------------------------------------------------------------------
# Real skill masters
# --------------------------------------------------------------------------------

@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_every_real_skill_keeps_its_frontmatter_for_each_agent(agent_name: str) -> None:
    output_by_path_map = render_repo(REPO_DIR)
    skill_dir_list = _real_skill_dir_list()

    assert skill_dir_list

    for skill_dir in skill_dir_list:
        master_frontmatter_map = _frontmatter_map((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
        output_text = output_by_path_map[f"{agent_name}/skills/{skill_dir.name}/SKILL.md"].content.decode("utf-8")

        assert _frontmatter_map(output_text) == master_frontmatter_map


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _output_text(repo_dir: Path, output_path: str) -> str:
    return render_repo(repo_dir)[output_path].content.decode("utf-8")


def _frontmatter_map(text: str) -> dict:
    block = text.split("\n---\n")[0].removeprefix("---\n")

    return yaml.safe_load(block)


def _real_skill_dir_list() -> list[Path]:
    skill_dir_list = []

    for entry in sorted((REPO_DIR / "skills").iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            skill_dir_list.append(entry)

    return skill_dir_list
