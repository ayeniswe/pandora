"""Top-level package for pandora.

Provides offline and online modules with strong typing support.
"""

from __future__ import annotations

import logging
import sys

from . import errors, offline, platforms, task, utils

__all__ = ["offline","task", "platforms", "errors", "utils"]

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
