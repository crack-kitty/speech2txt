# Discord Mute + Voice Command Toggle

A simple AutoHotKey script that lets you unmute Discord, dictate via a speech-to-text app, and re-mute Discord — all with a single hotkey. No more hot mic moments while you're talking to your computer.

## How It Works

Press **Ctrl+Shift+V** once to:
1. Unmute Discord
2. Send a clean Ctrl+Alt+Space tap to toggle recording ON

Press **Ctrl+Shift+V** again to:
1. Send a clean Ctrl+Alt+Space tap to toggle recording OFF (triggers transcription/paste)
2. Re-mute Discord

## Requirements

- **Windows** (AutoHotKey is Windows-only)
- **AutoHotKey v2.0** — download from [https://www.autohotkey.com](https://www.autohotkey.com)
- **Discord** (desktop app)
- A **speech-to-text application** in toggle mode that uses Ctrl+Alt+Space (e.g., Speech2Txt or similar Whisper-based tools)

## Setup

### Step 1: Set Up a Global Mute Keybind in Discord

Discord needs a global hotkey for mute so the script can toggle it even when Discord isn't the active window.

1. Open **Discord** → **Settings** (gear icon, bottom-left)
2. Go to **Keybinds** (under App Settings)
3. Click **Add a Keybind**
4. Set the action to **Toggle Mute**
5. Set the shortcut to **Ctrl+Shift+F9** (or any combo that doesn't conflict with your other apps)
6. Make sure it says **Global** — this means it works even when Discord is in the background
7. Test it: click into a different app and press Ctrl+Shift+F9. You should see the mute icon toggle in Discord.

### Step 2: Install AutoHotKey v2

1. Go to [https://www.autohotkey.com](https://www.autohotkey.com)
2. Download and install — choose **v2.0** when prompted (not v1.1)
3. Run through the installer with default settings

### Step 3: Create the Script File

Create a new file called `Discord Mute to Voice Command.ahk` and paste in the following:

```ahk
voiceMode := false

*^+v::
{
    global voiceMode

    if (!voiceMode)
    {
        KeyWait "Ctrl"
        KeyWait "Shift"
        KeyWait "v"

        voiceMode := true
        Send "^+{F9}"              ; Unmute Discord
        Sleep 200
        Send "^!{Space}"           ; Clean tap — toggles recording ON
    }
    else
    {
        KeyWait "Ctrl"
        KeyWait "Shift"
        KeyWait "v"

        voiceMode := false
        Send "^!{Space}"           ; Clean tap — toggles recording OFF
        Sleep 500
        Send "^+{F9}"             ; Mute Discord
    }
}
```

**Note about the script:**
- The `*` before `^+v` is a wildcard that tells AHK to fire the hotkey even if extra modifier keys happen to be held.
- `KeyWait` lines on both paths ensure your physical Ctrl, Shift, and V keys are fully released before sending any key combos, preventing conflicts.
- No modifier keys are held down during recording — you can freely alt-tab and interact with other windows while dictating.

### Step 4: Run the Script

- **Double-click** the `.ahk` file to start it
- You'll see a small green **H** icon appear in your system tray (bottom-right of taskbar, near the clock)
- That means it's running in the background

## Usage

1. Join a Discord voice channel and make sure you're **muted**
2. Press **Ctrl+Shift+V** → Discord unmutes, voice app starts listening
3. Speak your message
4. Press **Ctrl+Shift+V** again → voice app stops and converts your speech, Discord re-mutes

## Customization

**Change the trigger hotkey:** Replace `*^+v` at the top of the script with a different combo. The `*` is a wildcard — keep it. AHK uses these symbols for modifier keys:

| Symbol | Key |
|--------|-----|
| `^` | Ctrl |
| `+` | Shift |
| `!` | Alt |
| `#` | Win |

For example, `^!F10` would be Ctrl+Alt+F10.

**Change the Discord mute keybind:** If you used something other than Ctrl+Shift+F9 in Discord, update the two `Send "^+{F9}"` lines to match.

**Change the voice app trigger:** If your speech-to-text app uses a different key combination, update both `Send "^!{Space}"` lines accordingly.

## Managing the Script

- **Stop the script:** Right-click the green H icon in the system tray → **Exit**
- **Reload after editing:** Right-click the green H icon → **Reload Script**
- **Start automatically with Windows:** Press `Win+R`, type `shell:startup`, press Enter. Drop a shortcut to your `.ahk` file into that folder.

## Troubleshooting

**Discord doesn't mute/unmute:** Make sure your Discord keybind is set to **Global** (not just in-app). Test it manually first before using the script.

**Voice app doesn't trigger:** Some speech-to-text apps detect simulated key presses differently than real ones. If this happens, you may need to check your specific app's documentation for compatibility with AutoHotKey.

**Keys seem "stuck" after running:** This was a known issue with older versions of the script that held modifier keys during recording. The current version uses clean taps instead, so this should no longer occur. If it does happen, just physically tap Ctrl, Alt, and Space once each to release them.

**Syntax errors when double-clicking:** You probably installed AutoHotKey v1 instead of v2. Either reinstall with v2, or let someone know and the script can be rewritten for v1 syntax.
