from enum import Enum

from requests import get

from pandora.errors import Error
from pandora.platforms.base import Arch, LinuxDistro, OSType, PlatformInfo


class IDE(Enum):
    VSCode = 0


def setup(info: PlatformInfo, selection: IDE):
    match selection:
        case IDE.VSCode:
            return _setup_vscode(info)


def _build_vscode_download_url(info: PlatformInfo):
    platform_map: dict[tuple[OSType, None | LinuxDistro, Arch], str] = {
        (OSType.WINDOWS, None, Arch.X86_64): "win32-x64-user",
        (OSType.WINDOWS, None, Arch.ARM64): "win32-arm64-user",
        (OSType.WINDOWS, None, Arch.X86): "win32-user",
        (OSType.LINUX, None, Arch.X86_64): "linux-x64",
        (OSType.LINUX, None, Arch.ARM64): "linux-arm64",
        (OSType.LINUX, None, Arch.ARMHF): "linux-armhf",
        (OSType.LINUX, LinuxDistro.UBUNTU, Arch.X86_64): "linux-deb-x64",
        (OSType.LINUX, LinuxDistro.UBUNTU, Arch.ARM64): "linux-deb-arm64",
        (OSType.LINUX, LinuxDistro.UBUNTU, Arch.ARMHF): "linux-deb-armhf",
        (OSType.LINUX, LinuxDistro.CENTOS, Arch.X86_64): "linux-rpm-x64",
        (OSType.LINUX, LinuxDistro.CENTOS, Arch.ARM64): "linux-rpm-arm64",
        (OSType.LINUX, LinuxDistro.CENTOS, Arch.ARMHF): "linux-rpm-armhf",
        (OSType.LINUX, LinuxDistro.RHEL, Arch.X86_64): "linux-rpm-x64",
        (OSType.LINUX, LinuxDistro.RHEL, Arch.ARM64): "linux-rpm-arm64",
        (OSType.LINUX, LinuxDistro.RHEL, Arch.ARMHF): "linux-rpm-armhf",
        (OSType.MAC, None, Arch.X86_64): "darwin-x64",
        (OSType.MAC, None, Arch.ARM64): "darwin-arm64",
    }

    platform = platform_map.get((info.os, info.subtype, info.arch))
    if not platform:
        raise Error.PlatformUnsupported(info)

    build = "stable"
    version = "latest"
    url = f"https://update.code.visualstudio.com/{version}/{platform}/{build}"

    return url


def _setup_vscode(info: PlatformInfo):
    url = _build_vscode_download_url(info)
    resp = get(url)  # pyright: ignore[reportUnusedVariable] # noqa: F841
