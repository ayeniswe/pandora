"""Tests for environment variable configuration utilities."""
# pyright: reportPrivateUsage=false

import sys
from pathlib import Path

import pytest
from pandora.errors import ErrorMessage
from pandora.online.ide import _build_vscode_download_url
from pandora.platforms.base import Arch, LinuxDistro, OSType, PlatformInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


@pytest.mark.parametrize(
    "info, expected_platform",
    [
        # Windows
        (PlatformInfo(OSType.WINDOWS, Arch.X86_64, None), "win32-x64-user"),
        (PlatformInfo(OSType.WINDOWS, Arch.ARM64, None), "win32-arm64-user"),
        (PlatformInfo(OSType.WINDOWS, Arch.X86, None), "win32-user"),
        # macOS (chip-targeted)
        (PlatformInfo(OSType.MAC, Arch.X86_64, None), "darwin-x64"),
        (PlatformInfo(OSType.MAC, Arch.ARM64, None), "darwin-arm64"),
        # Linux generic (no subtype)
        (PlatformInfo(OSType.LINUX, Arch.X86_64, None), "linux-x64"),
        (PlatformInfo(OSType.LINUX, Arch.ARM64, None), "linux-arm64"),
        (PlatformInfo(OSType.LINUX, Arch.ARMHF, None), "linux-armhf"),
        # Linux Debian/Ubuntu (.deb)
        (PlatformInfo(OSType.LINUX, Arch.X86_64, LinuxDistro.UBUNTU), "linux-deb-x64"),
        (PlatformInfo(OSType.LINUX, Arch.ARM64, LinuxDistro.UBUNTU), "linux-deb-arm64"),
        (PlatformInfo(OSType.LINUX, Arch.ARMHF, LinuxDistro.UBUNTU), "linux-deb-armhf"),
        # Linux (CENTOS) RPM families (.rpm)
        (PlatformInfo(OSType.LINUX, Arch.X86_64, LinuxDistro.CENTOS), "linux-rpm-x64"),
        (PlatformInfo(OSType.LINUX, Arch.ARM64, LinuxDistro.CENTOS), "linux-rpm-arm64"),
        (PlatformInfo(OSType.LINUX, Arch.ARMHF, LinuxDistro.CENTOS), "linux-rpm-armhf"),
        # Linux (RHEL) RPM families (.rpm)
        (PlatformInfo(OSType.LINUX, Arch.X86_64, LinuxDistro.RHEL), "linux-rpm-x64"),
        (PlatformInfo(OSType.LINUX, Arch.ARM64, LinuxDistro.RHEL), "linux-rpm-arm64"),
        (PlatformInfo(OSType.LINUX, Arch.ARMHF, LinuxDistro.RHEL), "linux-rpm-armhf"),
    ],
)
def test_build_vscode_download_url_supported(info: PlatformInfo, expected_platform: str):
    url = _build_vscode_download_url(info)
    assert url == f"https://update.code.visualstudio.com/latest/{expected_platform}/stable"


def test_build_vscode_download_url_unsupported():
    with pytest.raises(ErrorMessage, match="Unsupported platform: OS: Mac ARCH: other"):
        _build_vscode_download_url(PlatformInfo(OSType.MAC, Arch.OTHER, None))
