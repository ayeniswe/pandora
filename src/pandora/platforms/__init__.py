"""Platform detection utilities."""

from __future__ import annotations

from .base import Arch, LinuxDistro, OSType, PlatformInfo, detect_platform

__all__ = [
    "Arch",
    "OSType",
    "LinuxDistro",
    "PlatformInfo",
    "detect_platform",
]
