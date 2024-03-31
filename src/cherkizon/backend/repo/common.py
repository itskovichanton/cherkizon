from dataclasses import dataclass
from enum import Enum
from typing import Any


class RepoAction(Enum):
    INSERTED = 1
    UPDATED = 2
    DELETED = 3


@dataclass
class RepoActionResult:
    action: RepoAction
    entity: Any
