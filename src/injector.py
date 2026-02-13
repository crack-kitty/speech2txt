"""Text injection into the active window via clipboard paste."""

import time

import pyautogui
import pyperclip


# Disable pyautogui's fail-safe (moving mouse to corner aborts)
# since this runs as a background service
pyautogui.FAILSAFE = False


def inject_text(text: str, paste_delay: float = 0.06) -> None:
    """Paste text into the currently focused application via Ctrl+V.

    Saves the clipboard, sets it to our text, simulates Ctrl+V,
    waits, then restores the original clipboard.
    """
    if not text:
        return

    old_clipboard = ""
    try:
        old_clipboard = pyperclip.paste()
    except Exception:
        pass  # Clipboard might be empty or contain non-text

    pyperclip.copy(text)
    time.sleep(0.02)  # Let clipboard settle before pasting
    pyautogui.hotkey("ctrl", "v")
    time.sleep(paste_delay)

    # Restore original clipboard
    try:
        pyperclip.copy(old_clipboard)
    except Exception:
        pass


def send_key(key: str) -> None:
    """Send a single keystroke (e.g. 'enter', 'backspace', 'tab')."""
    pyautogui.press(key)


def send_hotkey(*keys: str) -> None:
    """Send a hotkey combination (e.g. 'ctrl', 'z')."""
    pyautogui.hotkey(*keys)


def send_backspaces(count: int) -> None:
    """Send multiple backspace keystrokes to delete characters."""
    for _ in range(count):
        pyautogui.press("backspace")
        time.sleep(0.005)
