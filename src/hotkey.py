"""Global hotkey detection using pynput."""

import threading
from typing import Callable, Optional

from pynput import keyboard

from config import AppConfig


class HotkeyListener:
    """Listens for a global hotkey combination and fires callbacks."""

    def __init__(
        self,
        config: AppConfig,
        on_toggle: Callable[[], None],
        on_press: Optional[Callable[[], None]] = None,
        on_release: Optional[Callable[[], None]] = None,
    ) -> None:
        self.config = config
        self._on_toggle = on_toggle
        self._on_press = on_press
        self._on_release = on_release
        self._pressed_keys: set[str] = set()
        self._listener: Optional[keyboard.Listener] = None
        self._hotkey_active = False
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start listening for hotkeys in a background thread."""
        self._listener = keyboard.Listener(
            on_press=self._handle_press,
            on_release=self._handle_release,
        )
        self._listener.daemon = True
        self._listener.start()
        print(f"Hotkey listener started: {'+'.join(sorted(self.config.hotkey))}")

    def stop(self) -> None:
        """Stop the hotkey listener."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None

    def _key_to_str(self, key: keyboard.Key | keyboard.KeyCode) -> Optional[str]:
        """Normalize a pynput key to a lowercase string."""
        if isinstance(key, keyboard.Key):
            name = key.name  # e.g. 'ctrl_l', 'alt_l', 'space'
            # Normalize left/right modifiers
            for prefix in ("ctrl", "alt", "shift", "cmd"):
                if name.startswith(prefix):
                    return prefix
            return name
        elif isinstance(key, keyboard.KeyCode):
            if key.char:
                return key.char.lower()
            if key.vk:
                # Handle special virtual keys
                return str(key.vk)
        return None

    def _handle_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        name = self._key_to_str(key)
        if name is None:
            return

        with self._lock:
            self._pressed_keys.add(name)
            if self._pressed_keys >= self.config.hotkey:
                if self.config.recording_mode == "push_to_talk":
                    if not self._hotkey_active and self._on_press:
                        self._hotkey_active = True
                        self._on_press()
                else:
                    # Toggle mode: fire on press, debounced
                    if not self._hotkey_active:
                        self._hotkey_active = True
                        self._on_toggle()

    def _handle_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        name = self._key_to_str(key)
        if name is None:
            return

        with self._lock:
            self._pressed_keys.discard(name)
            if self._hotkey_active:
                if self.config.recording_mode == "push_to_talk":
                    if self._on_release:
                        self._hotkey_active = False
                        self._on_release()
                else:
                    # Toggle mode: reset hotkey_active so next press fires
                    self._hotkey_active = False
