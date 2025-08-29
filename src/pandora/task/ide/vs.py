import logging
import os
import subprocess
from typing import List, Set

from requests import get

from pandora.common import Status
from pandora.errors import Error, ErrorMessage
from pandora.platforms.base import Arch, OSType, PlatformInfo
from pandora.task.ide.base import IDE
from pandora.utils.osa import (
    activate,
    click_button,
    down,
    osa_return,
    spacebar,
    tab,
    tab_back_to_window,
    wait_for_element,
)

logger = logging.getLogger(__name__)


class VS(IDE):

    def __init__(self, info: PlatformInfo, workloads: Set[str] = set()):
        super().__init__()
        self.info = info
        self.workloads = workloads

    def setup(self):
        match self.info.os:
            case OSType.MAC:
                return (self._install_vscommunity()
                        if not os.path.isdir("/Applications/Visual Studio.app")
                        else Status.Success)
            case OSType.WINDOWS:
                return (self._install_vscommunity()
                        if not subprocess.check_output(
                            [
                                "vswhere", "-products", "Community",
                                "-property", "installationPath"
                            ],
                            text=True,
                        ).strip() else Status.Success)
            case _:
                raise Error.PlatformUnsupported(self.info)

    def _build_vscommunity_download_url(self):
        match (self.info.os, self.info.subtype, self.info.arch):
            case OSType.WINDOWS, None, Arch.X86_64:
                return "https://aka.ms/vs/17/release/vs_community.exe"
            case OSType.WINDOWS, None, Arch.X86:
                # Last latest build (2019)
                return "https://aka.ms/vs/16/release/vs_community.exe"
            case (OSType.MAC, None, Arch.X86_64) | (OSType.MAC, None,
                                                    Arch.ARM64):
                return "https://aka.ms/vs/mac/download"
            case _:
                raise Error.PlatformUnsupported(self.info)

    def _install_vscommunity(self):
        try:
            url = self._build_vscommunity_download_url()

            pkg = "vscommunity"
            if "mac" in url:
                pkg += ".dmg"
            else:
                pkg += ".exe"

            logger.debug(
                "Downloading Visual Studio Community Edition package to %s",
                pkg)
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
                                pkg,
                                "--quiet",
                                "--wait",
                                "--norestart",
                                "--nocache",
                                "--add",
                                "Microsoft.VisualStudio.Workload.CoreEditor",
                            ],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                    except subprocess.CalledProcessError:
                        logger.error("Windows installation failed")
                        raise
                case (OSType.MAC, None):
                    try:
                        logger.debug("Mounting macOS installer")
                        subprocess.run(
                            ["hdiutil", "attach", pkg],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        logger.debug("Copying Visual Studio to Applications")
                        subprocess.run(
                            [
                                "cp",
                                "-r",
                                "/Volumes/Visual Studio for Mac Installer/Install Visual Studio "
                                "for Mac"
                                ".app",
                                "/Applications/Install Visual Studio for Mac.app",
                            ],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        logger.debug("Detaching installer image")
                        subprocess.run(
                            [
                                "hdiutil",
                                "detach",
                                "/Volumes/Visual Studio for Mac Installer",
                            ],
                            check=True,
                            capture_output=True,
                            text=True,
                        )
                        logger.debug(
                            "Launching Visual Studio installer to complete installation"
                        )
                        subprocess.run(
                            [
                                "open",
                                "/Applications/Install Visual Studio for Mac.app",
                            ],
                            check=True,
                            capture_output=True,
                            text=True,
                        )

                        logger.debug(
                            "Automating Visual Studio for Mac Installer via AppleScript"
                        )
                        # Wait for the installer window to fully appear
                        APP_NAME = "Visual Studio for Mac Installer"
                        if not wait_for_element(
                                f'window "{APP_NAME}" of process "{APP_NAME}"',
                                timeout=120):
                            logger.error(
                                "Timed out waiting for installer window")
                            raise Error.InstallFailure(
                                "Visual Studio Community (macOS)")
                        # Select window
                        activate(APP_NAME)
                        # Wait for Terms to be visible
                        wait_for_element(
                            f'sheet 1 of window "{APP_NAME}" of process "{APP_NAME}"'
                        )
                        # Accept Terms
                        osa_return()
                        # Select options
                        self._auto_ui_selection(
                            dotnet_app="dotnet_app" in self.workloads,
                            dotnet_wasm="dotnet_wasm" in self.workloads,
                            tvos="tvos" in self.workloads,
                            native_cocoa="native_cocoa" in self.workloads,
                            android="android" in self.workloads,
                            ios="ios" in self.workloads,
                            xamarin_cocoa="xamarin_cocoa" in self.workloads,
                        )
                        # Wait until the Install button is visible
                        if not wait_for_element(
                                f'button "Install" of window "{APP_NAME}" of process "{APP_NAME}"',
                                timeout=180):
                            logger.error(
                                "Timed out waiting for Install button")
                            raise Error.InstallFailure(
                                "Visual Studio Community (macOS)")
                        # Start installing
                        click_button("Install", APP_NAME)
                        # Do not autostart app
                        tab()
                        tab()
                        spacebar()
                        # Wait until the installation finishes
                        if not wait_for_element(
                                f'button "Done" of window "{APP_NAME}" of process "{APP_NAME}"',
                                timeout=1800):
                            logger.error("Timed out waiting for Done button")
                            raise Error.InstallFailure(
                                "Visual Studio Community (macOS)")
                        # Close installer
                        click_button("Done", APP_NAME)

                    except subprocess.CalledProcessError:
                        logger.error("MacOS installation failed")
                        raise
                case _:
                    # [UNREACHABLE_CASE]
                    ...

        except (subprocess.CalledProcessError, ErrorMessage) as e:
            logger.exception(
                "Error during Visual Studio Community Edition installation: %s",
                e)
            raise Error.InstallFailure("Visual Studio Community")

        return Status.Success

    @staticmethod
    def _auto_ui_selection(dotnet_app: bool = False,
                           dotnet_wasm: bool = False,
                           tvos: bool = False,
                           native_cocoa: bool = False,
                           android: bool = False,
                           ios: bool = False,
                           xamarin_cocoa: bool = False):
        tab_to_new_window = False
        """
        Automates selection of spacebares in the Visual Studio for Mac Installer UI.

        Parameters:
            dotnet_app (bool): Whether to select the .NET Multi-platform App UI option.
            dotnet_wasm (bool): Whether to select the .NET WebAssembly build tools option.
            tvos (bool): Whether to select the tvOS option.
            native_cocoa (bool): Whether to select the macOS (Cocoa for native apps) option.
            android (bool): Whether to select the Android option.
            ios (bool): Whether to select the iOS option.
            xamarin_cocoa (bool): Whether to select the macOS (Cocoa for apps w/ Xamarin SDK) option
            .
        """
        # Start at ".Net Multi-platform App UI" option
        tab_back_to_window()

        # Select .Net Multi-platform App UI? (include Android and iOS option)
        down()
        if dotnet_app:
            spacebar()
            tab_to_new_window = True

        # Select .Net WebAssembly build tools?
        down()
        if dotnet_wasm:
            spacebar()

        # Select tvOS?
        down()
        if tvos:
            spacebar()

        # Select macOS (Cocoa for native apps)?
        down()
        if native_cocoa:
            spacebar()

        # Select Android?
        down()
        if android and not dotnet_app:
            spacebar()
        else:
            tab_to_new_window = True

        # Select iOS?
        down()
        if ios and not dotnet_app:
            if tab_to_new_window:
                tab_back_to_window()
                tab_to_new_window = False
                spacebar()
        else:
            tab_to_new_window = True

        # Select macOS (Cocoa for apps w/ Xamarin SDK)?
        down()
        if xamarin_cocoa:
            if tab_to_new_window:
                tab_back_to_window()
                spacebar()

    # TODO
    @staticmethod
    def add_extensions(exts: List[str]) -> Status:
        raise NotImplementedError
