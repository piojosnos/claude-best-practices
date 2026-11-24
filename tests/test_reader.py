# --------------------------------------------------------------------------------
# The reader: the typed model, the sorted walk and the strict rule dialect
# --------------------------------------------------------------------------------
# Real master files written under tmp_path; a broken master must stop the run with
# a message that starts with the master's path.
# --------------------------------------------------------------------------------

from pathlib import Path

import pytest

from practices.cli import PracticesError
from practices.model import Rule
from practices.reader import read_masters

BROKEN_RULE_MASTER_LIST = [
    (
        '---\npath:\n  - "**/*.x1"\n---\n\n# X1\n\nText x1.\n',
        "rules/x1.md: unknown frontmatter key 'path'; a rule allows only: paths",
    ),
    (
        '---\ndescription: d1\npaths:\n  - "**/*.x1"\n---\n\n# X1\n\nText x1.\n',
        "rules/x1.md: unknown frontmatter key 'description'; a rule allows only: paths",
    ),
    (
        '---\npaths: "**/*.x1"\n---\n\n# X1\n\nText x1.\n',
        "rules/x1.md: paths must be a non-empty list of globs",
    ),
    (
        "---\npaths: []\n---\n\n# X1\n\nText x1.\n",
        "rules/x1.md: paths must be a non-empty list of globs",
    ),
    (
        "---\npaths:\n  - 5\n---\n\n# X1\n\nText x1.\n",
        "rules/x1.md: paths must be a non-empty list of globs",
    ),
    (
        '---\npaths:\n  - ""\n---\n\n# X1\n\nText x1.\n',
        "rules/x1.md: paths must be a non-empty list of globs",
    ),
    (
        '---\npaths:\n  - "**/*.{x1,x2}"\n---\n\n# X1\n\nText x1.\n',
        "rules/x1.md: the glob '**/*.{x1,x2}' holds a comma; write one glob per entry",
    ),
    (
        "---\npaths: [unclosed\n---\n\n# X1\n\nText x1.\n",
        "rules/x1.md: the frontmatter is not valid YAML",
    ),
    (
        "---\n- a1\n---\n\n# X1\n\nText x1.\n",
        "rules/x1.md: the frontmatter must be a mapping of keys",
    ),
    (
        '---\npaths:\n  - "**/*.x1"\n\n# X1\n\nText x1.\n',
        "rules/x1.md: the frontmatter has no closing --- line",
    ),
    (
        '---\npaths:\n  - "**/*.x1"\n---\n',
        "rules/x1.md: the master has no text",
    ),
    (
        "\n\n\n",
        "rules/x1.md: the master has no text",
    ),
]


# --------------------------------------------------------------------------------
# The typed model and the walk
# --------------------------------------------------------------------------------

def test_reader_returns_typed_rules_of_the_fixture_masters(fixture_repo: Path) -> None:
    assert read_masters(fixture_repo).rule_list == [
        Rule("a", "rules/a.md", [], "# A1\n\nText a1."),
        Rule("b", "rules/b.md", ["**/*.b1", "**/b2*.txt"], "# B1\n\nText b1."),
    ]


def test_masters_come_back_sorted_by_name(fixture_repo: Path) -> None:
    _write_master(fixture_repo, "z1.md", "# Z1\n\nText z1.\n")
    _write_master(fixture_repo, "c1.md", "# C1\n\nText c1.\n")

    assert _name_list(fixture_repo) == ["a", "b", "c1", "z1"]


def test_a_master_in_a_subfolder_is_named_with_its_folder(fixture_repo: Path) -> None:
    _write_master(fixture_repo, "sub1/d1.md", "# D1\n\nText d1.\n")

    assert _name_list(fixture_repo) == ["a", "b", "sub1/d1"]


def test_a_master_with_crlf_line_ends_reads_like_its_lf_twin(fixture_repo: Path) -> None:
    lf_text = '---\npaths:\n  - "**/*.x1"\n---\n\n# X1\n\nText x1.\n'

    _write_master(fixture_repo, "x1.md", lf_text)
    lf_rule = _rule_named(fixture_repo, "x1")

    (fixture_repo / "rules" / "x1.md").write_bytes(lf_text.replace("\n", "\r\n").encode("utf-8"))

    assert _rule_named(fixture_repo, "x1") == lf_rule


def test_hidden_entries_in_rules_are_skipped(fixture_repo: Path) -> None:
    _write_master(fixture_repo, ".DS_Store", "not a master")
    _write_master(fixture_repo, ".hidden1/e1.md", "# E1\n\nText e1.\n")

    assert _name_list(fixture_repo) == ["a", "b"]


def test_a_body_keeps_trailing_spaces_and_loses_only_newlines(fixture_repo: Path) -> None:
    _write_master(fixture_repo, "x1.md", "\n\n# X1\n\nText x1.  \n\n\n")

    assert _rule_named(fixture_repo, "x1").body == "# X1\n\nText x1.  "


# --------------------------------------------------------------------------------
# Rejections
# --------------------------------------------------------------------------------

@pytest.mark.parametrize("content, message", BROKEN_RULE_MASTER_LIST)
def test_reader_rejects_a_broken_rule_master(fixture_repo: Path, content: str, message: str) -> None:
    _write_master(fixture_repo, "x1.md", content)

    with pytest.raises(PracticesError) as raised:
        read_masters(fixture_repo)

    assert str(raised.value) == message


def test_reader_rejects_a_file_in_rules_that_is_not_md(fixture_repo: Path) -> None:
    _write_master(fixture_repo, "notes1.txt", "Text n1.\n")

    with pytest.raises(PracticesError) as raised:
        read_masters(fixture_repo)

    assert str(raised.value) == "rules/notes1.txt: rules/ holds only .md rule files"


def test_reader_rejects_a_link_in_rules(fixture_repo: Path, tmp_path: Path) -> None:
    outside_file = tmp_path / "outside1.md"
    outside_file.write_text("# O1\n\nText o1.\n", encoding="utf-8")
    (fixture_repo / "rules" / "c1.md").symlink_to(outside_file)

    with pytest.raises(PracticesError) as raised:
        read_masters(fixture_repo)

    assert str(raised.value) == "rules/c1.md: is a link; a master is a plain file"


def test_reader_rejects_a_master_that_is_invalid_utf8(fixture_repo: Path) -> None:
    (fixture_repo / "rules" / "x1.md").write_bytes(b"\xff\xfe")

    with pytest.raises(PracticesError) as raised:
        read_masters(fixture_repo)

    assert str(raised.value) == "rules/x1.md: is not UTF-8 text"


# --------------------------------------------------------------------------------
# TDL
# --------------------------------------------------------------------------------

def _write_master(repo_dir: Path, relative_name: str, content: str) -> None:
    master_file = repo_dir / "rules" / relative_name

    master_file.parent.mkdir(parents=True, exist_ok=True)
    master_file.write_text(content, encoding="utf-8")


def _name_list(repo_dir: Path) -> list[str]:
    name_list = []

    for rule in read_masters(repo_dir).rule_list:
        name_list.append(rule.name)

    return name_list


def _rule_named(repo_dir: Path, name: str) -> Rule:
    for rule in read_masters(repo_dir).rule_list:
        if rule.name == name:
            return rule

    raise AssertionError(f"no rule named {name}")
