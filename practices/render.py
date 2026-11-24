# --------------------------------------------------------------------------------
# The renderer: the typed model through the agent templates to output files
# --------------------------------------------------------------------------------
# Python passes the model to Jinja and builds no file format itself; the
# differences between agents live in templates/<agent>/.
# --------------------------------------------------------------------------------

import json
from pathlib import Path

import jinja2

from practices.errors import PracticesError
from practices.model import Masters, OutputFile, Rule, Skill
from practices.profiles import AGENT_PROFILE_LIST, AgentProfile
from practices.skill_reader import SKILL_FILE_NAME


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

_TEMPLATES_FOLDER = "templates"
_MAX_SHORT_ESCAPE_CODE_POINT = 0xFFFF


# --------------------------------------------------------------------------------
# The Jinja environment
# --------------------------------------------------------------------------------
# A master body goes in as a value, so Jinja syntax inside it is never run.
# StrictUndefined turns a template typo into an error, not an empty value.
# --------------------------------------------------------------------------------

def _build_environment(templates_dir: Path) -> jinja2.Environment:
    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(templates_dir)),
        undefined=jinja2.StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )
    environment.filters["yaml_str"] = _yaml_str

    return environment


# --------------------------------------------------------------------------------

def _yaml_str(text: str) -> str:
    quoted_text = json.dumps(text, ensure_ascii=False)
    escaped_char_list = []

    for char in quoted_text:
        if not char.isprintable():
            escaped_char_list.append(_escape_code_point(ord(char)))
        else:
            escaped_char_list.append(char)

    return "".join(escaped_char_list)


# --------------------------------------------------------------------------------

def _escape_code_point(code_point: int) -> str:
    if code_point <= _MAX_SHORT_ESCAPE_CODE_POINT:
        return f"\\u{code_point:04x}"

    return f"\\U{code_point:08x}"


# --------------------------------------------------------------------------------
# Rendering every master
# --------------------------------------------------------------------------------

def render_all(masters: Masters, repo_dir: Path) -> dict[str, OutputFile]:
    environment = _build_environment(repo_dir / _TEMPLATES_FOLDER)
    output_by_path_map = {}

    for profile in AGENT_PROFILE_LIST:
        for rule in masters.rule_list:
            output_by_path_map.update(_render_rule(environment, profile, rule))

        for skill in masters.skill_list:
            output_by_path_map.update(_render_skill(environment, profile, skill))

    return _sorted_by_path(output_by_path_map)


# --------------------------------------------------------------------------------

def _render_rule(environment: jinja2.Environment, profile: AgentProfile, rule: Rule) -> dict[str, OutputFile]:
    output_path = f"{profile.name}/{profile.rule_folder}/{rule.name}{profile.rule_extension}"
    value_by_name_map = {"rule": rule, "master_path": rule.master_path}
    rule_content = _render_template(environment, profile.rule_template, value_by_name_map)

    return {output_path: OutputFile(rule_content, False)}


# --------------------------------------------------------------------------------

def _render_skill(environment: jinja2.Environment, profile: AgentProfile, skill: Skill) -> dict[str, OutputFile]:
    skill_path = f"{profile.name}/{profile.skill_folder}/{skill.name}"
    value_by_name_map = {"skill": skill, "master_path": skill.master_path}
    skill_content = _render_template(environment, profile.skill_template, value_by_name_map)
    output_by_path_map = {f"{skill_path}/{SKILL_FILE_NAME}": OutputFile(skill_content, False)}

    for extra_file in skill.extra_file_list:
        output_by_path_map[f"{skill_path}/{extra_file.path}"] = OutputFile(
            extra_file.content, extra_file.executable
        )

    return output_by_path_map


# --------------------------------------------------------------------------------

def _render_template(environment: jinja2.Environment, template_name: str, value_by_name_map: dict) -> bytes:
    try:
        template = environment.get_template(template_name)
        text = template.render(value_by_name_map)
    except jinja2.TemplateError as e:
        raise PracticesError(f"{template_name}: {e}") from e

    return text.encode("utf-8")


# --------------------------------------------------------------------------------

def _sorted_by_path(output_by_path_map: dict[str, OutputFile]) -> dict[str, OutputFile]:
    sorted_map = {}

    for output_path in sorted(output_by_path_map):
        sorted_map[output_path] = output_by_path_map[output_path]

    return sorted_map
