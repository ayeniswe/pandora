"""Top-level package for pandora.

Provides offline and online modules with strong typing support.
"""

from __future__ import annotations

import logging
import sys

from . import errors, offline, online, platforms

__all__ = ["offline", "online", "platforms", "errors"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
