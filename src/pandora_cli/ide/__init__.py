from pathlib import Path

from rich.console import Console
from pandora.online import ide
from pandora.platforms.base import detect_platform


def setup(
    selection: str,
    verbose: bool,
    console: Console,
) -> None:
    """Apply environment variables from a file."""
    info = detect_platform()
    ide.setup(info,sele)
