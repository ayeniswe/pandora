"""Tests for environment variable configuration utilities."""
# pyright: reportPrivateUsage=false
# ruff: noqa: E402

import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from pandora.common import WRITE_TAG
from pandora.errors import ErrorMessage
from pandora.offline.env import (
    _setup_linux_vars,
    _setup_windows_vars,
    config_reader,
)


def test_config_reader_parses_key_values(tmp_path: Path) -> None:
    env_file = tmp_path / "test.env"
    env_file.write_text(
        """# comment
FOO=bar
BAZ=qux
INVALID
"""
    )
    result = config_reader(env_file)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_config_reader_missing_file_returns_error(tmp_path: Path) -> None:
    missing = tmp_path / "missing.env"
    result = config_reader(missing)
    assert isinstance(result, ErrorMessage)
    assert "config file not found" in result.msg


def test_setup_linux_vars_writes_exports(tmp_path: Path) -> None:
    bashrc = tmp_path / "bashrc"
    data = {"FOO": "bar", "BAZ": "qux"}
    _setup_linux_vars(data, str(bashrc))
    expected = WRITE_TAG + "\n\n" + "\n".join(f"export {k}={v}" for k, v in data.items())
    assert bashrc.read_text() == expected


def test_setup_windows_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[object, ...]] = []

    # Fake winreg with realistic signatures & constants
    def OpenKey(root: int, subkey: str, reserved: int = 0, access: int = 0) -> str:
        calls.append(("OpenKey", root, subkey, reserved, access))
        return "handle"

    def SetValueEx(handle: str, name: str, reserved: int, typ: int, value: str) -> None:
        calls.append(("SetValueEx", handle, name, reserved, typ, value))

    def CloseKey(handle: str) -> None:
        calls.append(("CloseKey", handle))

    mock_winreg = types.SimpleNamespace(
        HKEY_CURRENT_USER=0x80000001,
        KEY_SET_VALUE=0x0002,
        REG_SZ=1,
        OpenKey=OpenKey,
        SetValueEx=SetValueEx,
        CloseKey=CloseKey,
    )

    # Patch the module's reference to winreg
    monkeypatch.setitem(sys.modules, "winreg", mock_winreg)

    _setup_windows_vars({"FOO": "bar", "BIN": r"C:\bin"})

    assert calls == [
        ("OpenKey", 0x80000001, r"Environment", 0, 0x0002),
        ("SetValueEx", "handle", "FOO", 0, 1, "bar"),
        ("SetValueEx", "handle", "BIN", 0, 1, r"C:\bin"),
        ("CloseKey", "handle"),
    ]
