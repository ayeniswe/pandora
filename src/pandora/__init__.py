"""Top-level package for pandora.

Provides offline and online modules with strong typing support.
"""

from __future__ import annotations

from . import offline, online, platforms, errors

__all__ = ["offline", "online", "platforms", "errors"]
