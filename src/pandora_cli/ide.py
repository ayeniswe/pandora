from typing import List, Set

from pandora.common import Status
from pandora.task.ide.builder import IDESelection
from pandora.task.ide import builder
from pandora.platforms.base import detect_platform


def full_setup(
    selection: IDESelection,
    extensions: List[str],
    workloads: Set[str] = set(),
) -> Status:
    """
    Set up and install the selected IDE with optional extensions and workloads.
    """
    info = detect_platform()
    status = builder.setup(info, selection, workloads)
    if status and extensions:
        status = builder.add_extensions(selection, extensions)
    return status
