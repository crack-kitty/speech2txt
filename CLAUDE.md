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

## Git
- Do NOT add Co-Authored-By lines to commits
