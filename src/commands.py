"""Voice command processor — detects and executes spoken commands."""

from typing import Optional

from injector import inject_text, send_key, send_hotkey, send_backspaces


# Exact-match commands: spoken phrase -> action
NAVIGATION_COMMANDS = {
    "new line": ("key", "enter"),
    "newline": ("key", "enter"),
    "new paragraph": ("key_repeat", "enter", 2),
    "tab": ("key", "tab"),
}

EDITING_COMMANDS = {
    "delete that": ("delete_last",),
    "scratch that": ("delete_last",),
    "undo": ("hotkey", "ctrl", "z"),
    "undo that": ("hotkey", "ctrl", "z"),
    "redo": ("hotkey", "ctrl", "y"),
    "redo that": ("hotkey", "ctrl", "y"),
    "select all": ("hotkey", "ctrl", "a"),
    "copy that": ("hotkey", "ctrl", "c"),
    "paste that": ("hotkey", "ctrl", "v"),
    "cut that": ("hotkey", "ctrl", "x"),
}

CONTROL_COMMANDS = {
    "stop listening": ("control", "stop"),
}

# Punctuation words to replace inline
PUNCTUATION_MAP = {
    "period": ".",
    "full stop": ".",
    "comma": ",",
    "question mark": "?",
    "exclamation mark": "!",
    "exclamation point": "!",
    "colon": ":",
    "semicolon": ";",
    "open quote": '"',
    "close quote": '"',
    "open paren": "(",
    "close paren": ")",
    "open parenthesis": "(",
    "close parenthesis": ")",
    "hyphen": "-",
    "dash": " — ",
    "ellipsis": "...",
}

# Merge all exact-match command dicts
ALL_COMMANDS = {}
ALL_COMMANDS.update(NAVIGATION_COMMANDS)
ALL_COMMANDS.update(EDITING_COMMANDS)
ALL_COMMANDS.update(CONTROL_COMMANDS)


class VoiceCommandProcessor:
    """Processes transcribed text for voice commands and punctuation."""

    def __init__(self) -> None:
        self.typed_history: list[str] = []

    def process(self, text: str) -> Optional[str]:
        """Process transcribed text. Returns a control signal or None.

        Side effect: executes the command or injects text.
        Returns 'stop' if the user said 'stop listening', else None.
        """
        normalized = text.strip().lower().rstrip(".")

        # Check for "literal" prefix
        if normalized.startswith("literal "):
            word = text.strip()[len("literal "):]
            self._inject_and_track(word)
            return None

        # Check exact command matches
        if normalized in ALL_COMMANDS:
            return self._execute_command(ALL_COMMANDS[normalized])

        # Replace inline punctuation words
        processed = self._replace_punctuation(text.strip())
        self._inject_and_track(processed)
        return None

    def _execute_command(self, action: tuple) -> Optional[str]:
        """Execute a command action tuple."""
        cmd_type = action[0]

        if cmd_type == "key":
            send_key(action[1])
        elif cmd_type == "key_repeat":
            for _ in range(action[2]):
                send_key(action[1])
        elif cmd_type == "hotkey":
            send_hotkey(*action[1:])
        elif cmd_type == "delete_last":
            self._delete_last()
        elif cmd_type == "control":
            return action[1]

        return None

    def _delete_last(self) -> None:
        """Delete the last injected text segment."""
        if not self.typed_history:
            return
        last = self.typed_history.pop()
        send_backspaces(len(last))

    def _replace_punctuation(self, text: str) -> str:
        """Replace punctuation words with their symbols."""
        result = text
        # Sort by length (longest first) to avoid partial matches
        for word, symbol in sorted(
            PUNCTUATION_MAP.items(), key=lambda x: len(x[0]), reverse=True
        ):
            # Case-insensitive replacement
            lower = result.lower()
            idx = 0
            new_result = ""
            while idx < len(lower):
                found = lower.find(word, idx)
                if found == -1:
                    new_result += result[idx:]
                    break
                new_result += result[idx:found]
                # Remove leading space before punctuation if symbol doesn't start with space
                if new_result.endswith(" ") and not symbol.startswith(" "):
                    new_result = new_result[:-1]
                new_result += symbol
                idx = found + len(word)
                # After punctuation, skip the trailing space from the word boundary
                # but add a space back if there's more text and the symbol
                # is non-sentence-ending (comma, colon, semicolon, etc.)
                if idx < len(result) and result[idx] == " ":
                    idx += 1
                    # Add space after punctuation if more text follows
                    if idx < len(result):
                        new_result += " "
            result = new_result
        return result

    def _inject_and_track(self, text: str) -> None:
        """Inject text and record it in history for delete-that."""
        inject_text(text)
        self.typed_history.append(text)
