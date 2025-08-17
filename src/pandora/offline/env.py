"""Cross-platform environment setup such as: variables setting, etc."""
# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportAttributeAccessIssue=false
from pathlib import Path

from pandora.common import WRITE_TAG
from pandora.errors import Error
from pandora.platforms.base import LinuxDistro, OSType, PlatformInfo


def config_reader(path: str | Path):
    """
    Read a simple KEY=VALUE config file into a dictionary.

    Args:
        path: Path to the env file.

    Returns:
        dict mapping keys to values.
    """
    env_vars: dict[str, str] = {}
    path = Path(path).expanduser()

    if not path.exists():
        return Error.ConfigNotFound(path)

    with path.open() as f:
        for line in f:
            line = line.strip()
            # Skip comments and EOF
            if not line or line.startswith("#") or line.startswith("//"):
                continue
            # Skip incorrect AST
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            env_vars[key.strip()] = val.strip()
    return env_vars


def setup_vars(info: PlatformInfo, data: dict[str, str]):
    """Persist environment variables for the current user.

    Args:
        info: Detected platform information.
        data: Mapping of environment variables to apply.

    On Linux, variables are appended to the user’s shell startup config (e.g. ~/.bashrc).

    On Windows, variables are written to the user environment registry.
    """
    match info.os:
        case OSType.WINDOWS:
            return _setup_windows_vars(data)
        case OSType.LINUX:
            match info.subtype:
                case LinuxDistro.UBUNTU | LinuxDistro.CENTOS:
                    return _setup_linux_vars(data, "~/.bashrc")
                case _:
                    return Error.PlatformUnsupported(info)
        case _:
            return Error.PlatformUnsupported(info)


def _setup_windows_vars(data: dict[str, str]):
    import winreg
    
    key_handle = winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, r"Environment", access=winreg.KEY_SET_VALUE
    )

    for k, v in data.items():
        winreg.SetValueEx(key_handle, k, 0, winreg.REG_SZ, v)
        
    winreg.CloseKey(key_handle)

def _setup_linux_vars(data: dict[str, str], config: str):
    import os

    with open(os.path.expanduser(config), "a") as f:
        f.write(WRITE_TAG + "\n")
        for k, v in data.items():
            f.write(f"\nexport {k}={v}")
