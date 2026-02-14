# Speech2Txt

A local, system-wide dictation app for Windows 11. Press a hotkey, speak, and transcribed text appears at the cursor in any application — Notepad++, VS Code, Claude Code, browsers, Discord, etc.

Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) for fully offline speech-to-text. No cloud, no API keys, no subscription.

## Features

- **System-wide dictation** — works in any app that accepts text input
- **Hotkey toggle** — Ctrl+Alt+Space to start/stop recording (configurable)
- **Fast transcription** — base.en model transcribes 10+ seconds of audio in under 1 second on CPU
- **Voice commands** — "new line", "new paragraph", "delete that", "undo", "select all", etc.
- **Inline punctuation** — say "comma", "period", "question mark" and they're inserted as symbols
- **Multiple Whisper models** — switch between tiny.en, base.en, small.en, medium.en from settings
- **Settings UI** — right-click the tray icon to configure hotkey, model, microphone, recording mode
- **System tray icon** — color-coded status (green=ready, red=recording, yellow=transcribing)
- **Audio feedback** — beep sounds on recording start/stop
- **Single instance** — prevents multiple copies from running simultaneously
- **Push-to-talk mode** — hold hotkey to record, release to transcribe (optional)

## Requirements

- **Windows 10/11**
- A microphone
- That's it (if using the installer)

## Installation

### Option 1: One-Click Installer (Recommended)

Download **`Speech2Txt-Setup.exe`** from the [latest release](https://github.com/crack-kitty/speech2txt/releases) and run it. No Python or dependencies needed — everything is bundled.

The installer includes:
- Desktop shortcut (optional)
- Start Menu entry
- Uninstaller (Add/Remove Programs)

The Whisper model (~150MB) downloads automatically on first run.

### Option 2: From Source

Requires **Python 3.13 or 3.14**.

```bash
git clone https://github.com/crack-kitty/speech2txt.git
cd speech2txt
install.bat
```

Or manually:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```bash
# Run the app
python src/main.py
```

Or double-click the desktop shortcut if you've created one.

### Dictating

1. Look for the green microphone icon in the system tray
2. Click into any text field (Notepad++, VS Code, browser, etc.)
3. Press **Ctrl+Alt+Space** — icon turns red, you hear a beep
4. Speak naturally
5. Press **Ctrl+Alt+Space** again — icon turns yellow while transcribing
6. Text appears at the cursor

### Voice Commands

| Say this | Does this |
|----------|-----------|
| "new line" | Enter key |
| "new paragraph" | Double Enter |
| "tab" | Tab key |
| "period" / "comma" / "question mark" | Inserts punctuation |
| "exclamation mark" / "colon" / "semicolon" | Inserts punctuation |
| "open quote" / "close quote" | Inserts `"` |
| "open paren" / "close paren" | Inserts `(` or `)` |
| "delete that" / "scratch that" | Deletes the last dictated text |
| "undo" / "redo" | Ctrl+Z / Ctrl+Y |
| "select all" / "copy that" / "paste that" | Ctrl+A / Ctrl+C / Ctrl+V |
| "stop listening" | Pauses dictation |
| "literal period" | Types the word "period" instead of `.` |

### Settings

Right-click the tray icon and select **Settings** to configure:

- Hotkey combination
- Whisper model (tiny.en → medium.en)
- Recording mode (toggle or push-to-talk)
- Microphone selection
- Formatting mode (cleaned or raw)
- Sound and notification preferences

Settings are saved to `%APPDATA%\Speech2Txt\settings.json`.

## Building from Source

If you've forked the repo or made changes, you can build your own installer.

### Standalone .exe only

```bash
pip install pyinstaller
build.bat
```

Output: `dist\Speech2Txt.exe`

### Full Windows Installer

Requires [Inno Setup](https://jrsoftware.org/isdl.php) (`choco install innosetup -y`) and PyInstaller.

```bash
build_installer.bat
```

Output: `installer\Speech2Txt-Setup.exe` — a self-contained installer with desktop shortcut, Start Menu entry, and uninstaller. No Python needed on the target machine.

## Architecture

Threading-based design with the main thread running the pystray event loop:

```
Hotkey (pynput) → Record (sounddevice) → Transcribe (faster-whisper) → Commands → Paste (Ctrl+V)
```

- `src/main.py` — App controller, wires all components
- `src/config.py` — Settings management with JSON persistence
- `src/tray.py` — System tray icon with color-coded states
- `src/hotkey.py` — Global hotkey detection (toggle + push-to-talk)
- `src/recorder.py` — 16kHz mono audio capture to WAV bytes
- `src/transcriber.py` — Whisper model loading and transcription
- `src/commands.py` — Voice command processor with history tracking
- `src/injector.py` — Clipboard paste text injection
- `src/settings_ui.py` — tkinter settings window

## Extras

- [Discord Mute + Voice Command Toggle](Discord%20Mute%20to%20Voice%20Command%20-%20README.md) — AutoHotKey script that unmutes Discord, dictates, and re-mutes with a single hotkey

## License

Private — not currently licensed for distribution.
