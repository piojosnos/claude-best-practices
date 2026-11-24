# --------------------------------------------------------------------------------
# The typed model: what the reader returns and what the renderer produces
# --------------------------------------------------------------------------------

from dataclasses import dataclass
from pathlib import Path


# --------------------------------------------------------------------------------
# Masters
# --------------------------------------------------------------------------------

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


# --------------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------------

@dataclass(frozen=True)
class OutputFile:
    content: bytes
    executable: bool


# --------------------------------------------------------------------------------
# File mode
# --------------------------------------------------------------------------------

_OWNER_EXEC_BIT = 0o100


def is_executable(path: Path) -> bool:
    return bool(path.stat().st_mode & _OWNER_EXEC_BIT)
