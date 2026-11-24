# --------------------------------------------------------------------------------
# The Claude rule format: exact bytes, the YAML round trip and literal Jinja text
# --------------------------------------------------------------------------------
# The expected text is written from the format, never copied from a generator run.
# --------------------------------------------------------------------------------

from pathlib import Path

import yaml

from practices.cli import REPO_DIR
from practices.model import Rule
from practices.reader import read_masters
from practices.render import render_all

EXPECTED_CLAUDE_RULE_A = (
    "<!-- GENERATED from rules/a.md; edit that file and regenerate -->\n"
    "\n"
    "# A1\n"
    "\n"
    "Text a1.\n"
)
EXPECTED_CLAUDE_RULE_B = (
    "---\n"
    "paths:\n"
    '  - "**/*.b1"\n'
    '  - "**/b2*.txt"\n'
    "---\n"
    "<!-- GENERATED from rules/b.md; edit that file and regenerate -->\n"
    "\n"
    "# B1\n"
    "\n"
    "Text b1.\n"
)
JINJA_BODY_LINE = "Use {{ x1 }} and {% if y1 %}z1{% endif %}."


# --------------------------------------------------------------------------------
# Fixture masters
# --------------------------------------------------------------------------------

def test_claude_rule_without_paths_is_the_header_and_the_body(fixture_repo: Path) -> None:
    assert _output_text(fixture_repo, "claude/rules/a.md") == EXPECTED_CLAUDE_RULE_A


def test_claude_rule_with_paths_keeps_a_quoted_paths_list_before_the_header(fixture_repo: Path) -> None:
    assert _output_text(fixture_repo, "claude/rules/b.md") == EXPECTED_CLAUDE_RULE_B


def test_a_glob_with_a_hash_and_a_quote_survives_the_yaml_round_trip(fixture_repo: Path) -> None:
    glob = "**/#1'x.txt"

    _write_master(fixture_repo, "h1.md", f'---\npaths:\n  - "{glob}"\n---\n\n# H1\n\nText h1.\n')

    frontmatter, _ = _split_output(_output_text(fixture_repo, "claude/rules/h1.md"))

    assert frontmatter == {"paths": [glob]}


def test_jinja_syntax_in_a_master_body_renders_literally(fixture_repo: Path) -> None:
    _write_master(fixture_repo, "l1.md", f"# L1\n\n{JINJA_BODY_LINE}\n")
    output_by_path_map = render_all(fixture_repo)

    assert JINJA_BODY_LINE in output_by_path_map["claude/rules/l1.md"].content.decode("utf-8").split("\n")
    assert JINJA_BODY_LINE in output_by_path_map["cursor/rules/l1.mdc"].content.decode("utf-8").split("\n")


# --------------------------------------------------------------------------------
# Real masters
# --------------------------------------------------------------------------------

def test_every_real_master_round_trips_through_its_claude_output() -> None:
    output_by_path_map = render_all(REPO_DIR)

    for rule in read_masters(REPO_DIR).rule_list:
        text = output_by_path_map[f"claude/rules/{rule.name}.md"].content.decode("utf-8")
        frontmatter, rest = _split_output(text)

        assert frontmatter == _expected_frontmatter(rule), rule.name
        assert rest.split("\n")[0] == _header_line(rule), rule.name


def test_every_output_ends_with_exactly_one_newline(fixture_repo: Path) -> None:
    for repo_dir in [fixture_repo, REPO_DIR]:
        for output_path, output_file in render_all(repo_dir).items():
            text = output_file.content.decode("utf-8")

            assert text.endswith("\n") and not text.endswith("\n\n"), output_path


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _output_text(repo_dir: Path, output_path: str) -> str:
    return render_all(repo_dir)[output_path].content.decode("utf-8")


def _write_master(repo_dir: Path, relative_name: str, content: str) -> None:
    (repo_dir / "rules" / relative_name).write_text(content, encoding="utf-8")


def _split_output(text: str) -> tuple[dict | None, str]:
    line_list = text.split("\n")

    if line_list[0] != "---":
        return None, text

    closing_index = line_list.index("---", 1)
    frontmatter = yaml.safe_load("\n".join(line_list[1:closing_index]))

    return frontmatter, "\n".join(line_list[closing_index + 1:])


def _expected_frontmatter(rule: Rule) -> dict | None:
    if not rule.path_list:
        return None

    return {"paths": rule.path_list}


def _header_line(rule: Rule) -> str:
    return f"<!-- GENERATED from {rule.master_path}; edit that file and regenerate -->"
