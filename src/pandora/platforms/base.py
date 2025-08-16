"""Typed platform and architecture detection."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import platform
from typing import Optional


class OSType(str, Enum):
    """Supported operating system families."""

    LINUX = "linux"
    WINDOWS = "windows"
    MAC = "mac"
    BSD = "bsd"
    OTHER = "other"


class LinuxDistro(str, Enum):
    """Linux distributions we care about first."""

    UBUNTU = "ubuntu"
    CENTOS = "centos"
    OTHER = "other"


class Arch(str, Enum):
    """Common CPU architectures."""

    X86_64 = "x86_64"
    X86 = "x86"
    ARM64 = "arm64"
    OTHER = "other"


@dataclass(frozen=True)
class PlatformInfo:
    """Information about the current runtime platform."""

    os: OSType
    arch: Arch
    subtype: Optional[str] = None


def _detect_arch() -> Arch:
    machine = platform.machine().lower()
    if machine in {"x86_64", "amd64"}:
        return Arch.X86_64
    if machine in {"x86", "i386", "i686"}:
        return Arch.X86
    if machine in {"arm64", "aarch64"}:
        return Arch.ARM64
    return Arch.OTHER


def detect_platform() -> PlatformInfo:
    """Detect the host platform and architecture."""

    system = platform.system().lower()
    arch = _detect_arch()

    if system == "linux":
        os_type = OSType.LINUX
        subtype: Optional[str]
        try:
            import distro  # type: ignore[import-not-found]

            name = distro.id().lower()
            if name == "ubuntu":
                subtype = LinuxDistro.UBUNTU.value
            elif name == "centos":
                subtype = LinuxDistro.CENTOS.value
            else:
                subtype = LinuxDistro.OTHER.value
        except Exception:
            subtype = None
        return PlatformInfo(os_type, arch, subtype)

    if system == "windows":
        return PlatformInfo(OSType.WINDOWS, arch)
    if system == "darwin":
        return PlatformInfo(OSType.MAC, arch)
    if system.endswith("bsd"):
        return PlatformInfo(OSType.BSD, arch)
    return PlatformInfo(OSType.OTHER, arch)
