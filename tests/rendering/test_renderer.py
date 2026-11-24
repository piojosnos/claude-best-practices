# --------------------------------------------------------------------------------
# The renderer: each agent's rule format and the skill files, byte for byte
# --------------------------------------------------------------------------------
# The expected text is written from the format, never copied from a generator run.
# --------------------------------------------------------------------------------

from pathlib import Path

import pytest
import yaml

from practices import generate
from practices.command.command_runner import REPO_DIR
from practices.masters.masters_model import Rule
from practices.masters.masters_reader import read_masters
from tests.helpers import render_repo, write_master, write_skill


AGENT_NAME_LIST = ["claude", "cursor"]
EXPECTED_CLAUDE_RULE_A = (
    "<!-- GENERATED from rules/a.md; edit that file and regenerate -->\n"
    "\n"
    "# A1\n"
    "\n"
    "Text a1.\n"
)
EXPECTED_CLAUDE_RULE_B = (
    "---\n"
    "paths:\n"
    '  - "**/*.b1"\n'
    '  - "**/b2*.txt"\n'
    "---\n"
    "<!-- GENERATED from rules/b.md; edit that file and regenerate -->\n"
    "\n"
    "# B1\n"
    "\n"
    "Text b1.\n"
)
EXPECTED_CURSOR_RULE_A = (
    "---\n"
    "alwaysApply: true\n"
    "---\n"
    "<!-- GENERATED from rules/a.md; edit that file and regenerate -->\n"
    "\n"
    "# A1\n"
    "\n"
    "Text a1.\n"
)
EXPECTED_CURSOR_RULE_B = (
    "---\n"
    "globs: **/*.b1, **/b2*.txt\n"
    "alwaysApply: false\n"
    "---\n"
    "<!-- GENERATED from rules/b.md; edit that file and regenerate -->\n"
    "\n"
    "# B1\n"
    "\n"
    "Text b1.\n"
)
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
JINJA_BODY_LINE = "Use {{ x1 }} and {% if y1 %}z1{% endif %}."


# --------------------------------------------------------------------------------
# Claude rules
# --------------------------------------------------------------------------------

def test_claude_rule_without_paths_is_the_header_and_the_body(fixture_repo: Path) -> None:
    assert _output_text(fixture_repo, "claude/rules/a.md") == EXPECTED_CLAUDE_RULE_A


# --------------------------------------------------------------------------------

def test_claude_rule_with_paths_keeps_a_quoted_paths_list_before_the_header(fixture_repo: Path) -> None:
    assert _output_text(fixture_repo, "claude/rules/b.md") == EXPECTED_CLAUDE_RULE_B


# --------------------------------------------------------------------------------

def test_a_glob_with_a_hash_and_a_quote_survives_the_yaml_round_trip(fixture_repo: Path) -> None:
    glob = "**/#1'x.txt"

    write_master(fixture_repo, "h1.md", f'---\npaths:\n  - "{glob}"\n---\n\n# H1\n\nText h1.\n')

    frontmatter_map, _ = _split_output(_output_text(fixture_repo, "claude/rules/h1.md"))

    assert frontmatter_map == {"paths": [glob]}


# --------------------------------------------------------------------------------

def test_jinja_syntax_in_a_master_body_renders_literally(fixture_repo: Path) -> None:
    write_master(fixture_repo, "l1.md", f"# L1\n\n{JINJA_BODY_LINE}\n")
    generated_file_by_path_map = render_repo(fixture_repo)

    assert JINJA_BODY_LINE in generated_file_by_path_map["claude/rules/l1.md"].content.decode("utf-8").split("\n")
    assert JINJA_BODY_LINE in generated_file_by_path_map["cursor/rules/l1.mdc"].content.decode("utf-8").split("\n")


# --------------------------------------------------------------------------------

