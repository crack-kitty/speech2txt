# Building a Local Dictation App for Windows 11

**A local, system-wide dictation app is entirely buildable on your hardware using Python, faster-whisper, and clipboard-based text injection — and Claude Code can write the whole thing.** Your Ryzen 9 5950X can transcribe 10 seconds of speech in under 1 second using the `medium.en` Whisper model, which delivers near-human accuracy with auto-punctuation built in. The recommended approach uses faster-whisper for transcription, pynput for hotkey detection, sounddevice for audio capture, and clipboard paste simulation for injecting text into any focused window. Below is the complete research and a phased build plan you can hand directly to Claude Code.

---

## How commercial cloud dictation apps work under the hood

Commercial cloud dictation services typically use a **cloud-only** two-stage pipeline. Audio streams to their servers where a custom ASR model transcribes it in under **200ms**, then a fine-tuned **LLM** reformats the transcript — removing filler words ("um," "uh"), adding punctuation, correcting grammar, and adapting tone to context — in another **200ms**. Total end-to-end latency targets **under 700ms at p99**. Some apps capture screenshots of the active window to understand context (email vs. Slack vs. code editor) and adjust formatting accordingly.

The key UX pattern is **hold-to-talk**: press and hold a hotkey, speak naturally, release, and polished text appears at the cursor 1-2 seconds later. This "batch" approach (no streaming word-by-word display) lets the LLM rewrite what you *meant*, not just what you said. For example, saying "Let's meet tomorrow, no wait, Friday instead" produces "Let's meet Friday." Users report **170+ WPM** dictation speed and **90% of text needs no edits**.

Electron-based implementations typically consume ~800MB RAM. Text injection uses OS-level keyboard simulation via Accessibility APIs. Cloud-only apps require an internet connection at all times.

**What makes cloud dictation good is the LLM post-processing, not the transcription itself.** The secret sauce is that they don't just transcribe — they rewrite. For a local app, you can approximate this with Whisper's built-in punctuation and capitalization plus a simple command processor, then optionally add LLM cleanup later.

---

## Your AMD GPU situation and why CPU is actually fine

**The critical hardware finding: your RX 6800 cannot use CUDA, and ROCm is Linux-only for consumer Radeon GPUs on Windows.** However, two viable GPU acceleration paths exist, and CPU-only performance is more than sufficient for real-time dictation.

**GPU options on Windows with the RX 6800:**

- **whisper.cpp with Vulkan** (`GGML_VULKAN=ON` build flag) works on AMD GPUs on Windows. Users report Vulkan being **~10x faster than CPU**. Your 16GB VRAM can fit even the largest Whisper model. Pre-built Windows binaries with Vulkan exist on GitHub. However, this requires C++ compilation or finding pre-built binaries, and Python integration is via subprocess calls — adding complexity.
- **sherpa-onnx with DirectML** uses ONNX Runtime's DirectML execution provider, which works with any DirectX 12-capable GPU including your RX 6800. AMD has published production guidance for this path. sherpa-onnx has native Python bindings (`pip install sherpa-onnx`).

**CPU-only performance on your Ryzen 9 5950X is excellent for dictation:**

| Model | Time to process 10s of audio | Accuracy | Recommended? |
|-------|------------------------------|----------|-------------|
| tiny.en | ~0.1-0.2s | Good for simple speech | Fast but lower quality |
| base.en | ~0.2-0.3s | Decent | Good starting point |
| small.en | ~0.4-0.6s | Very good | Great balance |
| **medium.en** | **~0.6-1.0s** | **Near-human** | **Best for dictation** |
| large-v3 | ~1.5-2.5s | Best available | Borderline for real-time |
| large-v3-turbo | ~0.3-0.5s | Near large-v3 quality | Excellent with GPU |

**The recommendation is to start with `faster-whisper` using the `medium.en` model on CPU.** Processing 10 seconds of speech in under 1 second on your 16-core CPU provides a smooth experience. GPU acceleration is a nice-to-have optimization for later, not a requirement. The `.en` English-only variants are slightly more accurate for English dictation.

