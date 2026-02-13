"""Application configuration and settings management."""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional


def _default_hotkey() -> set[str]:
    return {"ctrl", "alt", "space"}


@dataclass
class AppConfig:
    """Stores all user-configurable settings."""

    # Hotkey
    hotkey: set[str] = field(default_factory=_default_hotkey)

    # Whisper model
    model_name: str = "small.en"

    # Recording
    sample_rate: int = 16000
    channels: int = 1
    recording_mode: str = "toggle"  # "toggle" or "push_to_talk"
    audio_device: Optional[int] = None  # None = system default

    # Text injection
    paste_delay: float = 0.15

    # Formatting
    formatting_mode: str = "cleaned"  # "raw" or "cleaned"

    # Feedback
    play_sounds: bool = True
    show_notifications: bool = True

    # Startup
    start_on_boot: bool = False

    # Internal
    _settings_dir: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        if not self._settings_dir:
            appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
            self._settings_dir = os.path.join(appdata, "Speech2Txt")
        os.makedirs(self._settings_dir, exist_ok=True)

    @property
    def settings_file(self) -> str:
        return os.path.join(self._settings_dir, "settings.json")

    def save(self) -> None:
        """Persist settings to disk."""
        data = asdict(self)
        data.pop("_settings_dir", None)
        # Convert set to list for JSON serialization
        data["hotkey"] = sorted(list(data["hotkey"]))
        with open(self.settings_file, "w") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        """Load settings from disk if they exist."""
        if not os.path.exists(self.settings_file):
            return
        try:
            with open(self.settings_file, "r") as f:
                data = json.load(f)
            if "hotkey" in data:
                data["hotkey"] = set(data["hotkey"])
            for key, value in data.items():
                if hasattr(self, key) and not key.startswith("_"):
                    setattr(self, key, value)
        except (json.JSONDecodeError, OSError):
            pass  # Use defaults if settings file is corrupted
