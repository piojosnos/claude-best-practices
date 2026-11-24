# --------------------------------------------------------------------------------
# The skill reader: skills/ on disk to typed Skill objects
# --------------------------------------------------------------------------------
# A skill is a non-hidden folder of skills/. Its SKILL.md is rendered; every other
# file in the folder is carried along as bytes.
# --------------------------------------------------------------------------------

from pathlib import Path

from practices.errors import PracticesError
from practices.frontmatter import check_keys, split_frontmatter
from practices.master_files import read_text, refuse_link
from practices.model import ExtraFile, Skill, is_executable


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

SKILL_FILE_NAME = "SKILL.md"
_SKILLS_FOLDER = "skills"
_NAME_KEY = "name"
_DESCRIPTION_KEY = "description"
_DISABLE_MODEL_INVOCATION_KEY = "disable-model-invocation"
_ALLOWED_SKILL_KEY_SET = {_NAME_KEY, _DESCRIPTION_KEY, _DISABLE_MODEL_INVOCATION_KEY}
_MAX_DESCRIPTION_LENGTH = 1024
_MAX_SKILL_NAME_LENGTH = 64


# --------------------------------------------------------------------------------
# Reading the skills
# --------------------------------------------------------------------------------

def read_skill_list(repo_dir: Path) -> list[Skill]:
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

    refuse_link(entry, master_path)

    if not entry.is_dir():
        raise PracticesError(f"{master_path}: {_SKILLS_FOLDER}/ holds only skill folders")

    return True


def _read_skill(repo_dir: Path, skill_dir: Path) -> Skill:
    skill_path = skill_dir.relative_to(repo_dir).as_posix()
    skill_file = skill_dir / SKILL_FILE_NAME
    master_path = f"{skill_path}/{SKILL_FILE_NAME}"

    refuse_link(skill_file, master_path)

    if not skill_file.is_file():
        raise PracticesError(f"{skill_path}: has no {SKILL_FILE_NAME}")

    frontmatter_map, body = split_frontmatter(read_text(skill_file, master_path), master_path)

    check_keys(frontmatter_map, master_path, _ALLOWED_SKILL_KEY_SET, "skill")

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


# --------------------------------------------------------------------------------
# Checking the frontmatter values
# --------------------------------------------------------------------------------

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


# --------------------------------------------------------------------------------
# Extra files
# --------------------------------------------------------------------------------

def _read_extra_file_list(skill_dir: Path, skill_path: str) -> list[ExtraFile]:
    extra_file_list = []

    for entry in sorted(skill_dir.rglob("*"), key=Path.as_posix):
        relative_path = entry.relative_to(skill_dir).as_posix()
        master_path = f"{skill_path}/{relative_path}"

        if _is_hidden_or_skill_file(relative_path):
            continue

        refuse_link(entry, master_path)

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