---

## Local versus cloud transcription: a clear decision matrix

**For a privacy-respecting, zero-cost dictation tool, local transcription with faster-whisper is the clear winner.** Cloud APIs add latency (network round-trip), cost (per-minute billing), and privacy concerns, but offer streaming and slightly better accuracy for edge cases.

**Local options ranked for this project:**

1. **faster-whisper** (CTranslate2-based) — **recommended.** 4x faster than original Whisper, lower memory usage, INT8 quantization support, excellent Python API (`pip install faster-whisper`). CPU-only on your AMD system, but fast enough. Used by whisper-writer, RealtimeSTT, and most open-source dictation tools.
2. **whisper.cpp** — Best raw performance, Vulkan GPU support for your RX 6800, but Python integration requires subprocess calls or bindings. Better as a future optimization.
3. **sherpa-onnx** — DirectML GPU acceleration, native Python bindings, supports Whisper ONNX models plus faster alternatives like Zipformer. Actively maintained with AMD production guidance. Good alternative if you want GPU acceleration from day one.
4. **Vosk** — Lightning-fast streaming but significantly lower accuracy (10-15% WER vs. Whisper's 3-5%). No auto-punctuation. Not recommended.
5. **Coqui STT / Mozilla DeepSpeech** — **Discontinued.** Do not use.

**Cloud options if you later want to add a cloud mode:**

| Provider | Cost/min | Streaming | Best for |
|----------|----------|-----------|----------|
| AssemblyAI | $0.0025 | ✅ Yes | Cheapest per-minute |
| Deepgram | $0.0043-0.0077 | ✅ Yes, ~300ms | Lowest latency streaming |
| OpenAI Whisper API | $0.003-0.006 | ❌ Batch only | Simple integration |
| Azure Speech | $0.006-0.017 | ✅ Yes | Best Windows integration |
| Google Cloud STT | $0.024-0.036 | ✅ Yes | Multilingual breadth |

**All major Whisper variants (local and cloud) produce punctuated, capitalized output natively.** This is a huge advantage — you get auto-punctuation for free. Using an initial prompt like `"Hello, welcome to my lecture."` encourages Whisper to consistently punctuate output.

---

## How to inject text into any Windows application

**The most reliable method is clipboard paste simulation: save the clipboard, set it to your transcribed text, simulate Ctrl+V, wait 150ms, then restore the original clipboard.** This is what Talon Voice, AutoHotkey dictation scripts, and most open-source dictation tools use. It works across Win32, UWP, Electron, browser text fields, Word, Slack, Discord, VS Code, and terminals.

The alternative — `SendInput` with `KEYEVENTF_UNICODE` — sends each character individually. Microsoft's own documentation says this flag was designed for "nonkeyboard-input methods such as handwriting recognition or voice recognition." It works universally but is slow for long text (500 characters takes ~450ms) and triggers autocomplete in IDEs.

**Production dictation tools' approaches:**

- **Dragon NaturallySpeaking** uses the Text Services Framework (TSF), a COM-based API specifically designed for speech input. TSF is architecturally ideal but extremely complex to implement (requires C/C++ COM programming, registry DLL registration). Not practical for a Python app.
- **Windows built-in Voice Typing (Win+H)** also uses TSF natively since it's part of the OS.
- **Talon Voice** uses keyboard simulation (SendInput) for individual keys and clipboard save/restore + paste for bulk text insertion — exactly the approach recommended here.

**The recommended implementation in Python:**

```python
# Primary: clipboard paste (fast, universal, handles Unicode)
import pyperclip, pyautogui, time

def inject_text(text):
    old_clipboard = pyperclip.paste()     # Save current clipboard
    pyperclip.copy(text)                   # Set transcribed text
    pyautogui.hotkey('ctrl', 'v')          # Paste into active window
    time.sleep(0.15)                       # Wait for paste to complete
    pyperclip.copy(old_clipboard)          # Restore original clipboard
```

For individual key commands (Enter, Backspace, Ctrl+Z), use `pyautogui.press()` or `pyautogui.hotkey()` directly. The clipboard method is only needed for multi-character text insertion.

**One caveat:** pasting into rich text editors (Word, Google Docs) with `Ctrl+V` may carry formatting if the clipboard contains rich content. Setting only plain text (CF_UNICODETEXT) via `pyperclip` avoids this — the pasted text adopts the formatting at the cursor position, which is the desired behavior for dictation.

---

## Open-source projects worth knowing about

Several existing projects can serve as starting points, architectural references, or even direct solutions. The most relevant ones for this project:

**whisper-writer** (github.com/savbell/whisper-writer, ~2,000+ stars) is the single most relevant project. It's a Python app using faster-whisper, PyQt5, pynput, and pyautogui that does exactly what you want: press a hotkey, speak, text appears in the active window. It has four recording modes (continuous, voice activity detection, push-to-talk, toggle), a settings UI, and runs on Windows. It lacks voice commands and LLM post-processing but is an excellent starting point or reference.

**RealtimeSTT** (github.com/KoljaB/RealtimeSTT) is the best Python library for the real-time speech-to-text pipeline. It wraps faster-whisper with WebRTC VAD and Silero VAD for voice activity detection, provides instant partial results, and handles the audio-to-text pipeline robustly. Many dictation apps build on top of it. The author notes it's in maintenance mode but still merging PRs.

**OmniDictate** (github.com/gurjar1/OmniDictate) is a Windows-specific dictation app using faster-whisper with a modern UI, push-to-talk, VAD, and word filtering. It targets NVIDIA GPUs but the architecture is useful reference.

**OpenWhispr** (github.com/HeroTools/open-whispr) is a feature-complete open-source dictation app — cross-platform Electron app with local whisper.cpp + cloud API support, AI agent mode for command detection, model management, and global hotkey paste. If you want something that works immediately rather than building from scratch, try this first.

**Whispering** (github.com/braden-w/whispering) is built with Tauri (Rust + Svelte), offering a much lighter alternative to Electron. Supports whisper.cpp local and Groq/OpenAI cloud.

**Buzz** (github.com/chidiwilliams/buzz, ~17,600 stars) is the most popular Whisper GUI app but is a transcription tool, not a dictation tool — it processes audio files, not live microphone input for typing.

---

## Voice commands and auto-punctuation strategy

**Voice commands are best implemented as a simple string-matching command dictionary applied to each transcribed utterance, with a typed-history stack for "delete that."** This is the approach used by Dragon NaturallySpeaking's basic mode and most open-source dictation tools.

The processing pipeline for each utterance should be:

1. Normalize the transcript (strip whitespace, lowercase for matching)
2. Check for exact command matches ("delete that", "new line", "select all", "undo")
3. If no command match, replace embedded punctuation words ("period" → ".", "comma" → ",")
4. Type the resulting text and push it onto the history stack

**Handling "delete that"** requires maintaining a stack of previously typed text segments. When the user says "delete that," pop the last segment and send equivalent backspace keystrokes. Multiple "delete that" commands in succession continue popping the stack.

**Handling ambiguity** (does "period" mean the punctuation or the word?): by default, treat punctuation words as their symbols. Provide a "literal" escape command — "literal period" types the word "period." This mirrors Windows built-in dictation behavior.

**Minimum command set to implement:**

- **Navigation:** "new line" (Enter), "new paragraph" (double Enter), "tab" (Tab)
- **Punctuation:** "period", "comma", "question mark", "exclamation mark", "colon", "semicolon", "open quote", "close quote", "open paren", "close paren", "hyphen", "dash"
- **Editing:** "delete that" / "scratch that", "undo", "redo", "select all", "copy that", "paste that"
- **Control:** "stop listening"

**Auto-punctuation is largely solved by Whisper itself.** Whisper was trained on punctuated transcriptions and natively produces periods, commas, question marks, and capitalized sentences. To ensure consistent punctuation, pass an initial prompt like `"Hello, welcome."` to signal that output should be punctuated. The `medium.en` model produces reliable punctuation; smaller models may occasionally skip it.

For enhanced punctuation, the `deepmultilingualpunctuation` Python library can post-process any transcript to add missing punctuation marks. For premium quality, sending the transcript through an LLM (GPT-4 or Claude API) for cleanup matches what commercial cloud dictation services do, but adds 200-1000ms latency and API costs.

---

## The recommended tech stack and architecture

**Python 3.11+ is the right choice** for this project because it has the richest library ecosystem for audio processing, keyboard automation, and Whisper integration on Windows. Claude Code generates Python most reliably, and multiple proven open-source dictation apps already exist in Python to reference. The alternatives — C# (smaller Whisper ecosystem), Electron (overkill overhead), Rust/Tauri (steep learning curve) — all add friction without meaningful benefit for this use case.

**Complete dependency list:**

```
faster-whisper>=1.0.0      # Speech-to-text (Whisper via CTranslate2)
sounddevice>=0.4.6          # Microphone audio capture
numpy>=1.24.0               # Audio array handling
pynput>=1.7.6               # Global hotkey detection
pystray>=0.19.5             # System tray icon
Pillow>=10.0.0              # Icon image handling
pyperclip>=1.8.2            # Clipboard operations
pyautogui>=0.9.54           # Keyboard simulation / Ctrl+V paste
```

**Architecture: threading with queue-based communication.** The main thread runs the pystray system tray event loop. Three background threads handle hotkey listening (pynput), audio recording (sounddevice), and transcription (faster-whisper). Communication between threads uses `threading.Event` for signals and `queue.Queue` for data. Threading is correct here because faster-whisper releases the GIL during C-level inference, and the main bottlenecks are I/O-bound (audio capture, keyboard events).

**Project file structure:**

```
whisper-dictation/
├── CLAUDE.md               # Instructions for Claude Code
├── requirements.txt        # Python dependencies
├── README.md               # Setup and usage guide
├── src/
│   ├── main.py             # Entry point, initializes all components
│   ├── tray.py             # System tray icon and menu (pystray)
│   ├── hotkey.py           # Global hotkey detection (pynput)
│   ├── recorder.py         # Audio recording (sounddevice)
│   ├── transcriber.py      # Whisper transcription (faster-whisper)
│   ├── commands.py         # Voice command processor
│   ├── injector.py         # Text injection (clipboard paste)
│   └── config.py           # Settings and configuration
├── assets/
│   └── icon.png            # System tray icon
└── tests/
    └── test_commands.py    # Voice command tests
```

---

## Setting up Claude Code for this project

**Use Claude Code on native Windows (not WSL2)** because the app needs direct access to Windows audio devices, system tray, keyboard hooks, and clipboard. WSL2 is a Linux environment that cannot interact with Windows GUI elements. Install Claude Code via `winget install Anthropic.ClaudeCode` or use the Claude Desktop App's Code tab — both work identically.

**The single most important thing is creating a CLAUDE.md file before starting.** Claude Code reads this file at the start of every conversation, and it serves as the project's "memory." Run `/init` in Claude Code to generate a starter, then customize it with the project details below.

**Essential Claude Code workflow tips:**

- **Work in phases, one feature per session.** Start each session by telling Claude "Look at the codebase and create a plan for implementing X. Don't write any code yet." Review the plan, then ask it to implement.
- **Use `/clear` between features** to reset context. Claude's performance degrades as the context window fills.
- **Commit after each working feature.** This gives you safe rollback points.
- **Use "think harder" or "ultrathink" keywords** for complex architecture decisions — these allocate more reasoning budget.
- **Test frequently.** After each feature, ask Claude "Run this and tell me if it works."
- Watch for: missing system-level dependencies (PortAudio for audio libraries) that Claude can't install itself. If `sounddevice` fails, you may need to install the Microsoft Visual C++ Redistributable.

**CLAUDE.md content to create before starting:**

```markdown
# Whisper Dictation App

## Purpose
A Windows 11 system-wide dictation app. Press a hotkey, speak,
and transcribed text is pasted into whatever application is focused.

## Tech Stack
- Python 3.11+ on Windows 11
- faster-whisper (medium.en model, CPU inference)
- sounddevice (16kHz mono audio capture)
- pynput (global hotkey: Ctrl+Alt+Space)
- pystray + Pillow (system tray icon)
- pyperclip + pyautogui (clipboard paste text injection)
- PyInstaller for packaging

## Architecture
Threading-based. Main thread = pystray event loop.
Background threads: hotkey listener, audio recorder, transcriber.
Pipeline: hotkey → record audio → transcribe → process commands → paste text.
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
```

---

## The four-phase build plan for Claude Code

### Phase 1 — Basic dictation (hotkey → speak → text appears)

This phase delivers a working dictation app in its simplest form. Give Claude Code these instructions:

**Session 1: Project setup and system tray**
"Create a Python project with the file structure in CLAUDE.md. Set up requirements.txt with all dependencies. Create a system tray app using pystray that shows an icon in the Windows taskbar notification area with a right-click menu containing 'Quit'. The app should run and show the tray icon. Use a simple colored circle as the icon (generate it with Pillow, don't require an external image file)."

**Session 2: Hotkey detection**
"Add global hotkey detection using pynput. When the user presses Ctrl+Alt+Space, print 'Recording started' to console. When they press it again, print 'Recording stopped'. Use a toggle approach (press once to start, press again to stop). Change the tray icon color to red when recording, green when idle. Make the hotkey configurable in config.py."

**Session 3: Audio recording**
"Add audio recording using sounddevice. When the hotkey toggles recording on, start capturing microphone audio at 16000 Hz mono into a numpy buffer. When the hotkey toggles recording off, stop capturing and save the audio to a temporary WAV file. Print the duration of the recording to console. Handle the case where no audio device is available gracefully."

**Session 4: Whisper transcription**
"Integrate faster-whisper for transcription. At app startup, load the 'base.en' model in a background thread (show 'Loading model...' in console; we'll upgrade to medium.en later). When recording stops and audio is saved, transcribe it using the loaded model with initial_prompt='Hello, welcome.' for punctuation. Print the transcribed text to console. Include timing — print how many seconds the transcription took."

**Session 5: Text injection**
"Add text injection using the clipboard paste method. After transcription produces text: (1) save the current clipboard contents, (2) copy the transcribed text to clipboard using pyperclip, (3) simulate Ctrl+V using pyautogui to paste into the active window, (4) wait 150ms, (5) restore the original clipboard. Test this by running the app, clicking into Notepad, pressing the hotkey, speaking, and verifying text appears in Notepad."

**After Phase 1:** You have a working dictation app. Speak and text appears in any window.

### Phase 2 — Voice commands

**Session 6: Command processor**
"Create a VoiceCommandProcessor class in commands.py. It should maintain a typed_history list tracking each text segment that was injected. Implement these command categories: (1) Navigation commands — 'new line' sends Enter, 'new paragraph' sends Enter twice, 'tab' sends Tab. (2) Punctuation commands — 'period' inserts '.', 'comma' inserts ',', 'question mark' inserts '?', 'exclamation mark' inserts '!', 'colon' inserts ':', 'semicolon' inserts ';'. (3) Editing commands — 'delete that' sends backspace keystrokes to remove the last injected text segment, 'undo' sends Ctrl+Z, 'select all' sends Ctrl+A. (4) Control commands — 'stop listening' pauses the hotkey listener. The processor should first check for exact command matches (case-insensitive), then check for trailing punctuation words in the transcript, then fall through to normal text injection. Write unit tests in tests/test_commands.py."

**Session 7: Integration**
"Integrate the VoiceCommandProcessor into the main pipeline. After transcription, pass the text through the command processor before injecting it. If the processor detects a command, execute it instead of typing text. For punctuation commands embedded in text (e.g., 'Hello comma how are you'), replace them inline and inject the resulting text. Add a 'literal' prefix — if the user says 'literal period', type the word 'period' instead of the punctuation mark."

### Phase 3 — Auto-punctuation polish and model upgrade

**Session 8: Model upgrade and punctuation**
"Upgrade the Whisper model from base.en to medium.en for better accuracy and punctuation. Add a setting in config.py for model selection (tiny.en, base.en, small.en, medium.en). Add a startup progress indicator showing model download/loading progress. Verify that Whisper's built-in punctuation is working well by testing with several spoken sentences. If punctuation is inconsistent, try the initial_prompt trick with a well-punctuated sentence."

**Session 9: Text formatting**
"Add post-processing to the transcription output: (1) Ensure the first letter of each new dictation segment is capitalized if it starts a sentence. (2) Add a space before injected text if the previous injection didn't end with a newline. (3) Handle the case where the user dictates multiple sentences — Whisper should already handle this, but verify. (4) Add a 'formatting mode' option in config that can be set to 'raw' (inject exactly what Whisper outputs) or 'cleaned' (apply the post-processing)."

### Phase 4 — System tray app, settings, and packaging

**Session 10: Settings UI**
"Create a settings window using tkinter that opens when the user right-clicks the tray icon and selects 'Settings'. Include: (1) Hotkey configuration (text field showing current hotkey combo), (2) Whisper model selection dropdown (tiny.en through medium.en), (3) Recording mode selection (push-to-talk vs toggle), (4) Audio device selection dropdown (list available microphones from sounddevice), (5) A 'Start on Windows startup' checkbox. Save settings to a JSON file in the user's AppData folder. Load settings on startup."

**Session 11: Push-to-talk mode**
"Add a push-to-talk recording mode as an alternative to toggle mode. In push-to-talk: hold the hotkey to record, release to stop and transcribe. Use pynput's on_press and on_release events. Make this selectable in settings. Push-to-talk should feel snappy — start recording immediately on keypress, transcribe immediately on release."

**Session 12: Visual feedback and polish**
"Add visual feedback: (1) Change the tray icon to red while recording, yellow while transcribing, green when ready. (2) Show a small Windows toast notification with the transcribed text after injection (use the win10toast or plyer library). (3) Add an option to play a subtle beep sound when recording starts and stops (use winsound.Beep). (4) Add error handling throughout — if transcription fails, show a notification instead of crashing. (5) Handle the edge case where no microphone is connected."

**Session 13: PyInstaller packaging**
"Package the app with PyInstaller into a single .exe file. Create a build script (build.bat) that: (1) activates the venv, (2) runs PyInstaller with --onefile --noconsole --name WhisperDictation flags, (3) copies the exe to a dist/ folder. Handle the faster-whisper model files — they should download automatically on first run, not be bundled in the exe. Test the packaged exe on a clean path (no venv activated) to verify it works standalone."

---

## Conclusion: the practical path forward

The entire project is achievable in **4-6 focused sessions with Claude Code** for Phase 1 (working dictation), with Phases 2-4 adding ~4-6 more sessions. The most critical technical decisions are already made: **faster-whisper with medium.en on CPU** for transcription (your Ryzen 9 5950X handles it comfortably), **clipboard paste simulation** for universal text injection, and **pynput** for hotkey detection. This exact stack is proven by whisper-writer's 2,000+ GitHub stars and active user base.

**If you want something working today before building custom,** try OpenWhispr (open-source, cross-platform, local+cloud) or whisper-writer (Python, simpler, Windows-focused). Both are free and functional.

The biggest gap between a local approach and commercial cloud dictation is the LLM post-processing layer — the ability to remove filler words, rewrite incoherent sentences, and adapt tone to context. You can approximate this later by adding an optional cloud LLM pass (send each transcript to Claude or GPT-4 API for cleanup, adding ~500ms latency and ~$0.001 per utterance). But Whisper's native punctuation and capitalization get you **80% of the way there for free, locally, with zero ongoing cost**. Start with the basics, and add intelligence incrementally.