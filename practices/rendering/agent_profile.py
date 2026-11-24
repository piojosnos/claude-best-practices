# --------------------------------------------------------------------------------
# The agent profile: where and how each agent receives the generated files
# --------------------------------------------------------------------------------
# The rule and skill folders are the folders of the agent's config directory, so
# generated/<agent>/rules/ and generated/<agent>/skills/ mirror it.
# --------------------------------------------------------------------------------

from dataclasses import dataclass


# --------------------------------------------------------------------------------
# Profiles
# --------------------------------------------------------------------------------

@dataclass(frozen=True)
class AgentProfile:
    name: str
    rule_folder: str
    rule_extension: str
    rule_template: str
    skill_folder: str
    skill_template: str


CLAUDE_PROFILE = AgentProfile(
    name="claude",
    rule_folder="rules",
    rule_extension=".md",
    rule_template="claude/rule.md.j2",
    skill_folder="skills",
    skill_template="claude/skill.md.j2",
)
CURSOR_PROFILE = AgentProfile(
    name="cursor",
    rule_folder="rules",
    rule_extension=".mdc",
    rule_template="cursor/rule.mdc.j2",
    skill_folder="skills",
    skill_template="cursor/skill.md.j2",
)
AGENT_PROFILE_LIST = [CLAUDE_PROFILE, CURSOR_PROFILE]
