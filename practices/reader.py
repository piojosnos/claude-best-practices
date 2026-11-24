# --------------------------------------------------------------------------------
# The reader: rule and skill masters on disk to the typed model
# --------------------------------------------------------------------------------
# A plain sorted walk of rules/ (one Rule per Markdown file) and of skills/ (one
# Skill per folder, the same notion of a skill as the sandbox linker).
# --------------------------------------------------------------------------------

from pathlib import Path

import yaml

from practices.errors import PracticesError
from practices.model import ExtraFile, Masters, Rule, Skill, is_executable


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

_RULES_FOLDER = "rules"
_SKILLS_FOLDER = "skills"
SKILL_FILE_NAME = "SKILL.md"
_FRONTMATTER_FENCE = "---"
_PATHS_KEY = "paths"
_NAME_KEY = "name"
_DESCRIPTION_KEY = "description"
_DISABLE_MODEL_INVOCATION_KEY = "disable-model-invocation"
_ALLOWED_RULE_KEY_SET = {_PATHS_KEY}
_ALLOWED_SKILL_KEY_SET = {_NAME_KEY, _DESCRIPTION_KEY, _DISABLE_MODEL_INVOCATION_KEY}
_MAX_DESCRIPTION_LENGTH = 1024
_MAX_SKILL_NAME_LENGTH = 64


# --------------------------------------------------------------------------------
# Reading the masters
# --------------------------------------------------------------------------------

def read_masters(repo_dir: Path) -> Masters:
    return Masters(_read_rule_list(repo_dir), _read_skill_list(repo_dir))


def _read_rule_list(repo_dir: Path) -> list[Rule]:
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


def _is_master(repo_dir: Path, rules_dir: Path, entry: Path) -> bool:
    for part in entry.relative_to(rules_dir).parts:
        if part.startswith("."):
            return False

    master_path = entry.relative_to(repo_dir).as_posix()

    _refuse_link(entry, master_path)

    if not entry.is_file():
        return False

    if entry.suffix != ".md":
        raise PracticesError(f"{master_path}: {_RULES_FOLDER}/ holds only .md rule files")

    return True


def _read_rule(repo_dir: Path, master_file: Path) -> Rule:
    master_path = master_file.relative_to(repo_dir).as_posix()
    name = master_file.relative_to(repo_dir / _RULES_FOLDER).with_suffix("").as_posix()
    text = _read_text(master_file, master_path)
    frontmatter_map, body = _split_frontmatter(text, master_path)

    _check_keys(frontmatter_map, master_path, _ALLOWED_RULE_KEY_SET, "rule")

    path_list = []

    if _PATHS_KEY in frontmatter_map:
        path_list = _check_path_list(frontmatter_map[_PATHS_KEY], master_path)

    body = body.strip("\n")

    if not body.strip():
        raise PracticesError(f"{master_path}: the master has no text")

    return Rule(name, master_path, path_list, body)


def _refuse_link(entry: Path, master_path: str) -> None:
    if entry.is_symlink():
        raise PracticesError(f"{master_path}: is a link; a master is a plain file")


def _read_text(master_file: Path, master_path: str) -> str:
    try:
        return master_file.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        raise PracticesError(f"{master_path}: is not UTF-8 text") from e
    except OSError as e:
        raise PracticesError(f"{master_path}: cannot read the file") from e


def _check_keys(frontmatter_map: dict, master_path: str, allowed_key_set: set[str], kind: str) -> None:
    for key in sorted(frontmatter_map, key=str):
        if key not in allowed_key_set:
            allowed_text = ", ".join(sorted(allowed_key_set))

            raise PracticesError(
                f"{master_path}: unknown frontmatter key '{key}'; a {kind} allows only: {allowed_text}"
            )


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

    return list(path_list)


# --------------------------------------------------------------------------------
# Skills
# --------------------------------------------------------------------------------
# A skill is a non-hidden folder of skills/. Its SKILL.md is rendered; every other
# file in the folder is carried along as bytes, so the reader is the only code that
# touches master files.
# --------------------------------------------------------------------------------

def _read_skill_list(repo_dir: Path) -> list[Skill]:
    skills_dir = repo_dir / _SKILLS_FOLDER

    if not skills_dir.is_dir():
        raise PracticesError(f"{_SKILLS_FOLDER}: no such folder in {repo_dir}")

    skill_list = []

    for entry in sorted(skills_dir.iterdir(), key=Path.as_posix):
        if _is_skill_dir(repo_dir, entry):
            skill_list.append(_read_skill(repo_dir, entry))

    return skill_list


