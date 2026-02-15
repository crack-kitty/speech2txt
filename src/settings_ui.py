"""Settings window using tkinter."""

import os
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

import sounddevice as sd

from config import AppConfig


def _read_version() -> str:
    """Read version from VERSION file."""
    version_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "VERSION"
    )
    try:
        with open(version_file) as f:
            return f.read().strip()
    except OSError:
        return "unknown"


VERSION = _read_version()

WHISPER_MODELS = ["tiny.en", "base.en", "small.en", "medium.en"]
RECORDING_MODES = ["toggle", "push_to_talk"]
FORMATTING_MODES = ["cleaned", "raw"]


def open_settings_window(
    config: AppConfig,
    on_save: Optional[Callable[[], None]] = None,
) -> None:
    """Open a tkinter settings dialog. Blocks until closed."""
    root = tk.Tk()
    root.title("Speech2Txt Settings")
    root.geometry("550x500")
    root.resizable(False, False)

    # Make it look a bit nicer on Windows
    try:
        root.tk.call("tk", "scaling", 1.5)
    except Exception:
        pass

    frame = ttk.Frame(root, padding=20)
    frame.pack(fill="both", expand=True)

    row = 0

    # ── Hotkey ───────────────────────────────────────────────
    ttk.Label(frame, text="Hotkey:").grid(row=row, column=0, sticky="w", pady=5)
    hotkey_var = tk.StringVar(value="+".join(sorted(config.hotkey)))
    hotkey_entry = ttk.Entry(frame, textvariable=hotkey_var, width=30)
    hotkey_entry.grid(row=row, column=1, sticky="w", pady=5)
    row += 1

    # ── Model ────────────────────────────────────────────────
    ttk.Label(frame, text="Whisper Model:").grid(row=row, column=0, sticky="w", pady=5)
    model_var = tk.StringVar(value=config.model_name)
    model_combo = ttk.Combobox(
        frame, textvariable=model_var, values=WHISPER_MODELS, state="readonly", width=27
    )
    model_combo.grid(row=row, column=1, sticky="w", pady=5)
    row += 1

    # ── Recording mode ───────────────────────────────────────
    ttk.Label(frame, text="Recording Mode:").grid(row=row, column=0, sticky="w", pady=5)
    mode_var = tk.StringVar(value=config.recording_mode)
    mode_combo = ttk.Combobox(
        frame, textvariable=mode_var, values=RECORDING_MODES, state="readonly", width=27
    )
    mode_combo.grid(row=row, column=1, sticky="w", pady=5)
    row += 1

    # ── Audio device ─────────────────────────────────────────
    ttk.Label(frame, text="Microphone:").grid(row=row, column=0, sticky="w", pady=5)
    devices = []
    device_names = ["System Default"]
    try:
        all_devices = sd.query_devices()
        for i, d in enumerate(all_devices):
            if d["max_input_channels"] > 0:
                devices.append(i)
                device_names.append(f"{d['name']} (#{i})")
    except Exception:
        pass

    device_var = tk.StringVar(value=device_names[0])
    if config.audio_device is not None and config.audio_device in devices:
        idx = devices.index(config.audio_device) + 1
        device_var.set(device_names[idx])
    device_combo = ttk.Combobox(
        frame, textvariable=device_var, values=device_names, state="readonly", width=45
    )
    device_combo.grid(row=row, column=1, sticky="w", pady=5)
    row += 1

    # ── Formatting mode ──────────────────────────────────────
    ttk.Label(frame, text="Formatting:").grid(row=row, column=0, sticky="w", pady=5)
    fmt_var = tk.StringVar(value=config.formatting_mode)
    fmt_combo = ttk.Combobox(
        frame, textvariable=fmt_var, values=FORMATTING_MODES, state="readonly", width=27
    )
    fmt_combo.grid(row=row, column=1, sticky="w", pady=5)
    row += 1

    # ── Checkboxes ───────────────────────────────────────────
    sounds_var = tk.BooleanVar(value=config.play_sounds)
    ttk.Checkbutton(frame, text="Play sounds", variable=sounds_var).grid(
        row=row, column=0, columnspan=2, sticky="w", pady=5
    )
    row += 1

    notif_var = tk.BooleanVar(value=config.show_notifications)
    ttk.Checkbutton(frame, text="Show notifications", variable=notif_var).grid(
        row=row, column=0, columnspan=2, sticky="w", pady=5
    )
    row += 1

    boot_var = tk.BooleanVar(value=config.start_on_boot)
    ttk.Checkbutton(frame, text="Start on Windows startup", variable=boot_var).grid(
        row=row, column=0, columnspan=2, sticky="w", pady=5
    )
    row += 1

    # ── Save / Cancel ────────────────────────────────────────
    def save():
        config.hotkey = set(hotkey_var.get().lower().split("+"))
        config.model_name = model_var.get()
        config.recording_mode = mode_var.get()
        config.formatting_mode = fmt_var.get()
        config.play_sounds = sounds_var.get()
        config.show_notifications = notif_var.get()
        config.start_on_boot = boot_var.get()

        # Parse audio device
        selected = device_var.get()
        if selected == "System Default":
            config.audio_device = None
        else:
            for i, name in enumerate(device_names[1:]):
                if name == selected:
                    config.audio_device = devices[i]
                    break

        config.save()
        if on_save:
            on_save()
        root.destroy()

    btn_frame = ttk.Frame(frame)
    btn_frame.grid(row=row, column=0, columnspan=2, pady=20)
    ttk.Button(btn_frame, text="Save", command=save).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Cancel", command=root.destroy).pack(side="left", padx=10)
    row += 1

    # ── Version ───────────────────────────────────────────
    ttk.Label(frame, text=f"v{VERSION}", foreground="gray").grid(
        row=row, column=0, columnspan=2, sticky="e", pady=(0, 5)
    )

    root.mainloop()
