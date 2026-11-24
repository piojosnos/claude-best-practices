# --------------------------------------------------------------------------------
# The committed output of the real repo: tracked, headed, without drift
# --------------------------------------------------------------------------------

import subprocess
from pathlib import Path

from practices.check import find_drift
from practices.cli import REPO_DIR
from practices.output import GENERATED_FOLDER
from practices.reader import read_masters
from tests.helpers import render_repo


AGENT_NAME_LIST = ["claude", "cursor"]


# --------------------------------------------------------------------------------
# Tracked and not ignored
# --------------------------------------------------------------------------------

def test_generated_output_is_tracked_and_not_ignored() -> None:
    tracked_result = _git("ls-files", "--", GENERATED_FOLDER)

    assert tracked_result.stdout.strip()

    for output_path in render_repo(REPO_DIR):
        ignored_result = _git("check-ignore", "--no-index", f"{GENERATED_FOLDER}/{output_path}")

        assert ignored_result.returncode == 1, f"{GENERATED_FOLDER}/{output_path} is ignored"


# --------------------------------------------------------------------------------
# Headers
# --------------------------------------------------------------------------------

def test_every_rendered_file_carries_the_header_of_its_master() -> None:
    header_file_list = _rendered_header_file_list()

    assert header_file_list

    for output_file, master_path in header_file_list:
        assert (REPO_DIR / master_path).is_file(), f"{master_path}: the master does not exist"
        assert _first_line_after_frontmatter(output_file) == (
            f"<!-- GENERATED from {master_path}; edit that file and regenerate -->"
        ), f"{output_file.relative_to(REPO_DIR).as_posix()}: wrong header"


# --------------------------------------------------------------------------------
# Drift
# --------------------------------------------------------------------------------

def test_committed_output_has_no_drift() -> None:
    assert find_drift(REPO_DIR) == []


# --------------------------------------------------------------------------------
# The update skill
# --------------------------------------------------------------------------------

def test_update_practice_skill_reads_and_names_the_generate_and_gate_commands() -> None:
    skill_by_name_map = {}

    for skill in read_masters(REPO_DIR).skill_list:
        skill_by_name_map[skill.name] = skill

    assert "update-practice" in skill_by_name_map

    body = skill_by_name_map["update-practice"].body

    assert "uv run --locked python -m practices.generate" in body
    assert "uv run --locked python -m practices.gate" in body

    for agent_name in AGENT_NAME_LIST:
        skill_file = REPO_DIR / GENERATED_FOLDER / agent_name / "skills" / "update-practice" / "SKILL.md"

        assert skill_file.is_file()


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _git(*argument_list: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *argument_list], cwd=REPO_DIR, capture_output=True, text=True, check=False
    )


def _rendered_header_file_list() -> list[tuple[Path, str]]:
    header_file_list = []

    for agent_name in AGENT_NAME_LIST:
        agent_dir = REPO_DIR / GENERATED_FOLDER / agent_name

        for rule_file in sorted((agent_dir / "rules").iterdir()):
            header_file_list.append((rule_file, f"rules/{rule_file.stem}.md"))

        for skill_dir in sorted((agent_dir / "skills").iterdir()):
            header_file_list.append((skill_dir / "SKILL.md", f"skills/{skill_dir.name}/SKILL.md"))

    return header_file_list


def _first_line_after_frontmatter(output_file: Path) -> str:
    line_list = output_file.read_text(encoding="utf-8").split("\n")

    if line_list[0] != "---":
        return line_list[0]

    for index in range(1, len(line_list)):
        if line_list[index] == "---":
            return line_list[index + 1]

    return ""
