from typing import List, Set

from pandora.common import Status
from pandora.online import ide
from pandora.platforms.base import detect_platform


def setup(
    selection: ide.IDE,
    extensions: List[str],
    workloads: Set[str] = set(),
) -> Status:
    """
    Set up and install the selected IDE with optional extensions and workloads.
    """
    info = detect_platform()
    status = ide.setup(info, selection, workloads)
    if status and extensions:
        status = ide.add_extensions(selection, extensions)
    return status
