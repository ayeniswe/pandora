from abc import ABC, abstractmethod
from enum import Enum
import logging
from typing import List

from pandora.common import Status

logger = logging.getLogger(__name__)

class IDE(ABC):

    @abstractmethod
    def setup(self) -> Status:
        ...

    @staticmethod
    @abstractmethod
    def add_extensions(exts: List[str]) -> Status:
        ...


class IDESelection(Enum):
    VSCODE = 0
    VS = 1
    INTELLIJ = 2
