# Whisper Dictation App (Speech2Txt)

## Purpose
A Windows 11 system-wide dictation app. Press a hotkey, speak,
and transcribed text is pasted into whatever application is focused.

## Tech Stack
- Python 3.15 on Windows 11
- faster-whisper (medium.en model, CPU inference)
- sounddevice (16kHz mono audio capture)
- pynput (global hotkey: Ctrl+Alt+Space)
- pystray + Pillow (system tray icon)
- pyperclip + pyautogui (clipboard paste text injection)
- PyInstaller for packaging

## Architecture
Threading-based. Main thread = pystray event loop.
Background threads: hotkey listener, audio recorder, transcriber.
Pipeline: hotkey -> record audio -> transcribe -> process commands -> paste text.
Use threading.Event for signaling, queue.Queue for data passing.

## Code Style
- Type hints on all functions
- Each module in its own file under src/
- Docstrings on classes and public methods
- Keep functions under 30 lines where possible

## Build & Run
- python -m venv venv && venv\Scripts\activate
- pip install -r requirements.txt
- python src/main.py
- PyInstaller: pyinstaller --onefile --noconsole src/main.py

## Installer
- Pre-built installer: `installer/Speech2Txt-Setup.exe` (built with PyInstaller + Inno Setup)
- Do NOT auto-rebuild the installer on every push, ASK.
- At the end of a work session, if source code was changed, ASK the user if they want to rebuild the installer before wrapping up
- Build command: `build_installer.bat` (requires Inno Setup installed)

## Git
- Do NOT add Co-Authored-By lines to commits
- Every commit bumps the version (semantic versioning in `VERSION` file):
  - Default: bump PATCH (1.1.0 → 1.1.1)
  - User says "minor": bump MINOR (1.1.0 → 1.2.0)
  - User says "major": bump MAJOR (1.1.0 → 2.0.0)
- On every commit: update `VERSION`, update `AppVersion` in `installer.iss`, create git tag `v{VERSION}`
- After pushing, ASK the user if they want to rebuild the installer and create a GitHub release
