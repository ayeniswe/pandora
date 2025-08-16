
from pandora.platforms.base import OSType, PlatformInfo, LinuxDistro
from pandora.errors import Error

def setup_vars(info: PlatformInfo, data: dict[str, str]):
    match info.os:
        case OSType.WINDOWS:
            _setup_windows_vars(data)
        case OSType.LINUX:
            match info.subtype:
                case LinuxDistro.UBUNTU | LinuxDistro.CENTOS:
                    _setup_linux_vars(data, "~/.bashrc")
                case _:
                    return Error.PlatformUnsupported(info)
        case _:
             return Error.PlatformUnsupported(info)

def _setup_windows_vars(data: dict[str, str]):
    def set_env_var(key: str, value: str, expand: bool = False):
        import winreg
        key_handle = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            access=winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(
            key_handle, 
            key, 
            0, 
            winreg.REG_EXPAND_SZ if expand else winreg.REG_SZ, 
            value
        )
        winreg.CloseKey(key_handle) 

    for (k,v) in data.items():
        set_env_var(k,v)

def _setup_linux_vars(data: dict[str, str], config: str):
    import os
    with open(os.path.expanduser(config), "a") as f:
        for (k,v) in data.items():
            f.write(f"\nexport {k}={v}\n")