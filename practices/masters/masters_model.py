# --------------------------------------------------------------------------------
# The masters model: the typed rules and skills the readers return
# --------------------------------------------------------------------------------

from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    name: str
    master_path: str
    path_list: list[str]
    body: str


# --------------------------------------------------------------------------------

@dataclass(frozen=True)
class ExtraFile:
    path: str
    content: bytes
    executable: bool


# --------------------------------------------------------------------------------

@dataclass(frozen=True)
class Skill:
    name: str
    master_path: str
    description: str
    body: str
    extra_file_list: list[ExtraFile]
    disable_model_invocation: bool | None = None


# --------------------------------------------------------------------------------

@dataclass(frozen=True)
class Masters:
    rule_list: list[Rule]
    skill_list: list[Skill]
