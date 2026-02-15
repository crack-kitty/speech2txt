"""Speech2Txt — system-wide dictation app entry point."""

import ctypes
import re
import sys
import os
import threading
import winsound

# Add src to path so modules can import each other
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import AppConfig
from recorder import AudioRecorder
from transcriber import Transcriber
from commands import VoiceCommandProcessor
from hotkey import HotkeyListener
from injector import get_foreground_window, restore_focus
from tray import TrayApp


class Speech2Txt:
    """Main application controller — wires all components together."""

    def __init__(self) -> None:
        self.config = AppConfig()
        self.config.load()

        self.recorder = AudioRecorder(self.config)
        self.transcriber = Transcriber(self.config)
        self.commands = VoiceCommandProcessor()

        self._recording = False
        self._lock = threading.Lock()
        self._settings_open = False

        self.hotkey = HotkeyListener(
            config=self.config,
            on_toggle=self._on_hotkey_toggle,
            on_press=self._on_hotkey_press,
            on_release=self._on_hotkey_release,
        )

        self.tray = TrayApp(
            on_quit=self._quit,
            on_settings=self._open_settings,
        )

    def run(self) -> None:
        """Start the app. Blocks on the tray event loop."""
        self.tray.run(setup_callback=self._on_tray_ready)

    def _on_tray_ready(self, icon: object) -> None:
        """Called once the tray icon is created."""
        # pystray Win32 backend requires explicitly making the icon visible
        icon.visible = True
        # Load model in background
        model_thread = threading.Thread(
            target=self._load_model, daemon=True
        )
        model_thread.start()

    def _load_model(self) -> None:
        """Load the Whisper model and start the hotkey listener."""
        self.transcriber.load_model()
        self.hotkey.start()
        self.tray.set_state("idle")
        print("Ready! Press Ctrl+Alt+Space to dictate.")

    # ── Toggle mode ──────────────────────────────────────────

    def _on_hotkey_toggle(self) -> None:
        """Toggle recording on/off (toggle mode)."""
        with self._lock:
            if self._recording:
                self._stop_and_transcribe()
            else:
                self._start_recording()

    # ── Push-to-talk mode ────────────────────────────────────

    def _on_hotkey_press(self) -> None:
        """Start recording (push-to-talk mode)."""
        with self._lock:
            if not self._recording:
                self._start_recording()

    def _on_hotkey_release(self) -> None:
        """Stop recording and transcribe (push-to-talk mode)."""
        with self._lock:
            if self._recording:
                self._stop_and_transcribe()

    # ── Recording helpers ────────────────────────────────────

    def _start_recording(self) -> None:
        """Start audio capture."""
        if not self.transcriber.is_ready:
            print("Model still loading, please wait...")
            return
        self._recording = True
        self.tray.set_state("recording")
        self._play_sound(1000, 100)  # High beep — start
        self.recorder.start()
        print("Recording...")

    def _stop_and_transcribe(self) -> None:
        """Stop recording and run transcription in a background thread."""
        self._recording = False
        audio_data = self.recorder.stop()
        target_hwnd = get_foreground_window()
        self.tray.set_state("processing")
        self._play_sound(600, 100)  # Low beep — stop

        threading.Thread(
            target=self._transcribe_and_inject,
            args=(audio_data, target_hwnd),
            daemon=True,
        ).start()

    def _transcribe_and_inject(self, audio_data, target_hwnd: int) -> None:
        """Transcribe audio and inject the result."""
        text = self.transcriber.transcribe(audio_data)
        if text:
            # Restore focus to the window that was active when recording stopped,
            # in case the user alt-tabbed during transcription.
            if not restore_focus(target_hwnd):
                print("Warning: could not restore focus to target window")
            result = self._post_process(text)
            control = self.commands.process(result)
            if control == "stop":
                print("Stop listening command received.")
                # Could pause hotkey listener here
        self.tray.set_state("idle")

    # Pattern matches spelled-out letters like "D-I-R" or "D.I.R." or "D. I. R."
    _SPELLED_RE = re.compile(
        r'\b([A-Za-z])(?:[.\-]\s*([A-Za-z])){1,}(?:\.|\b)'
    )

    @staticmethod
    def _collapse_spelled(match: re.Match) -> str:
        """Convert 'D-I-R' or 'D.I.R.' to 'dir'."""
        # Extract just the letters from the full match
        letters = re.findall(r'[A-Za-z]', match.group(0))
        return "".join(letters).lower()

    # Matches all-caps words of 2-5 letters that aren't common acronyms
    _ALLCAPS_RE = re.compile(r'\b([A-Z]{2,5})\b')
    _KEEP_UPPER = {"I", "OK", "US", "UK", "AI", "API", "URL", "HTTP", "HTML", "CSS", "SQL", "JSON", "XML", "PDF", "USB", "RAM", "CPU", "GPU", "SSD", "HDD", "DNS", "SSH", "FTP", "IDE"}

    def _lowercase_short_caps(self, match: re.Match) -> str:
        """Lowercase short all-caps words unless they're known acronyms."""
        word = match.group(1)
        if word in self._KEEP_UPPER:
            return word
        return word.lower()

    def _post_process(self, text: str) -> str:
        """Apply text formatting based on config."""
        if self.config.formatting_mode == "raw":
            return text

        # Collapse spelled-out letters: "D-I-R" -> "dir", "D. I. R." -> "dir"
        text = self._SPELLED_RE.sub(self._collapse_spelled, text)

        # Lowercase short all-caps words: "DIR" -> "dir", "PING" -> "ping"
        text = self._ALLCAPS_RE.sub(self._lowercase_short_caps, text)

        # Clean Whisper punctuation artifacts
        text = re.sub(r'([,?!;:])\.+', r'\1', text)  # period after other punct: ",." -> ","
        text = re.sub(r'\.([,?!;:])', r'\1', text)   # period before other punct: ".," -> ","
        text = re.sub(r'(?<!\.)\.{2}(?!\.)', '.', text)  # double period (not ellipsis ...)

        # Ensure first character is capitalized
        if text and text[0].islower():
            text = text[0].upper() + text[1:]

        return text

    def _play_sound(self, freq: int, duration: int) -> None:
        """Play a beep sound if enabled."""
        if self.config.play_sounds:
            threading.Thread(
                target=winsound.Beep,
                args=(freq, duration),
                daemon=True,
            ).start()

    def _open_settings(self) -> None:
        """Open the settings window (only one at a time)."""
        if self._settings_open:
            return
        self._settings_open = True
        # Import here to avoid circular import and tkinter overhead at startup
        from settings_ui import open_settings_window

        def _run_settings() -> None:
            try:
                open_settings_window(self.config, self._on_settings_changed)
            finally:
                self._settings_open = False

        threading.Thread(target=_run_settings, daemon=True).start()

    def _on_settings_changed(self) -> None:
        """Called when settings are saved from the UI."""
        print("Settings updated.")
        # Restart hotkey listener with new config
        self.hotkey.stop()
        self.hotkey = HotkeyListener(
            config=self.config,
            on_toggle=self._on_hotkey_toggle,
            on_press=self._on_hotkey_press,
            on_release=self._on_hotkey_release,
        )
        self.hotkey.start()

        # Reload model if it changed
        if self.config.model_name != self.transcriber.current_model_name:
            self.tray.set_state("disabled")
            self.transcriber = Transcriber(self.config)
            threading.Thread(
                target=self._load_model, daemon=True
            ).start()

    def _quit(self) -> None:
        """Clean shutdown."""
        print("Shutting down...")
        self.hotkey.stop()
        self.tray.stop()


_MUTEX_NAME = "Global\\Speech2Txt_SingleInstance"


def _acquire_single_instance() -> bool:
    """Try to acquire a named mutex. Returns False if already running."""
    # CreateMutexW returns a handle; GetLastError == 183 means it already exists
    handle = ctypes.windll.kernel32.CreateMutexW(None, True, _MUTEX_NAME)
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        ctypes.windll.kernel32.CloseHandle(handle)
        return False
    # Keep handle alive for the process lifetime (don't close it)
    return True


def main() -> None:
    if not _acquire_single_instance():
        print("Speech2Txt is already running!")
        ctypes.windll.user32.MessageBoxW(
            0,
            "Speech2Txt is already running.\nCheck your system tray.",
            "Speech2Txt",
            0x40,  # MB_ICONINFORMATION
        )
        sys.exit(1)

    app = Speech2Txt()
    app.run()


if __name__ == "__main__":
    main()
