"""Text injection into the active window via pynput keyboard typing."""

import ctypes
import time

import pyautogui
from pynput.keyboard import Controller


# Disable pyautogui's fail-safe (moving mouse to corner aborts)
# since this runs as a background service
pyautogui.FAILSAFE = False

_keyboard = Controller()
_user32 = ctypes.windll.user32


def get_foreground_window() -> int:
    """Get the handle of the currently focused window."""
    return _user32.GetForegroundWindow()


def restore_focus(hwnd: int) -> bool:
    """Bring a window back to the foreground. Returns True on success."""
    if not hwnd or not _user32.IsWindow(hwnd):
        return False
    if _user32.GetForegroundWindow() == hwnd:
        return True

    # Attach our thread's input to the foreground window's thread.
    # This lifts the SetForegroundWindow restriction without injecting
    # any phantom keystrokes into the input stream.
    kernel32 = ctypes.windll.kernel32
    our_thread = kernel32.GetCurrentThreadId()
    fg_thread = _user32.GetWindowThreadProcessId(
        _user32.GetForegroundWindow(), None
    )

    attached = False
    if our_thread != fg_thread:
        attached = bool(_user32.AttachThreadInput(our_thread, fg_thread, True))

    _user32.SetForegroundWindow(hwnd)

    if attached:
        _user32.AttachThreadInput(our_thread, fg_thread, False)

    time.sleep(0.05)
    return _user32.GetForegroundWindow() == hwnd


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
