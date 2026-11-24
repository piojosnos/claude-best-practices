# --------------------------------------------------------------------------------
# Agent profiles: where and how each agent receives the generated rules
# --------------------------------------------------------------------------------
# The rule folder is the rules folder of the agent's config directory, so
# generated/<agent>/rules/ mirrors it.
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


CLAUDE_PROFILE = AgentProfile("claude", "rules", ".md", "claude/rule.md.j2")
CURSOR_PROFILE = AgentProfile("cursor", "rules", ".mdc", "cursor/rule.mdc.j2")
AGENT_PROFILE_LIST = [CLAUDE_PROFILE, CURSOR_PROFILE]
