# --------------------------------------------------------------------------------
# The reader: rule masters on disk to the typed model
# --------------------------------------------------------------------------------
# A plain sorted walk of rules/, one Rule per Markdown file.
# --------------------------------------------------------------------------------

from pathlib import Path

import yaml

from practices.cli import PracticesError
from practices.model import Masters, Rule


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

RULES_FOLDER = "rules"
_FRONTMATTER_FENCE = "---"
_PATHS_KEY = "paths"


# --------------------------------------------------------------------------------
# Reading the masters
# --------------------------------------------------------------------------------

def read_masters(repo_dir: Path) -> Masters:
    rules_dir = repo_dir / RULES_FOLDER

    if not rules_dir.is_dir():
        raise PracticesError(f"{RULES_FOLDER}: no such folder in {repo_dir}")

    master_file_list = []

    for entry in rules_dir.rglob("*"):
        if _is_master(rules_dir, entry):
            master_file_list.append(entry)

    rule_list = []

    for master_file in sorted(master_file_list, key=Path.as_posix):
        rule_list.append(read_rule(repo_dir, master_file))

    return Masters(rule_list)


def _is_master(rules_dir: Path, entry: Path) -> bool:
    for part in entry.relative_to(rules_dir).parts:
        if part.startswith("."):
            return False

    return entry.is_file() and entry.suffix == ".md"


def read_rule(repo_dir: Path, master_file: Path) -> Rule:
    master_path = master_file.relative_to(repo_dir).as_posix()
    name = master_file.relative_to(repo_dir / RULES_FOLDER).with_suffix("").as_posix()

    try:
        text = master_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise PracticesError(f"{master_path}: cannot read the master ({e})") from e

    frontmatter, body = split_frontmatter(text, master_path)

    return Rule(name, master_path, _read_path_list(frontmatter, master_path), body.strip("\n"))


def _read_path_list(frontmatter: dict, master_path: str) -> list[str]:
    value = frontmatter.get(_PATHS_KEY)

    if value is None:
        return []

    if not isinstance(value, list):
        raise PracticesError(f"{master_path}: the paths key must be a list of globs")

    path_list = []

    for glob in value:
        path_list.append(str(glob))

    return path_list


# --------------------------------------------------------------------------------
# Frontmatter
# --------------------------------------------------------------------------------

def split_frontmatter(text: str, master_path: str) -> tuple[dict, str]:
    line_list = text.split("\n")

    if line_list[0] != _FRONTMATTER_FENCE:
        return {}, text

    for index in range(1, len(line_list)):
        if line_list[index] == _FRONTMATTER_FENCE:
            block = "\n".join(line_list[1:index])
            body = "\n".join(line_list[index + 1:])

            return _parse_block(block, master_path), body

    raise PracticesError(f"{master_path}: the frontmatter is not closed")


def _parse_block(block: str, master_path: str) -> dict:
    try:
        parsed = yaml.safe_load(block)
    except yaml.YAMLError as e:
        raise PracticesError(f"{master_path}: the frontmatter is not valid YAML ({e})") from e

    if parsed is None:
        return {}

    if not isinstance(parsed, dict):
        raise PracticesError(f"{master_path}: the frontmatter must be a mapping")

    return parsed
