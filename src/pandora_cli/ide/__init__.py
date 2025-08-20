from typing import List

from pandora.common import Status
from pandora.online import ide
from pandora.platforms.base import detect_platform


def setup(
    selection: ide.IDE,
    extensions: List[str],
) -> Status:
    """
    Set up and install the selected IDE with optional extensions.
    """
    info = detect_platform()
    status = ide.setup(info, selection)
    if status and extensions:
        status = ide.add_extensions(selection, extensions)
    return status
