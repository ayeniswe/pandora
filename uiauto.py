import subprocess


def osa(script: str) -> str:
    """Run AppleScript and return stdout (stripped)."""
    out = subprocess.check_output(["osascript", "-e", script])
    return out.decode("utf-8").strip()


def activate_app(window_name: str) -> None:
    osa(f'tell application "{window_name}" to activate')


def invoke_event(e: str, delay_amt: float = 0) -> None:
    # Add delay in seconds
    delay = "" if delay_amt == 0 else f"delay {delay_amt}"
    osa(f'''
        tell application "System Events"
        {e}
        {delay}
        end tell
    ''')


def move_down() -> None:
    # Down Arrow
    invoke_event("key code 125")


def checkbox() -> None:
    # Space
    invoke_event("key code 49")


def tab() -> None:
    # Tab key
    invoke_event("key code 48")


def click_button(name: str, window_name: str):
    invoke_event(
        f'click button "{name}" of window "{window_name}" of process "{window_name}"'
    )


def select_default() -> None:
    # Return
    invoke_event("keystroke return")


def tab_back_to_window() -> None:
    """
    Due to quirks in the installer's UI, this function repeatedly tabs
    back into the group box containing the checkboxes before selections can be made.
    """
    for _ in range(0, 4):
        tab()


def auto_ui_selection(dotnet_app: bool = False,
                      dotnet_wasm: bool = False,
                      tvos: bool = False,
                      native_cocoa: bool = False,
                      android: bool = False,
                      ios: bool = False,
                      xamarin_cocoa: bool = False):
    tab_to_new_window = False
    """
    Automates selection of checkboxes in the Visual Studio for Mac Installer UI.

    Parameters:
        dotnet_app (bool): Whether to select the .NET Multi-platform App UI option.
        dotnet_wasm (bool): Whether to select the .NET WebAssembly build tools option.
        tvos (bool): Whether to select the tvOS option.
        native_cocoa (bool): Whether to select the macOS (Cocoa for native apps) option.
        android (bool): Whether to select the Android option.
        ios (bool): Whether to select the iOS option.
        xamarin_cocoa (bool): Whether to select the macOS (Cocoa for apps w/ Xamarin SDK) option.
    """
    # Start at ".Net Multi-platform App UI" option
    tab_back_to_window()

    # Select .Net Multi-platform App UI? (include Android and iOS option)
    move_down()
    if dotnet_app:
        checkbox()
        tab_to_new_window = True

    # Select .Net WebAssembly build tools?
    move_down()
    if dotnet_wasm:
        checkbox()

    # Select tvOS?
    move_down()
    if tvos:
        checkbox()

    # Select macOS (Cocoa for native apps)?
    move_down()
    if native_cocoa:
        checkbox()

    # Select Android?
    move_down()
    if android and not dotnet_app:
        checkbox()
    else:
        tab_to_new_window = True

    # Select iOS?
    move_down()
    if ios and not dotnet_app:
        if tab_to_new_window:
            tab_back_to_window()
            tab_to_new_window = False
            checkbox()
    else:
        tab_to_new_window = True

    # Select macOS (Cocoa for apps w/ Xamarin SDK)?
    move_down()
    if xamarin_cocoa:
        if tab_to_new_window:
            tab_back_to_window()
            checkbox()


if __name__ == "__main__":
    APP_NAME = "Visual Studio for Mac Installer"
    # Select window
    activate_app(APP_NAME)
    # Accept Terms
    select_default()
    # Select options
    auto_ui_selection(True)
    # Start installing
    click_button("Install", APP_NAME)
    # Do not autostart app
    tab()
    tab()
    checkbox()

