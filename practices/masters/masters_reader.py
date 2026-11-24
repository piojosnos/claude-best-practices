# --------------------------------------------------------------------------------
# The masters reader: every master on disk to the typed model
# --------------------------------------------------------------------------------
# Rules and skills each have their own reader; this module joins them.
# --------------------------------------------------------------------------------

from pathlib import Path

from practices.masters.masters_model import Masters
from practices.masters.rule_reader import read_rule_list
from practices.masters.skill_reader import read_skill_list


# --------------------------------------------------------------------------------
# Reading the masters
# --------------------------------------------------------------------------------

def read_masters(repo_dir: Path) -> Masters:
    return Masters(read_rule_list(repo_dir), read_skill_list(repo_dir))
