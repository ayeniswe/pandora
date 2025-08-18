"""Typed platform and architecture detection."""

from __future__ import annotations

import platform
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OSType(str, Enum):
    """Supported operating system families."""

    LINUX = "linux"
    WINDOWS = "windows"
    MAC = "mac"
    OTHER = "other"


class LinuxDistro(str, Enum):
    """Linux distributions ids"""

    UBUNTU = "ubuntu"
    CENTOS = "centos"
    RHEL = "rhel"


class Arch(str, Enum):
    """Common CPU architectures."""

    X86_64 = "x86_64"
    X86 = "x86"
    ARM64 = "arm64"
    ARMHF = "armhf"
    OTHER = "other"


@dataclass(frozen=True)
class PlatformInfo:
    """Information about the current runtime platform."""

    os: OSType
    arch: Arch
    subtype: Optional[LinuxDistro] = None

    def __str__(self) -> str:
        if self.os == OSType.LINUX:
            return (
                f"OS: {self.os.capitalize()} "
                f"Distro: {self.subtype if self.subtype else 'other'} "
                f"ARCH: {self.arch.upper()}"
            )
        return f"OS: {self.os.capitalize()} " f"ARCH: {self.arch}"


def _detect_arch() -> Arch:
    machine = platform.machine().lower()
    match machine:
        case "x86_64" | "amd64":
            return Arch.X86_64
        case "x86" | "i386" | "i686":
            return Arch.X86
        case "arm64" | "aarch64":
            return Arch.ARM64
        case "armhf":
            return Arch.ARMHF
        case _:
            return Arch.OTHER


def detect_platform() -> PlatformInfo:
    """Detect the host platform and architecture."""

    system = platform.system().lower()
    arch = _detect_arch()

    if system == "linux":
        os_type = OSType.LINUX
        subtype: Optional[LinuxDistro]

        import distro

        name = distro.id().lower()
        if name == "ubuntu":
            subtype = LinuxDistro.UBUNTU
        elif name == "centos":
            subtype = LinuxDistro.CENTOS
        elif name == "rhel":
            subtype = LinuxDistro.RHEL
        else:
            subtype = None

        return PlatformInfo(os_type, arch, subtype)

    if system == "windows":
        return PlatformInfo(OSType.WINDOWS, arch)
    if system == "darwin":
        return PlatformInfo(OSType.MAC, arch)
    return PlatformInfo(OSType.OTHER, arch)
