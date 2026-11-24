# --------------------------------------------------------------------------------
# The rule reader: rules/ on disk to typed Rule objects
# --------------------------------------------------------------------------------
# One Rule per Markdown file, walked in sorted order; a rule master allows only
# a paths list in its frontmatter.
# --------------------------------------------------------------------------------

from pathlib import Path

from practices.error.practices_error import PracticesError
from practices.masters.frontmatter_parser import check_keys, split_frontmatter
from practices.masters.master_file import read_text, refuse_link
from practices.masters.masters_model import Rule


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

_RULES_FOLDER = "rules"
_PATHS_KEY = "paths"
_ALLOWED_RULE_KEY_SET = {_PATHS_KEY}


# --------------------------------------------------------------------------------
# Reading the rules
# --------------------------------------------------------------------------------

def read_rule_list(repo_dir: Path) -> list[Rule]:
    rules_dir = repo_dir / _RULES_FOLDER

    if not rules_dir.is_dir():
        raise PracticesError(f"{_RULES_FOLDER}: no such folder in {repo_dir}")

    master_file_list = []

    for entry in rules_dir.rglob("*"):
        if _is_master(repo_dir, rules_dir, entry):
            master_file_list.append(entry)

    rule_list = []

    for master_file in sorted(master_file_list, key=Path.as_posix):
        rule_list.append(_read_rule(repo_dir, master_file))

    return rule_list


# --------------------------------------------------------------------------------

def _is_master(repo_dir: Path, rules_dir: Path, entry: Path) -> bool:
    for part in entry.relative_to(rules_dir).parts:
        if part.startswith("."):
            return False

    master_path = entry.relative_to(repo_dir).as_posix()

    refuse_link(entry, master_path)

    if not entry.is_file():
        return False

    if entry.suffix != ".md":
        raise PracticesError(f"{master_path}: {_RULES_FOLDER}/ holds only .md rule files")

    return True


# --------------------------------------------------------------------------------

def _read_rule(repo_dir: Path, master_file: Path) -> Rule:
    master_path = master_file.relative_to(repo_dir).as_posix()
    name = master_file.relative_to(repo_dir / _RULES_FOLDER).with_suffix("").as_posix()
    text = read_text(master_file, master_path)
    frontmatter_map, body = split_frontmatter(text, master_path)

    check_keys(frontmatter_map, master_path, _ALLOWED_RULE_KEY_SET, "rule")

    path_list = []

    if _PATHS_KEY in frontmatter_map:
        path_list = _check_path_list(frontmatter_map[_PATHS_KEY], master_path)

    body = body.strip("\n")

    if not body.strip():
        raise PracticesError(f"{master_path}: the master has no text")

    return Rule(name, master_path, path_list, body)


# --------------------------------------------------------------------------------

def _check_path_list(path_list: object, master_path: str) -> list[str]:
    if not isinstance(path_list, list) or not path_list:
        raise PracticesError(f"{master_path}: paths must be a non-empty list of globs")

    for glob in path_list:
        if not isinstance(glob, str) or not glob:
            raise PracticesError(f"{master_path}: paths must be a non-empty list of globs")

        if "," in glob:
            raise PracticesError(
                f"{master_path}: the glob '{glob}' holds a comma; write one glob per entry"
            )

        if glob != glob.strip() or not glob.isprintable():
            raise PracticesError(
                f"{master_path}: the glob {glob!r} has a control character or a space at an end; write a plain glob"
            )

    return list(path_list)
