# --------------------------------------------------------------------------------
# The Cursor rule format: exact bytes and the globs and alwaysApply lines
# --------------------------------------------------------------------------------
# The globs line is comma separated text, not YAML, so these tests read lines and
# never parse the frontmatter.
# --------------------------------------------------------------------------------

from pathlib import Path

from practices.cli import REPO_DIR
from practices.reader import read_masters
from tests.helpers import render_repo


EXPECTED_CURSOR_RULE_A = (
    "---\n"
    "alwaysApply: true\n"
    "---\n"
    "<!-- GENERATED from rules/a.md; edit that file and regenerate -->\n"
    "\n"
    "# A1\n"
    "\n"
    "Text a1.\n"
)
EXPECTED_CURSOR_RULE_B = (
    "---\n"
    "globs: **/*.b1, **/b2*.txt\n"
    "alwaysApply: false\n"
    "---\n"
    "<!-- GENERATED from rules/b.md; edit that file and regenerate -->\n"
    "\n"
    "# B1\n"
    "\n"
    "Text b1.\n"
)


# --------------------------------------------------------------------------------
# Fixture masters
# --------------------------------------------------------------------------------

def test_cursor_rule_without_paths_is_always_apply(fixture_repo: Path) -> None:
    assert _output_text(fixture_repo, "cursor/rules/a.mdc") == EXPECTED_CURSOR_RULE_A


# --------------------------------------------------------------------------------

def test_cursor_rule_with_paths_joins_the_globs_and_is_not_always_apply(fixture_repo: Path) -> None:
    assert _output_text(fixture_repo, "cursor/rules/b.mdc") == EXPECTED_CURSOR_RULE_B


# --------------------------------------------------------------------------------
# Real masters
# --------------------------------------------------------------------------------

def test_every_real_master_has_its_globs_and_always_apply_lines() -> None:
    output_by_path_map = render_repo(REPO_DIR)

    for rule in read_masters(REPO_DIR).rule_list:
        line_list = output_by_path_map[f"cursor/rules/{rule.name}.mdc"].content.decode("utf-8").split("\n")
        header = f"<!-- GENERATED from {rule.master_path}; edit that file and regenerate -->"

        assert line_list[0] == "---", rule.name

        if rule.path_list:
            assert line_list[1] == "globs: " + ", ".join(rule.path_list), rule.name
            assert line_list[2] == "alwaysApply: false", rule.name
            assert line_list[3] == "---", rule.name
            assert line_list[4] == header, rule.name
        else:
            assert line_list[1] == "alwaysApply: true", rule.name
            assert line_list[2] == "---", rule.name
            assert line_list[3] == header, rule.name


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _output_text(repo_dir: Path, output_path: str) -> str:
    return render_repo(repo_dir)[output_path].content.decode("utf-8")
