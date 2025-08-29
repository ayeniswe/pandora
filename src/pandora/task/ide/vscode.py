import logging
import subprocess
from typing import List

from requests import get

from pandora.common import Status
from pandora.errors import Error, ErrorMessage
from pandora.platforms.base import Arch, LinuxDistro, OSType, PlatformInfo
from pandora.task.ide.base import IDE
from pandora.utils.utils import is_package_installed

logger = logging.getLogger(__name__)


class VSCode(IDE):
    def __init__(self, info: PlatformInfo):
        super().__init__()
        self.info = info

    def setup(self):
        return self._install_vscode(
        ) if not is_package_installed("code") else Status.Success

    @staticmethod
    def add_extensions(exts: List[str]):
        logger.debug("Installing Visual Studio Code extensions")
        try:
            for ext in exts:
                # Ignore empty extension ids
                if not ext:
                    continue
                # NOTE will fail on MAC OS unless grab cli as well when
                #  installing
                out = subprocess.run(["code", "--install-extension", ext],
                                     check=True,
                                     capture_output=True,
                                     text=True)
                # No exit-code so missing or error anywhere
                # in output signals something went wrong
                if "not found" in out.stdout or "Error" in out.stdout:
                    logger.error(
                        "Visual Studio Code extension '%s' installation failed:\n%s",
                        ext, out.stdout)
                    raise Error.InstallFailure(f"vscode-extension({ext})")
        except subprocess.CalledProcessError:
            logger.error("Visual Studio Code extensions installation failed")
            return Status.Failure

        return Status.Success

    def _build_vscode_download_url(self):
        match (self.info.os, self.info.subtype, self.info.arch):
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
            case ((OSType.LINUX, LinuxDistro.CENTOS, Arch.X86_64)
                  | (
                      OSType.LINUX,
                      LinuxDistro.RHEL,
                      Arch.X86_64,
                  )):
                platform = "linux-rpm-x64"
            case ((OSType.LINUX, LinuxDistro.CENTOS, Arch.ARM64)
                  | (
                      OSType.LINUX,
                      LinuxDistro.RHEL,
                      Arch.ARM64,
                  )):
                platform = "linux-rpm-arm64"
            case ((OSType.LINUX, LinuxDistro.CENTOS, Arch.ARMHF)
                  | (
                      OSType.LINUX,
                      LinuxDistro.RHEL,
                      Arch.ARMHF,
                  )):
                platform = "linux-rpm-armhf"
            case (OSType.MAC, None, Arch.X86_64):
                platform = "darwin-x64"
            case (OSType.MAC, None, Arch.ARM64):
                platform = "darwin-arm64"
            case _:
                raise Error.PlatformUnsupported(self.info)

        build = "stable"
        version = "latest"
        url = f"https://update.code.visualstudio.com/{version}/{platform}/{build}"

        return url

    def _install_vscode(self):
        try:
            url = self._build_vscode_download_url()

            pkg = "vscode"
            if "deb" in url:
                pkg += ".deb"
            elif "rpm" in url:
                pkg += ".rpm"
            elif "win32" in url:
                pkg += ".exe"
            elif "darwin" in url:
                pkg += ".zip"

            logger.debug("Downloading Visual Studio Code package to %s", pkg)
            with open(pkg, "wb") as f:
                response = get(url, verify=False, timeout=30)
                f.write(response.content)
                logger.debug("Download complete, size: %s bytes",
                             len(response.content))

            match (self.info.os, self.info.subtype):
                case (OSType.WINDOWS, None):
                    try:
                        logger.debug("Running Windows installer")
                        subprocess.run(
                            [
                                pkg, "/VERYSILENT", "NORESTART",
                                "MERGETASKS=!runcode"
                            ],
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

                        subprocess.run(["dpkg", "-i", pkg],
                                       check=True,
                                       capture_output=True,
                                       text=True)
                    except subprocess.CalledProcessError:
                        logger.error("Ubuntu installation failed")
                        raise
                case (OSType.LINUX, LinuxDistro.RHEL) | (OSType.LINUX,
                                                         LinuxDistro.CENTOS):
                    try:
                        logger.debug("Running RHEL/CentOS installer (yum)")
                        subprocess.run(["yum", "install", "-y", pkg],
                                       check=True,
                                       capture_output=True,
                                       text=True)
                    except subprocess.CalledProcessError:
                        logger.error("RHEL/CentOS installation failed")
                        raise
                case (OSType.MAC, None):
                    try:
                        logger.debug("Running macOS installer (unzip)")
                        subprocess.run(
                            ["unzip", pkg, "-d", "/Applications"],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                    except subprocess.CalledProcessError:
                        logger.error("MacOS installation failed")
                        raise
                case _:
                    # [UNREACHABLE_CASE]
                    ...

        except (subprocess.CalledProcessError, ErrorMessage) as e:
            logger.exception(
                "Error during Visual Studio Code installation: %s", e)
            raise Error.InstallFailure("Visual Studio Code")

        return Status.Success
