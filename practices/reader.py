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
ALLOWED_RULE_KEY_SET = {"paths"}
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
        if _is_master(repo_dir, rules_dir, entry):
            master_file_list.append(entry)

    rule_list = []

    for master_file in sorted(master_file_list, key=Path.as_posix):
        rule_list.append(read_rule(repo_dir, master_file))

    return Masters(rule_list)


def _is_master(repo_dir: Path, rules_dir: Path, entry: Path) -> bool:
    for part in entry.relative_to(rules_dir).parts:
        if part.startswith("."):
            return False

    master_path = entry.relative_to(repo_dir).as_posix()

    if entry.is_symlink():
        raise PracticesError(f"{master_path}: is a link; a master is a plain file")

    if not entry.is_file():
        return False

    if entry.suffix != ".md":
        raise PracticesError(f"{master_path}: {RULES_FOLDER}/ holds only .md rule files")

    return True


def read_rule(repo_dir: Path, master_file: Path) -> Rule:
    master_path = master_file.relative_to(repo_dir).as_posix()
    name = master_file.relative_to(repo_dir / RULES_FOLDER).with_suffix("").as_posix()
    text = _read_text(master_file, master_path)
    frontmatter, body = split_frontmatter(text, master_path)

    _check_keys(frontmatter, master_path)

    path_list = []

    if _PATHS_KEY in frontmatter:
        path_list = check_path_list(frontmatter[_PATHS_KEY], master_path)

    body = body.strip("\n")

    if not body.strip():
        raise PracticesError(f"{master_path}: the master has no text")

    return Rule(name, master_path, path_list, body)


def _read_text(master_file: Path, master_path: str) -> str:
    try:
        return master_file.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise PracticesError(f"{master_path}: is not UTF-8 text") from e
    except OSError as e:
        raise PracticesError(f"{master_path}: cannot read the file") from e


def _check_keys(frontmatter: dict, master_path: str) -> None:
    for key in sorted(frontmatter, key=str):
        if key not in ALLOWED_RULE_KEY_SET:
            allowed_text = ", ".join(sorted(ALLOWED_RULE_KEY_SET))

            raise PracticesError(
                f"{master_path}: unknown frontmatter key '{key}'; a rule allows only: {allowed_text}"
            )


def check_path_list(path_list: object, master_path: str) -> list[str]:
    if not isinstance(path_list, list) or not path_list:
        raise PracticesError(f"{master_path}: paths must be a non-empty list of globs")

    for glob in path_list:
        if not isinstance(glob, str) or not glob:
            raise PracticesError(f"{master_path}: paths must be a non-empty list of globs")

        if "," in glob:
            raise PracticesError(
                f"{master_path}: the glob '{glob}' holds a comma; write one glob per entry"
            )

    return list(path_list)


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

    raise PracticesError(f"{master_path}: the frontmatter has no closing {_FRONTMATTER_FENCE} line")


def _parse_block(block: str, master_path: str) -> dict:
    try:
        parsed = yaml.safe_load(block)
    except yaml.YAMLError as e:
        raise PracticesError(f"{master_path}: the frontmatter is not valid YAML") from e

    if parsed is None:
        return {}

    if not isinstance(parsed, dict):
        raise PracticesError(f"{master_path}: the frontmatter must be a mapping of keys")

    return parsed
