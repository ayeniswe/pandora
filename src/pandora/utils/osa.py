import logging
import subprocess

logger = logging.getLogger(__name__)

def osa(script: str) -> str:
    """
    Run AppleScript code using osascript and return the standard output as a stripped string.

    Parameters:
        script (str): The AppleScript code to execute.

    Returns:
        str: The stripped standard output of the script.
    """
    out = subprocess.check_output(["osascript", "-e", script], text=True)
    return out.strip()


def activate(window_name: str) -> None:
    """
    Activate (bring to foreground) the application with the given window name.

    Parameters:
        window_name (str): The name of the application window to activate.
    """
    osa(f'tell application "{window_name}" to activate')


def invoke_event(e: str, delay_amt: float = 0) -> None:
    """
    Invoke a macOS System Events AppleScript event, optionally adding a delay.

    Parameters:
        e (str): The AppleScript event to trigger.
        delay_amt (float): Optional delay in seconds after the event (default: 0).
    """
    delay = "" if delay_amt == 0 else f"delay {delay_amt}"
    osa(f'''
        tell application "System Events"
        {e}
        {delay}
        end tell
    ''')


def down() -> None:
    """
    Simulate pressing the Down Arrow key using System Events.
    """
    invoke_event("key code 125")


def spacebar() -> None:
    """
    Simulate pressing the Space key, typically used to toggle a checkbox.
    """
    invoke_event("key code 49")


def tab() -> None:
    """
    Simulate pressing the Tab key using System Events.
    """
    invoke_event("key code 48")


def click_button(name: str, window_name: str):
    """
    Simulate clicking a button in a specific window of an application using System Events.

    Parameters:
        name (str): The name of the button to click.
        window_name (str): The name of the window containing the button.
    """
    invoke_event(
        f'click button "{name}" of window "{window_name}" of process "{window_name}"'
    )


def osa_return() -> None:
    """
    Simulate pressing the Return key, typically used to select the default button.
    """
    invoke_event("keystroke return")


def tab_back_to_window() -> None:
    """
    Repeatedly press the Tab key to focus back into the group box containing checkboxes.
    This is used to work around UI quirks in some installers.
    """
    for _ in range(0, 4):
        tab()


def wait_for_element(element_query: str, timeout: int = 60) -> bool:
    """
    Wait for a UI element to appear in the macOS Accessibility tree.

    Parameters:
        element_query (str): The AppleScript exists() query for the UI element, e.g.
                             window "Foo" of process "Foo"
        timeout (int): Maximum number of seconds to wait.

    Returns:
        bool: True if the element appeared before timeout, False otherwise.
    """
    script = f'''
    tell application "System Events"
        set endTime to (current date) + {timeout}
        repeat until (exists ({element_query})) or ((current date) > endTime)
            delay 1
        end repeat
        if (exists ({element_query})) then
            return "FOUND"
        else
            return "TIMEOUT"
        end if
    end tell
    '''
    return osa(script) == "FOUND"