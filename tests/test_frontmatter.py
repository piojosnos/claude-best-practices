# --------------------------------------------------------------------------------
# Frontmatter: the split of a master's text and the strict YAML block
# --------------------------------------------------------------------------------

import pytest

from practices.errors import PracticesError
from practices.frontmatter import split_frontmatter


BROKEN_FRONTMATTER_LIST = [
    (
        "---\npaths: [unclosed\n---\n\n# X1\n\nText x1.\n",
        "the frontmatter is not valid YAML",
    ),
    (
        "---\nfoo: 2026-13-45\n---\n\n# X1\n\nText x1.\n",
        "the frontmatter is not valid YAML",
    ),
    (
        '---\npaths:\n  - "**/*.x1"\npaths:\n  - "**/*.x2"\n---\n\n# X1\n\nText x1.\n',
        "the frontmatter repeats the key 'paths'",
    ),
    (
        "---\n- a1\n---\n\n# X1\n\nText x1.\n",
        "the frontmatter must be a mapping of keys",
    ),
    (
        '---\npaths:\n  - "**/*.x1"\n\n# X1\n\nText x1.\n',
        "the frontmatter has no closing --- line",
    ),
    (
        "---\nname: x1\ndescription: d1\ndescription: d2\n---\n\n# X1\n\nText x1.\n",
        "the frontmatter repeats the key 'description'",
    ),
]


# --------------------------------------------------------------------------------
# Splitting
# --------------------------------------------------------------------------------

def test_split_frontmatter_returns_the_map_and_the_body() -> None:
    assert split_frontmatter("---\nk1: v1\n---\n\n# X1\n", "m1.md") == ({"k1": "v1"}, "\n# X1\n")


# --------------------------------------------------------------------------------

def test_a_text_without_frontmatter_is_all_body() -> None:
    assert split_frontmatter("# X1\n\nText x1.\n", "m1.md") == ({}, "# X1\n\nText x1.\n")


# --------------------------------------------------------------------------------
# Rejections
# --------------------------------------------------------------------------------

@pytest.mark.parametrize("text, message", BROKEN_FRONTMATTER_LIST)
def test_split_frontmatter_rejects_a_broken_block(text: str, message: str) -> None:
    with pytest.raises(PracticesError) as raised:
        split_frontmatter(text, "m1.md")

    assert str(raised.value) == f"m1.md: {message}"
