"""Tests for IDE installation utilities."""
# pyright: reportPrivateUsage=false

import os
import subprocess
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from pandora.common import Status
from pandora.errors import Error, ErrorMessage
from pandora.online.ide import (
    IDE,
    add_extensions,
    setup,
    _build_vscommunity_download_url,
    _build_vscode_download_url,
    _install_vscommunity,
    _install_vscode,
    _install_vscode_extensions,
)
from pandora.platforms.base import Arch, LinuxDistro, OSType, PlatformInfo


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
    with pytest.raises(ErrorMessage, match="Unsupported platform: OS: Mac ARCH: Arch.OTHER"):
        _build_vscode_download_url(PlatformInfo(OSType.MAC, Arch.OTHER, None))


@pytest.mark.parametrize(
    "info, expected_url",
    [
        (PlatformInfo(OSType.WINDOWS, Arch.X86_64, None), "https://aka.ms/vs/17/release/vs_community.exe"),
        (PlatformInfo(OSType.WINDOWS, Arch.X86, None), "https://aka.ms/vs/16/release/vs_community.exe"),
        (PlatformInfo(OSType.MAC, Arch.X86_64, None), "https://aka.ms/vs/mac/download"),
        (PlatformInfo(OSType.MAC, Arch.ARM64, None), "https://aka.ms/vs/mac/download"),
    ],
)
def test_build_vscommunity_download_url_supported(info: PlatformInfo, expected_url: str) -> None:
    assert _build_vscommunity_download_url(info) == expected_url


def test_build_vscommunity_download_url_unsupported() -> None:
    with pytest.raises(ErrorMessage):
        _build_vscommunity_download_url(PlatformInfo(OSType.LINUX, Arch.X86_64, None))


def test_setup_vscode_calls_install(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("pandora.online.ide.is_package_installed", lambda _: False)
    called = {}

    def fake_install(info: PlatformInfo) -> Status:
        called["invoked"] = True
        return Status.Success

    monkeypatch.setattr("pandora.online.ide._install_vscode", fake_install)
    status = setup(PlatformInfo(OSType.WINDOWS, Arch.X86_64, None), IDE.VSCODE)
    assert called["invoked"] and status == Status.Success


def test_setup_vs_mac_calls_install(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(os.path, "isdir", lambda _: False)
    called = {}

    def fake_install(info: PlatformInfo) -> Status:
        called["invoked"] = True
        return Status.Success

    monkeypatch.setattr("pandora.online.ide._install_vscommunity", fake_install)
    status = setup(PlatformInfo(OSType.MAC, Arch.X86_64, None), IDE.VS)
    assert called["invoked"] and status == Status.Success


def test_setup_vs_unsupported() -> None:
    with pytest.raises(ErrorMessage):
        setup(PlatformInfo(OSType.LINUX, Arch.X86_64, None), IDE.VS)


def test_setup_intellij_returns_failure() -> None:
    status = setup(PlatformInfo(OSType.WINDOWS, Arch.X86_64, None), IDE.INTELLIJ)
    assert status == Status.Failure


def test_add_extensions_vscode(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {}

    def fake_install(exts: list[str]) -> Status:
        called["exts"] = exts
        return Status.Success

    monkeypatch.setattr("pandora.online.ide._install_vscode_extensions", fake_install)
    status = add_extensions(IDE.VSCODE, ["ext1"])
    assert called["exts"] == ["ext1"] and status == Status.Success


def test_add_extensions_other_returns_none() -> None:
    assert add_extensions(IDE.VS, []) is None
    assert add_extensions(IDE.INTELLIJ, []) is None


def test_install_vscode_extensions_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    def fake_run(cmd, check, capture_output, text):
        calls.append(cmd)
        return types.SimpleNamespace(stdout="")

    monkeypatch.setattr("pandora.online.ide.subprocess.run", fake_run)
    status = _install_vscode_extensions(["ext1", "", "ext2"])
    assert status == Status.Success
    assert calls == [
        ["code", "--install-extension", "ext1"],
        ["code", "--install-extension", "ext2"],
    ]


def test_install_vscode_extensions_error_output(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd, check, capture_output, text):
        return types.SimpleNamespace(stdout="Error: something")

    monkeypatch.setattr("pandora.online.ide.subprocess.run", fake_run)
    with pytest.raises(ErrorMessage):
        _install_vscode_extensions(["ext"])


def test_install_vscode_extensions_subprocess_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(cmd, check, capture_output, text):
        raise subprocess.CalledProcessError(1, cmd)

    monkeypatch.setattr("pandora.online.ide.subprocess.run", fake_run)
    status = _install_vscode_extensions(["ext"])
    assert status == Status.Failure


def test_install_vscode_mac(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    info = PlatformInfo(OSType.MAC, Arch.X86_64, None)
    calls = []

    def fake_run(cmd, check, capture_output, text):
        calls.append(cmd)
        return types.SimpleNamespace(stdout="")

    monkeypatch.setattr("pandora.online.ide.subprocess.run", fake_run)
    monkeypatch.setattr(
        "pandora.online.ide.get", lambda url, verify, timeout: types.SimpleNamespace(content=b"data")
    )
    monkeypatch.chdir(tmp_path)
    status = _install_vscode(info)
    assert status == Status.Success
    assert ["unzip", "vscode.zip", "-d", "/Applications"] in calls


def test_install_vscommunity_mac(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    info = PlatformInfo(OSType.MAC, Arch.X86_64, None)
    calls = []

    def fake_run(cmd, check, capture_output, text):
        calls.append(cmd)
        return types.SimpleNamespace(stdout="")

    monkeypatch.setattr("pandora.online.ide.subprocess.run", fake_run)
    monkeypatch.setattr(
        "pandora.online.ide.get", lambda url, verify, timeout: types.SimpleNamespace(content=b"data")
    )
    monkeypatch.chdir(tmp_path)
    status = _install_vscommunity(info)
    assert status == Status.Success
    assert calls[0] == ["hdiutil", "attach", "vscommunity.dmg"]
    assert calls[1] == [
        "cp",
        "-r",
        "/Volumes/Visual Studio/Visual Studio.app",
        "/Applications/Visual Studio.app",
    ]
    assert calls[2] == ["hdiutil", "detach", "/Volumes/Visual Studio"]