def test_every_real_master_round_trips_through_its_claude_output() -> None:
    generated_file_by_path_map = render_repo(REPO_DIR)

    for rule in read_masters(REPO_DIR).rule_list:
        text = generated_file_by_path_map[f"claude/rules/{rule.name}.md"].content.decode("utf-8")
        frontmatter_map, rest = _split_output(text)

        assert frontmatter_map == _expected_frontmatter_map(rule), rule.name
        assert rest.split("\n")[0] == _header_line(rule), rule.name


# --------------------------------------------------------------------------------

def test_every_output_ends_with_exactly_one_newline(fixture_repo: Path) -> None:
    for repo_dir in [fixture_repo, REPO_DIR]:
        for output_path, generated_file in render_repo(repo_dir).items():
            text = generated_file.content.decode("utf-8")

            assert text.endswith("\n") and not text.endswith("\n\n"), output_path


# --------------------------------------------------------------------------------

def test_output_keys_are_sorted_whatever_the_creation_order(fixture_repo: Path) -> None:
    write_master(fixture_repo, "z1.md", "# R1\n\nText r1.\n")
    write_master(fixture_repo, "c1.md", "# R1\n\nText r1.\n")

    output_path_list = list(render_repo(fixture_repo))

    assert output_path_list == sorted(output_path_list)
    assert "claude/rules/c1.md" in output_path_list


# --------------------------------------------------------------------------------
# Cursor rules
# --------------------------------------------------------------------------------
# The globs line is comma separated text, not YAML, so these tests read lines and
# never parse the frontmatter.
# --------------------------------------------------------------------------------

def test_cursor_rule_without_paths_is_always_apply(fixture_repo: Path) -> None:
    assert _output_text(fixture_repo, "cursor/rules/a.mdc") == EXPECTED_CURSOR_RULE_A


# --------------------------------------------------------------------------------

def test_cursor_rule_with_paths_joins_the_globs_and_is_not_always_apply(fixture_repo: Path) -> None:
    assert _output_text(fixture_repo, "cursor/rules/b.mdc") == EXPECTED_CURSOR_RULE_B


# --------------------------------------------------------------------------------

def test_every_real_master_has_its_globs_and_always_apply_lines() -> None:
    generated_file_by_path_map = render_repo(REPO_DIR)

    for rule in read_masters(REPO_DIR).rule_list:
        line_list = generated_file_by_path_map[f"cursor/rules/{rule.name}.mdc"].content.decode("utf-8").split("\n")
        header = f"<!-- GENERATED from {rule.master_path}; edit that file and regenerate -->"

        assert line_list[0] == "---", rule.name

        if rule.path_list:
            assert line_list[1] == "globs: " + ", ".join(rule.path_list), rule.name
            assert line_list[2] == "alwaysApply: false", rule.name
            assert line_list[3] == "---", rule.name
            assert line_list[4] == header, rule.name
        else:
            assert line_list[1] == "alwaysApply: true", rule.name
            assert line_list[2] == "---", rule.name
            assert line_list[3] == header, rule.name


# --------------------------------------------------------------------------------
# Skills
# --------------------------------------------------------------------------------
# Both agents get the same skill files: the rendered SKILL.md and the extra files.
# --------------------------------------------------------------------------------

@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_the_skill_file_is_the_frontmatter_the_header_and_the_body(fixture_repo: Path, agent_name: str) -> None:
    assert _output_text(fixture_repo, f"{agent_name}/skills/a/SKILL.md") == EXPECTED_SKILL_A


# --------------------------------------------------------------------------------

@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_the_skill_frontmatter_round_trips_through_yaml(fixture_repo: Path, agent_name: str) -> None:
    frontmatter_map = _frontmatter_map(_output_text(fixture_repo, f"{agent_name}/skills/a/SKILL.md"))

    assert frontmatter_map == {"name": "a", "description": 'Skill a1 does "a1" work. Use when a1.'}


# --------------------------------------------------------------------------------

@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_a_numeric_skill_name_stays_a_string_in_the_output(fixture_repo: Path, agent_name: str) -> None:
    write_skill(fixture_repo, "123", '---\nname: "123"\ndescription: d1\n---\n\n# N1\n\nText n1.\n')

    output_text = _output_text(fixture_repo, f"{agent_name}/skills/123/SKILL.md")

    assert _frontmatter_map(output_text)["name"] == "123"