def _is_skill_dir(repo_dir: Path, entry: Path) -> bool:
    if entry.name.startswith("."):
        return False

    master_path = entry.relative_to(repo_dir).as_posix()

    _refuse_link(entry, master_path)

    if not entry.is_dir():
        raise PracticesError(f"{master_path}: {_SKILLS_FOLDER}/ holds only skill folders")

    return True


def _read_skill(repo_dir: Path, skill_dir: Path) -> Skill:
    skill_path = skill_dir.relative_to(repo_dir).as_posix()
    skill_file = skill_dir / SKILL_FILE_NAME
    master_path = f"{skill_path}/{SKILL_FILE_NAME}"

    _refuse_link(skill_file, master_path)

    if not skill_file.is_file():
        raise PracticesError(f"{skill_path}: has no {SKILL_FILE_NAME}")

    frontmatter_map, body = _split_frontmatter(_read_text(skill_file, master_path), master_path)

    _check_keys(frontmatter_map, master_path, _ALLOWED_SKILL_KEY_SET, "skill")

    name = frontmatter_map.get(_NAME_KEY)

    _check_name(name, skill_dir.name, master_path)

    description = frontmatter_map.get(_DESCRIPTION_KEY)

    _check_description(description, master_path)

    disable_model_invocation = _read_disable_model_invocation(frontmatter_map, master_path)

    body = body.strip("\n")

    if not body.strip():
        raise PracticesError(f"{master_path}: the master has no text")

    return Skill(
        name,
        master_path,
        description,
        body,
        _read_extra_file_list(skill_dir, skill_path),
        disable_model_invocation,
    )


def _check_name(name: object, folder_name: str, master_path: str) -> None:
    if name != folder_name:
        raise PracticesError(f"{master_path}: name must equal the folder name '{folder_name}'")

    if not _is_skill_name(folder_name):
        raise PracticesError(
            f"{master_path}: the name '{folder_name}' breaks the skill name rule: "
            f"lowercase letters and digits in words joined by single hyphens, "
            f"at most {_MAX_SKILL_NAME_LENGTH} characters"
        )


def _is_skill_name(name: str) -> bool:
    if len(name) > _MAX_SKILL_NAME_LENGTH:
        return False

    for word in name.split("-"):
        if not word or not word.isascii() or not word.isalnum() or word != word.lower():
            return False

    return True


def _check_description(description: object, master_path: str) -> None:
    if (
        not isinstance(description, str)
        or not description.strip()
        or len(description) > _MAX_DESCRIPTION_LENGTH
    ):
        raise PracticesError(
            f"{master_path}: description must be text of 1 to {_MAX_DESCRIPTION_LENGTH} characters"
        )


def _read_disable_model_invocation(frontmatter_map: dict, master_path: str) -> bool | None:
    if _DISABLE_MODEL_INVOCATION_KEY not in frontmatter_map:
        return None

    value = frontmatter_map[_DISABLE_MODEL_INVOCATION_KEY]

    if not isinstance(value, bool):
        raise PracticesError(f"{master_path}: {_DISABLE_MODEL_INVOCATION_KEY} must be true or false")

    return value


def _read_extra_file_list(skill_dir: Path, skill_path: str) -> list[ExtraFile]:
    extra_file_list = []

    for entry in sorted(skill_dir.rglob("*"), key=Path.as_posix):
        relative_path = entry.relative_to(skill_dir).as_posix()
        master_path = f"{skill_path}/{relative_path}"

        if _is_hidden_or_skill_file(relative_path):
            continue

        _refuse_link(entry, master_path)

        if entry.is_file():
            extra_file_list.append(_read_extra_file(entry, relative_path, master_path))

    return extra_file_list


def _is_hidden_or_skill_file(relative_path: str) -> bool:
    if relative_path == SKILL_FILE_NAME:
        return True

    for part in relative_path.split("/"):
        if part.startswith("."):
            return True

    return False


def _read_extra_file(entry: Path, relative_path: str, master_path: str) -> ExtraFile:
    try:
        content = entry.read_bytes()
    except OSError as e:
        raise PracticesError(f"{master_path}: cannot read the file") from e

    return ExtraFile(relative_path, content, is_executable(entry))


# --------------------------------------------------------------------------------
# Frontmatter
# --------------------------------------------------------------------------------

def _split_frontmatter(text: str, master_path: str) -> tuple[dict, str]:
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
        parsed_value = yaml.safe_load(block)
    except yaml.YAMLError as e:
        raise PracticesError(f"{master_path}: the frontmatter is not valid YAML") from e

    if parsed_value is None:
        return {}

    if not isinstance(parsed_value, dict):
        raise PracticesError(f"{master_path}: the frontmatter must be a mapping of keys")

    return parsed_value
