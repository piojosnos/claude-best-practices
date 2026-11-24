# --------------------------------------------------------------------------------
# The masters stay agent-neutral: no agent path, tool or command syntax
# --------------------------------------------------------------------------------
# CLAUDE.md is not forbidden: the pr-reply skill names it next to AGENTS.md on purpose.
# --------------------------------------------------------------------------------

from pathlib import Path

from practices.cli import REPO_DIR
from practices.reader import read_masters


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
    text_by_path_map = _master_text_by_path_map(REPO_DIR)
    problem_list = []

    assert text_by_path_map

    for master_path, text in text_by_path_map.items():
        for forbidden_text in FORBIDDEN_TEXT_LIST:
            if forbidden_text in text:
                problem_list.append(f"{master_path}: {forbidden_text}")

    assert problem_list == []


def test_the_master_walk_skips_hidden_and_binary_files(fixture_repo: Path) -> None:
    (fixture_repo / "rules" / ".DS_Store").write_bytes(b"\xff\xfe")
    (fixture_repo / "skills" / "a" / ".DS_Store").write_bytes(b"\xff\xfe")
    (fixture_repo / "skills" / "a" / "blob1.bin").write_bytes(b"\xff\xfe")

    assert list(_master_text_by_path_map(fixture_repo)) == [
        "rules/a.md",
        "rules/b.md",
        "skills/a/SKILL.md",
        "skills/a/extra1.txt",
    ]


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

    for master_path, text in _master_text_by_path_map(REPO_DIR).items():
        for line in text.split("\n"):
            if "rev-parse --show-toplevel" in line and "git -C" not in line:
                problem_list.append(f"{master_path}: {line.strip()}")

    assert problem_list == []


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _master_text_by_path_map(repo_dir: Path) -> dict[str, str]:
    masters = read_masters(repo_dir)
    text_by_path_map = {}

    for rule in masters.rule_list:
        text_by_path_map[rule.master_path] = (repo_dir / rule.master_path).read_text(encoding="utf-8")

    for skill in masters.skill_list:
        text_by_path_map[skill.master_path] = (repo_dir / skill.master_path).read_text(encoding="utf-8")

        for extra_file in skill.extra_file_list:
            extra_path = f"skills/{skill.name}/{extra_file.path}"

            try:
                text_by_path_map[extra_path] = extra_file.content.decode("utf-8")
            except UnicodeDecodeError:
                continue

    return text_by_path_map
