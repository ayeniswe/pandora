# pyright: reportPrivateUsage=false
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownArgumentType=false

import pytest

from pandora.platforms.base import OSType, LinuxDistro, Arch, PlatformInfo
from pandora.errors import Error, ErrorMessage
from pandora.task.ide.vscode import VSCode
import builtins
from unittest.mock import Mock, call, mock_open

from pandora.common import Status
from pandora.errors import ErrorMessage
from pandora.platforms.base import Arch, LinuxDistro, OSType, PlatformInfo
from pandora.task.ide.vscode import VSCode

from typing import Any, Optional, List


@pytest.fixture
def dummy_bytes() -> bytes:
    return b"\x00\x01\x02dummy-zip-or-exe-or-deb-or-rpm"


def _patch_download(monkeypatch: pytest.MonkeyPatch,
                    dummy_bytes: bytes,
                    url: str = "https://example.com/file") -> Mock:
    """Patch the module-level `get` imported in vscode.py and return the spy."""
    fake_resp = Mock()
    fake_resp.content = dummy_bytes
    get_spy = Mock(return_value=fake_resp)
    monkeypatch.setattr("pandora.task.ide.vscode.get", get_spy)
    return get_spy


def _patch_file_write(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Patch builtins.open to a mock that supports .write assertions."""
    m = mock_open()
    monkeypatch.setattr(builtins, "open", m)
    return m


def _patch_subprocess_success(monkeypatch: pytest.MonkeyPatch) -> Mock:
    """Patch subprocess.run to a success stub."""
    run_spy = Mock()
    monkeypatch.setattr("pandora.task.ide.vscode.subprocess.run", run_spy)
    return run_spy


def _patch_subprocess_raising(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch subprocess.run to raise a CalledProcessError."""

    def _raise(*args, **kwargs: Any):
        from subprocess import CalledProcessError
        raise CalledProcessError(returncode=1, cmd=kwargs.get("args", args[0]))

    monkeypatch.setattr("pandora.task.ide.vscode.subprocess.run", _raise)


def _patch_url(monkeypatch: pytest.MonkeyPatch, url: str) -> None:
    """Force the platform URL used inside _install_vscode."""
    monkeypatch.setattr(VSCode, "_build_vscode_download_url",
                        Mock(return_value=url))


@pytest.mark.parametrize(
    "os_, subtype, arch, expected_platform",
    [
        # Windows (user installers)
        (OSType.WINDOWS, None, Arch.X86_64, "win32-x64-user"),
        (OSType.WINDOWS, None, Arch.ARM64, "win32-arm64-user"),
        (OSType.WINDOWS, None, Arch.X86, "win32-user"),

        # Generic Linux (no distro subtype)
        (OSType.LINUX, None, Arch.X86_64, "linux-x64"),
        (OSType.LINUX, None, Arch.ARM64, "linux-arm64"),
        (OSType.LINUX, None, Arch.ARMHF, "linux-armhf"),

        # Ubuntu (deb packages)
        (OSType.LINUX, LinuxDistro.UBUNTU, Arch.X86_64, "linux-deb-x64"),
        (OSType.LINUX, LinuxDistro.UBUNTU, Arch.ARM64, "linux-deb-arm64"),
        (OSType.LINUX, LinuxDistro.UBUNTU, Arch.ARMHF, "linux-deb-armhf"),

        # RHEL/CentOS (rpm packages)
        (OSType.LINUX, LinuxDistro.CENTOS, Arch.X86_64, "linux-rpm-x64"),
        (OSType.LINUX, LinuxDistro.RHEL, Arch.X86_64, "linux-rpm-x64"),
        (OSType.LINUX, LinuxDistro.CENTOS, Arch.ARM64, "linux-rpm-arm64"),
        (OSType.LINUX, LinuxDistro.RHEL, Arch.ARM64, "linux-rpm-arm64"),
        (OSType.LINUX, LinuxDistro.CENTOS, Arch.ARMHF, "linux-rpm-armhf"),
        (OSType.LINUX, LinuxDistro.RHEL, Arch.ARMHF, "linux-rpm-armhf"),

        # macOS (zip)
        (OSType.MAC, None, Arch.X86_64, "darwin-x64"),
        (OSType.MAC, None, Arch.ARM64, "darwin-arm64"),
    ],
)
def test_build_vscode_download_url_supported(os_: OSType,
                                             subtype: Optional[LinuxDistro],
                                             arch: Arch,
                                             expected_platform: str) -> None:
    """
    For every supported (OS, subtype, arch) combination, ensure the constructed
    URL matches the official VS Code update service format:
    https://update.code.visualstudio.com/{version}/{platform}/{build}
    where version='latest' and build='stable' for this function.
    """
    info = PlatformInfo(os=os_, subtype=subtype, arch=arch)
    url = VSCode(info)._build_vscode_download_url()

    # Structure and constants
    assert url.startswith(
        "https://update.code.visualstudio.com/"), "unexpected base URL"
    assert "/latest/" in url, "version must be 'latest'"
    assert url.endswith("/stable"), "build must be 'stable'"

    # Platform slug
    parts = url.split("/")
    # .../latest/{platform}/stable  -> index -2 is the platform slug
    platform_slug = parts[-2]
    assert platform_slug == expected_platform


def test_build_vscode_download_url_unsupported_raises() -> None:
    """
    An unsupported tuple should raise Error.PlatformUnsupported.
    Example: macOS with 32-bit x86 (not supported in the match).
    """
    info = PlatformInfo(os=OSType.MAC, subtype=None, arch=Arch.X86)
    with pytest.raises(ErrorMessage):
        VSCode(info)._build_vscode_download_url()


def test_install_windows_success(monkeypatch: pytest.MonkeyPatch,
                                 dummy_bytes: bytes) -> None:
    info = PlatformInfo(os=OSType.WINDOWS, subtype=None, arch=Arch.X86_64)
    sut = VSCode(info)

    # URL drives extension selection
    _patch_url(
        monkeypatch,
        "https://update.code.visualstudio.com/latest/win32-x64-user/stable")
    get_spy = _patch_download(monkeypatch, dummy_bytes)
    open_mock = _patch_file_write(monkeypatch)
    run_spy = _patch_subprocess_success(monkeypatch)

    result = sut._install_vscode()
    assert result == Status.Success

    # Download called with correct params
    get_spy.assert_called_once()
    called_url = get_spy.call_args.args[0]
    assert "win32-x64-user" in called_url
    assert get_spy.call_args.kwargs["verify"] is False
    assert get_spy.call_args.kwargs["timeout"] == 30

    # File written
    open_mock.assert_called_once_with("vscode.exe", "wb")
    handle = open_mock()
    handle.write.assert_called_once_with(dummy_bytes)

    # Installer invoked correctly
    assert run_spy.call_args == call(
        ["vscode.exe", "/VERYSILENT", "NORESTART", "MERGETASKS=!runcode"],
        check=True,
        capture_output=True,
        text=True)


@pytest.mark.parametrize(
    "subtype,url,expected_pkg,expected_cmd",
    [
        (
            LinuxDistro.UBUNTU,
            "https://update.code.visualstudio.com/latest/linux-deb-x64/stable",
            "vscode.deb",
            ["dpkg", "-i", "vscode.deb"],
        ),
        (
            LinuxDistro.RHEL,
            "https://update.code.visualstudio.com/latest/linux-rpm-x64/stable",
            "vscode.rpm",
            ["yum", "install", "-y", "vscode.rpm"],
        ),
        (
            LinuxDistro.CENTOS,
            "https://update.code.visualstudio.com/latest/linux-rpm-x64/stable",
            "vscode.rpm",
            ["yum", "install", "-y", "vscode.rpm"],
        ),
    ],
)
def test_install_linux_success(monkeypatch: pytest.MonkeyPatch,
                               dummy_bytes: bytes, subtype: LinuxDistro,
                               url: str, expected_pkg: str,
                               expected_cmd: List[str]) -> None:
    info = PlatformInfo(os=OSType.LINUX, subtype=subtype, arch=Arch.X86_64)
    sut = VSCode(info)

    _patch_url(monkeypatch, url)
    get_spy = _patch_download(monkeypatch, dummy_bytes)
    open_mock = _patch_file_write(monkeypatch)
    run_spy = _patch_subprocess_success(monkeypatch)

    result = sut._install_vscode()
    assert result == Status.Success

    # Download used
    get_spy.assert_called_once()
    assert get_spy.call_args.kwargs["verify"] is False
    assert get_spy.call_args.kwargs["timeout"] == 30

    # Correct package filename
    open_mock.assert_called_once_with(expected_pkg, "wb")
    open_mock().write.assert_called_once_with(dummy_bytes)

    # Correct installer command
    run_spy.assert_called_once_with(expected_cmd,
                                    check=True,
                                    capture_output=True,
                                    text=True)


def test_install_macos_success(monkeypatch: pytest.MonkeyPatch,
                               dummy_bytes: bytes) -> None:
    info = PlatformInfo(os=OSType.MAC, subtype=None, arch=Arch.X86_64)
    sut = VSCode(info)

    _patch_url(
        monkeypatch,
        "https://update.code.visualstudio.com/latest/darwin-x64/stable")
    get_spy = _patch_download(monkeypatch, dummy_bytes)
    open_mock = _patch_file_write(monkeypatch)
    run_spy = _patch_subprocess_success(monkeypatch)

    result = sut._install_vscode()
    assert result == Status.Success

    get_spy.assert_called_once()
    open_mock.assert_called_once_with("vscode.zip", "wb")
    open_mock().write.assert_called_once_with(dummy_bytes)
    run_spy.assert_called_once_with(
        ["unzip", "vscode.zip", "-d", "/Applications"],
        check=True,
        capture_output=True,
        text=True)


@pytest.mark.parametrize(
    "os_,subtype,url",
    [
        (OSType.WINDOWS, None,
         "https://update.code.visualstudio.com/latest/win32-x64-user/stable"),
        (OSType.LINUX, LinuxDistro.UBUNTU,
         "https://update.code.visualstudio.com/latest/linux-deb-x64/stable"),
        (OSType.LINUX, LinuxDistro.RHEL,
         "https://update.code.visualstudio.com/latest/linux-rpm-x64/stable"),
        (OSType.MAC, None,
         "https://update.code.visualstudio.com/latest/darwin-x64/stable"),
    ],
)
def test_install_subprocess_failure_raises_installfailure(
        monkeypatch: pytest.MonkeyPatch, dummy_bytes: bytes, os_: OSType,
        subtype: Optional[LinuxDistro], url: str) -> None:
    info = PlatformInfo(os=os_, subtype=subtype, arch=Arch.X86_64)
    sut = VSCode(info)

    _patch_url(monkeypatch, url)
    _patch_download(monkeypatch, dummy_bytes)
    _patch_file_write(monkeypatch)
    _patch_subprocess_raising(monkeypatch)

    with pytest.raises(ErrorMessage):
        sut._install_vscode()


def test_install_url_builder_error_raises_installfailure(
        monkeypatch: pytest.MonkeyPatch) -> None:
    info = PlatformInfo(os=OSType.MAC, subtype=None, arch=Arch.X86_64)
    sut = VSCode(info)

    # Simulate earlier stages throwing an ErrorMessage (caught by outer except)
    def _boom(*a, **kw):
        raise ErrorMessage("Bad platform")

    monkeypatch.setattr(VSCode, "_build_vscode_download_url", _boom)

    with pytest.raises(ErrorMessage):
        sut._install_vscode()
