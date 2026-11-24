# --------------------------------------------------------------------------------
# The masters stay agent-neutral: no agent path, tool or command syntax
# --------------------------------------------------------------------------------
# CLAUDE.md is not forbidden: the pr-reply skill names it next to AGENTS.md on purpose.
# --------------------------------------------------------------------------------

from pathlib import Path

from practices.cli import REPO_DIR


FORBIDDEN_TEXT_LIST = [
    ".claude/",
    "~/.claude",
    ".cursor/",
    "~/.cursor",
    "AskUserQuestion",
    "gsd-tools.cjs",
    "/gsd-",
    "/home/",
]
BEST_PRACTICES_RULE = "rules/best-practices.md"


# --------------------------------------------------------------------------------
# Every master
# --------------------------------------------------------------------------------

def test_no_master_names_an_agent_path_or_tool() -> None:
    master_file_list = _master_file_list()
    problem_list = []

    assert master_file_list

    for master_file in master_file_list:
        master_path = master_file.relative_to(REPO_DIR).as_posix()
        text = master_file.read_text(encoding="utf-8")

        for forbidden_text in FORBIDDEN_TEXT_LIST:
            if forbidden_text in text:
                problem_list.append(f"{master_path}: {forbidden_text}")

    assert problem_list == []


# --------------------------------------------------------------------------------
# The always-loaded rule
# --------------------------------------------------------------------------------

def test_the_best_practices_rule_points_at_the_masters_and_the_update_skill() -> None:
    text = (REPO_DIR / BEST_PRACTICES_RULE).read_text(encoding="utf-8")

    for expected_text in ["update-practice", "generated/"]:
        assert expected_text in text


def test_the_best_practices_rule_names_no_absolute_path() -> None:
    text = (REPO_DIR / BEST_PRACTICES_RULE).read_text(encoding="utf-8")

    assert "`/" not in text
    assert "~/" not in text


def test_finding_the_clone_names_the_folder_git_must_run_in() -> None:
    problem_list = []

    for master_file in _master_file_list():
        text = master_file.read_text(encoding="utf-8")

        for line in text.split("\n"):
            if "rev-parse --show-toplevel" in line and "git -C" not in line:
                problem_list.append(f"{master_file.relative_to(REPO_DIR).as_posix()}: {line.strip()}")

    assert problem_list == []


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _master_file_list() -> list[Path]:
    master_file_list = []

    for folder in ["rules", "skills"]:
        for entry in (REPO_DIR / folder).rglob("*"):
            if entry.is_file():
                master_file_list.append(entry)

    return sorted(master_file_list, key=Path.as_posix)
