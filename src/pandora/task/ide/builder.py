import logging
from typing import List, Set

from pandora.platforms.base import PlatformInfo
from pandora.task.ide.base import IDESelection
from pandora.task.ide.vs import VS
from pandora.task.ide.vscode import VSCode

logger = logging.getLogger(__name__)


def setup(info: PlatformInfo, selection: IDESelection, workloads: Set[str] = set()):
    match selection:
        case IDESelection.VSCODE:
            return VSCode(info).setup()
        case IDESelection.VS:
            return VS(info, workloads).setup()
        # TODO
        case IDESelection.INTELLIJ:
            raise NotImplementedError


def add_extensions(selection: IDESelection, exts: List[str]):
    match selection:
        case IDESelection.VSCODE:
            return VSCode.add_extensions(exts)
        case IDESelection.VS:
            return VS.add_extensions(exts)
        # TODO
        case IDESelection.INTELLIJ:
            raise NotImplementedError
