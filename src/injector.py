"""Text injection into the active window via pynput keyboard typing."""

import time

import pyautogui
from pynput.keyboard import Controller


# Disable pyautogui's fail-safe (moving mouse to corner aborts)
# since this runs as a background service
pyautogui.FAILSAFE = False

_keyboard = Controller()


def inject_text(text: str) -> None:
    """Type text into the currently focused application.

    Uses pynput's keyboard controller to type Unicode text directly.
    Bypasses the clipboard entirely.
    """
    if not text:
        return

    # Strip newlines — Whisper sometimes adds them on pauses, and pynput
    # would send them as Enter keystrokes (which submits in chat apps).
    # Intentional newlines come from voice commands ("new line"), not here.
    clean = text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    _keyboard.type(clean)


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