# --------------------------------------------------------------------------------

@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_a_description_with_odd_characters_survives_the_yaml_round_trip(fixture_repo: Path, agent_name: str) -> None:
    description = "a\x85b\x7fc\u2028d\u00a0e\U0001f600f"

    write_skill(
        fixture_repo,
        "x1",
        '---\nname: x1\ndescription: "a\\x85b\\x7fc\\u2028d\\u00a0e\\U0001f600f"\n---\n\n# X1\n\nText x1.\n',
    )

    output_text = _output_text(fixture_repo, f"{agent_name}/skills/x1/SKILL.md")

    assert _frontmatter_map(output_text)["description"] == description


# --------------------------------------------------------------------------------

@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_an_extra_file_is_copied_byte_for_byte_without_a_header(fixture_repo: Path, agent_name: str) -> None:
    generated_file = render_repo(fixture_repo)[f"{agent_name}/skills/a/extra1.txt"]

    assert generated_file.content == b"extra a1\n"
    assert generated_file.executable is False


# --------------------------------------------------------------------------------

def test_an_executable_extra_file_keeps_its_exec_bit_on_disk(fixture_repo: Path) -> None:
    tool_file = fixture_repo / "skills" / "a" / "tool1"

    tool_file.write_bytes(b"#!/bin/sh\n")
    tool_file.chmod(0o755)

    assert generate.main([], fixture_repo) == 0

    for agent_name in AGENT_NAME_LIST:
        generated_file = render_repo(fixture_repo)[f"{agent_name}/skills/a/tool1"]

        assert generated_file.content == b"#!/bin/sh\n"
        assert generated_file.executable is True
        assert (fixture_repo / "generated" / agent_name / "skills" / "a" / "tool1").stat().st_mode & 0o100


# --------------------------------------------------------------------------------

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

@pytest.mark.parametrize("agent_name", AGENT_NAME_LIST)
def test_every_real_skill_keeps_its_frontmatter_for_each_agent(agent_name: str) -> None:
    generated_file_by_path_map = render_repo(REPO_DIR)
    skill_dir_list = _real_skill_dir_list()

    assert skill_dir_list

    for skill_dir in skill_dir_list:
        master_frontmatter_map = _frontmatter_map((skill_dir / "SKILL.md").read_text(encoding="utf-8"))
        output_text = generated_file_by_path_map[f"{agent_name}/skills/{skill_dir.name}/SKILL.md"].content.decode(
            "utf-8"
        )

        assert _frontmatter_map(output_text) == master_frontmatter_map


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _output_text(repo_dir: Path, output_path: str) -> str:
    return render_repo(repo_dir)[output_path].content.decode("utf-8")


# --------------------------------------------------------------------------------

def _split_output(text: str) -> tuple[dict | None, str]:
    line_list = text.split("\n")

    if line_list[0] != "---":
        return None, text

    closing_index = line_list.index("---", 1)
    frontmatter_map = yaml.safe_load("\n".join(line_list[1:closing_index]))

    return frontmatter_map, "\n".join(line_list[closing_index + 1:])


# --------------------------------------------------------------------------------

def _expected_frontmatter_map(rule: Rule) -> dict | None:
    if not rule.path_list:
        return None

    return {"paths": rule.path_list}


# --------------------------------------------------------------------------------

def _header_line(rule: Rule) -> str:
    return f"<!-- GENERATED from {rule.master_path}; edit that file and regenerate -->"


# --------------------------------------------------------------------------------

def _frontmatter_map(text: str) -> dict:
    block = text.split("\n---\n", 1)[0].removeprefix("---\n")

    return yaml.safe_load(block)


# --------------------------------------------------------------------------------

def _real_skill_dir_list() -> list[Path]:
    skill_dir_list = []

    for entry in sorted((REPO_DIR / "skills").iterdir()):
        if entry.is_dir() and not entry.name.startswith("."):
            skill_dir_list.append(entry)

    return skill_dir_list
