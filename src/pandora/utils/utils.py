import logging
import shutil

logger = logging.getLogger(__name__)


def is_package_installed(package: str):
    """
    Determines if a system package or executable is installed.
    Supports Windows and Linux.

    Args:
        package (str): The name of the executable or package.

    Returns:
        bool: True if installed, False otherwise.
    """
    # Check if executable is in PATH
    if shutil.which(package):
        return True
    return False
