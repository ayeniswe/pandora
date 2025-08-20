import logging
import subprocess
from enum import Enum

from requests import get

from pandora.errors import Error
from pandora.platforms.base import Arch, LinuxDistro, OSType, PlatformInfo

logger = logging.getLogger(__name__)


class IDE(Enum):
    VSCode = 0


def setup(info: PlatformInfo, selection: IDE):
    match selection:
        case IDE.VSCode:
            return _install_vscode(info)


def _build_vscode_download_url(info: PlatformInfo):
    match (info.os, info.subtype, info.arch):
        case (OSType.WINDOWS, None, Arch.X86_64):
            platform = "win32-x64-user"
        case (OSType.WINDOWS, None, Arch.ARM64):
            platform = "win32-arm64-user"
        case (OSType.WINDOWS, None, Arch.X86):
            platform = "win32-user"
        case (OSType.LINUX, None, Arch.X86_64):
            platform = "linux-x64"
        case (OSType.LINUX, None, Arch.ARM64):
            platform = "linux-arm64"
        case (OSType.LINUX, None, Arch.ARMHF):
            platform = "linux-armhf"
        case (OSType.LINUX, LinuxDistro.UBUNTU, Arch.X86_64):
            platform = "linux-deb-x64"
        case (OSType.LINUX, LinuxDistro.UBUNTU, Arch.ARM64):
            platform = "linux-deb-arm64"
        case (OSType.LINUX, LinuxDistro.UBUNTU, Arch.ARMHF):
            platform = "linux-deb-armhf"
        case (
            (OSType.LINUX, LinuxDistro.CENTOS, Arch.X86_64)
            | (OSType.LINUX, LinuxDistro.RHEL, Arch.X86_64)
        ):
            platform = "linux-rpm-x64"
        case (
            (OSType.LINUX, LinuxDistro.CENTOS, Arch.ARM64)
            | (OSType.LINUX, LinuxDistro.RHEL, Arch.ARM64)
        ):
            platform = "linux-rpm-arm64"
        case (
            (OSType.LINUX, LinuxDistro.CENTOS, Arch.ARMHF)
            | (OSType.LINUX, LinuxDistro.RHEL, Arch.ARMHF)
        ):
            platform = "linux-rpm-armhf"
        case (OSType.MAC, None, Arch.X86_64):
            platform = "darwin-x64"
        case (OSType.MAC, None, Arch.ARM64):
            platform = "darwin-arm64"
        case _:
            raise Error.PlatformUnsupported(info)

    build = "stable"
    version = "latest"
    url = f"https://update.code.visualstudio.com/{version}/{platform}/{build}"

    return url


def _install_vscode(info: PlatformInfo):
    try:
        url = _build_vscode_download_url(info)

        pkg = "vscode"
        if "deb" in url:
            pkg += ".deb"
        elif "rpm" in url:
            pkg += ".rpm"
        elif "win32" in url:
            pkg += ".exe"
        elif "darwin" in url:
            pkg += ".zip"

        logger.debug(f"Downloading VSCode package to {pkg}")
        with open(pkg, "wb") as f:
            response = get(url, verify=False)
            f.write(response.content)
            logger.debug(f"Download complete, size: {len(response.content)} bytes")

        logger.info("Installing VSCode")
        match (info.os, info.subtype):
            case (OSType.WINDOWS, None):
                try:
                    logger.debug("Running Windows installer")
                    subprocess.run(
                        [pkg, "/VERYSILENT", "NORESTART", "MERGETASKS=!runcode"],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                except subprocess.CalledProcessError:
                    logger.error("Windows installation failed")
                    raise
            case (OSType.LINUX, LinuxDistro.UBUNTU):
                try:
                    logger.debug("Running Ubuntu installer (dpkg)")

                    subprocess.run(["dpkg", "-i", pkg], check=True, capture_output=True, text=True)
                except subprocess.CalledProcessError:
                    logger.error("Ubuntu installation failed")
                    raise
            case (OSType.LINUX, LinuxDistro.RHEL) | (OSType.LINUX, LinuxDistro.CENTOS):
                try:
                    logger.debug("Running RHEL/CentOS installer (yum)")
                    subprocess.run(
                        ["yum", "install", "-y", pkg], check=True, capture_output=True, text=True
                    )
                except subprocess.CalledProcessError:
                    logger.error("RHEL/CentOS installation failed")
                    raise
            case _:
                # Unreachable case
                logger.error("Reached supposedly unreachable case in VSCode installer")
                return

        logger.info("VSCode installation completed successfully")

    except Exception as e:
        logger.exception(f"Error during VSCode installation: {e}")
        raise