# --------------------------------------------------------------------------------
# Frontmatter: the YAML block at the top of a master, read strictly
# --------------------------------------------------------------------------------
# A repeated key or an unknown key stops the run with a message naming the master.
# --------------------------------------------------------------------------------

from collections.abc import Hashable

import yaml

from practices.errors import PracticesError


# --------------------------------------------------------------------------------
# Constants
# --------------------------------------------------------------------------------

_FRONTMATTER_FENCE = "---"


# --------------------------------------------------------------------------------
# Splitting and checking
# --------------------------------------------------------------------------------

def split_frontmatter(text: str, master_path: str) -> tuple[dict, str]:
    line_list = text.split("\n")

    if line_list[0].rstrip() != _FRONTMATTER_FENCE:
        return {}, text

    for index in range(1, len(line_list)):
        if line_list[index].rstrip() == _FRONTMATTER_FENCE:
            block = "\n".join(line_list[1:index])
            body = "\n".join(line_list[index + 1:])

            return _parse_block(block, master_path), body

    raise PracticesError(f"{master_path}: the frontmatter has no closing {_FRONTMATTER_FENCE} line")


# --------------------------------------------------------------------------------

def _parse_block(block: str, master_path: str) -> dict:
    try:
        parsed_value = yaml.load(block, Loader=_UniqueKeyLoader)
    except _DuplicateKeyError as e:
        raise PracticesError(f"{master_path}: the frontmatter repeats the key {e.key!r}") from e
    except (yaml.YAMLError, ValueError) as e:
        raise PracticesError(f"{master_path}: the frontmatter is not valid YAML") from e

    if parsed_value is None:
        return {}

    if not isinstance(parsed_value, dict):
        raise PracticesError(f"{master_path}: the frontmatter must be a mapping of keys")

    return parsed_value


# --------------------------------------------------------------------------------

def check_keys(frontmatter_map: dict, master_path: str, allowed_key_set: set[str], kind: str) -> None:
    for key in sorted(frontmatter_map, key=str):
        if key not in allowed_key_set:
            allowed_text = ", ".join(sorted(allowed_key_set))

            raise PracticesError(
                f"{master_path}: unknown frontmatter key '{key}'; a {kind} allows only: {allowed_text}"
            )


# --------------------------------------------------------------------------------
# The strict YAML loader
# --------------------------------------------------------------------------------

class _DuplicateKeyError(yaml.YAMLError):
    def __init__(self, key: object) -> None:
        super().__init__(key)
        self.key = key


# --------------------------------------------------------------------------------

class _UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict:
        seen_key_set = set()

        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)

            if not isinstance(key, Hashable):
                continue

            if key in seen_key_set:
                raise _DuplicateKeyError(key)

            seen_key_set.add(key)

        return super().construct_mapping(node, deep=deep)
