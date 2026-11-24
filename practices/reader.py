# --------------------------------------------------------------------------------
# The reader: every master on disk to the typed model
# --------------------------------------------------------------------------------
# Rules and skills each have their own reader; this module joins them.
# --------------------------------------------------------------------------------

from pathlib import Path

from practices.model import Masters
from practices.rule_reader import read_rule_list
from practices.skill_reader import read_skill_list


# --------------------------------------------------------------------------------
# Reading the masters
# --------------------------------------------------------------------------------

def read_masters(repo_dir: Path) -> Masters:
    return Masters(read_rule_list(repo_dir), read_skill_list(repo_dir))
