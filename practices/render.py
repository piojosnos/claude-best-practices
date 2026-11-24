# --------------------------------------------------------------------------------
# The renderer: the typed model through the agent templates to output files
# --------------------------------------------------------------------------------
# Python passes the model to Jinja and builds no file format itself; the
# differences between agents live in templates/<agent>/.
# --------------------------------------------------------------------------------

import json
from pathlib import Path

import jinja2

from practices.cli import PracticesError
from practices.model import OutputFile, Rule
from practices.profiles import AGENT_PROFILE_LIST, AgentProfile
from practices.reader import read_masters


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

TEMPLATES_FOLDER = "templates"


# --------------------------------------------------------------------------------
# The Jinja environment
# --------------------------------------------------------------------------------
# A master body goes in as a value, so Jinja syntax inside it is never run.
# StrictUndefined turns a template typo into an error, not an empty value.
# --------------------------------------------------------------------------------

def build_environment(templates_dir: Path) -> jinja2.Environment:
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


def _yaml_str(text: str) -> str:
    return json.dumps(text, ensure_ascii=False)


# --------------------------------------------------------------------------------
# Rendering every master
# --------------------------------------------------------------------------------

def render_all(repo_dir: Path) -> dict[str, OutputFile]:
    masters = read_masters(repo_dir)
    environment = build_environment(repo_dir / TEMPLATES_FOLDER)
    output_by_path_map = {}

    for profile in AGENT_PROFILE_LIST:
        for rule in masters.rule_list:
            output_path = f"{profile.name}/{profile.rule_folder}/{rule.name}{profile.rule_extension}"
            output_by_path_map[output_path] = OutputFile(_render_rule(environment, profile, rule), False)

    return _sorted_by_path(output_by_path_map)


def _render_rule(environment: jinja2.Environment, profile: AgentProfile, rule: Rule) -> bytes:
    try:
        template = environment.get_template(profile.rule_template)
        text = template.render(rule=rule, master_path=rule.master_path)
    except jinja2.TemplateError as e:
        raise PracticesError(f"{profile.rule_template}: {e}") from e

    return text.encode("utf-8")


def _sorted_by_path(output_by_path_map: dict[str, OutputFile]) -> dict[str, OutputFile]:
    sorted_map = {}

    for output_path in sorted(output_by_path_map):
        sorted_map[output_path] = output_by_path_map[output_path]

    return sorted_map
