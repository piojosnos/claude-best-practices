# --------------------------------------------------------------------------------
# The committed output of the real repo: tracked, headed, without drift
# --------------------------------------------------------------------------------

import subprocess
from pathlib import Path

import pytest

from practices.command.command_runner import REPO_DIR
from practices.generated.generated_folder import GENERATED_FOLDER
from practices.masters.masters_reader import read_masters
from practices.masters.skill_reader import SKILL_FILE_NAME
from practices.rendering.agent_profile import AGENT_PROFILE_LIST
from tests.helpers import find_repo_drift, render_repo


AGENT_NAME_LIST = ["claude", "cursor"]


# --------------------------------------------------------------------------------
# Tracked and not ignored
# --------------------------------------------------------------------------------

def test_generated_output_is_tracked_and_not_ignored() -> None:
    if _git("rev-parse", "--is-inside-work-tree").returncode != 0:
        pytest.skip("not a git checkout")

    rendered_path_set = set(render_repo(REPO_DIR))
    tracked_path_set = _tracked_output_path_set()

    assert sorted(rendered_path_set - tracked_path_set) == [], "rendered but not tracked: git add generated"
    assert sorted(tracked_path_set - rendered_path_set) == [], "tracked but no longer rendered"

    for output_path in sorted(rendered_path_set):
        ignored_result = _git("check-ignore", "--no-index", f"{GENERATED_FOLDER}/{output_path}")

        assert ignored_result.returncode == 1, f"{GENERATED_FOLDER}/{output_path} is ignored"


# --------------------------------------------------------------------------------
# Headers
# --------------------------------------------------------------------------------

def test_every_rendered_file_carries_the_header_of_its_master() -> None:
    master_path_by_output_path_map = _master_path_by_output_path_map()

    assert master_path_by_output_path_map

    for output_path, master_path in master_path_by_output_path_map.items():
        output_file = REPO_DIR / GENERATED_FOLDER / output_path

        assert (REPO_DIR / master_path).is_file(), f"{master_path}: the master does not exist"
        assert _first_line_after_frontmatter(output_file) == (
            f"<!-- GENERATED from {master_path}; edit that file and regenerate -->"
        ), f"{GENERATED_FOLDER}/{output_path}: wrong header"


# --------------------------------------------------------------------------------
# Drift
# --------------------------------------------------------------------------------

def test_committed_output_has_no_drift() -> None:
    assert find_repo_drift(REPO_DIR) == []


# --------------------------------------------------------------------------------
# The update skill
# --------------------------------------------------------------------------------

def test_update_practice_skill_reads_and_names_the_generate_and_gate_commands() -> None:
    skill_by_name_map = {}

    for skill in read_masters(REPO_DIR).skill_list:
        skill_by_name_map[skill.name] = skill

    assert "bp-update-practice" in skill_by_name_map

    body = skill_by_name_map["bp-update-practice"].body

    assert "uv run --locked python -m practices.generate" in body
    assert "uv run --locked python -m practices.gate" in body

    for agent_name in AGENT_NAME_LIST:
        skill_file = REPO_DIR / GENERATED_FOLDER / agent_name / "skills" / "bp-update-practice" / "SKILL.md"

        assert skill_file.is_file()


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _git(*argument_list: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *argument_list], cwd=REPO_DIR, capture_output=True, text=True, check=False
    )


# --------------------------------------------------------------------------------

def _tracked_output_path_set() -> set[str]:
    tracked_path_set = set()
    prefix = f"{GENERATED_FOLDER}/"

    for line in _git("ls-files", "--", GENERATED_FOLDER).stdout.splitlines():
        tracked_path_set.add(line.removeprefix(prefix))

    return tracked_path_set


# --------------------------------------------------------------------------------

def _master_path_by_output_path_map() -> dict[str, str]:
    masters = read_masters(REPO_DIR)
    master_path_by_output_path_map = {}

    for profile in AGENT_PROFILE_LIST:
        for rule in masters.rule_list:
            output_path = f"{profile.name}/{profile.rule_folder}/{rule.name}{profile.rule_extension}"
            master_path_by_output_path_map[output_path] = rule.master_path

        for skill in masters.skill_list:
            output_path = f"{profile.name}/{profile.skill_folder}/{skill.name}/{SKILL_FILE_NAME}"
            master_path_by_output_path_map[output_path] = skill.master_path

    return master_path_by_output_path_map


# --------------------------------------------------------------------------------

def _first_line_after_frontmatter(output_file: Path) -> str:
    line_list = output_file.read_text(encoding="utf-8").split("\n")

    if line_list[0] != "---":
        return line_list[0]

    for index in range(1, len(line_list)):
        if line_list[index] == "---":
            return line_list[index + 1]

    return ""
