"""System tray icon using pystray."""

from typing import Callable, Optional

import pystray
from PIL import Image, ImageDraw


# Icon colors for different states
COLOR_IDLE = "#22c55e"        # Green — ready
COLOR_RECORDING = "#ef4444"   # Red — recording
COLOR_PROCESSING = "#eab308"  # Yellow — transcribing
COLOR_DISABLED = "#6b7280"    # Gray — model loading / disabled


def _create_icon_image(color: str, size: int = 64) -> Image.Image:
    """Generate a microphone-style tray icon with a colored background."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Solid rounded-rectangle background so it's visible in any tray theme
    draw.rounded_rectangle(
        [0, 0, size - 1, size - 1],
        radius=12,
        fill=color,
    )

    # Draw a simple white microphone shape in the center
    cx, cy = size // 2, size // 2
    mic_w, mic_h = size // 5, size // 3

    # Mic body (rounded rect)
    draw.rounded_rectangle(
        [cx - mic_w, cy - mic_h, cx + mic_w, cy + mic_w],
        radius=mic_w,
        fill="white",
    )
    # Mic arc (half-circle cradle below the body)
    arc_r = int(mic_w * 1.6)
    draw.arc(
        [cx - arc_r, cy - mic_w, cx + arc_r, cy + arc_r + mic_w // 2],
        start=0, end=180,
        fill="white", width=3,
    )
    # Mic stand (vertical line + base)
    stand_top = cy + arc_r + mic_w // 2
    stand_bottom = stand_top + mic_w
    draw.line(
        [cx, stand_top, cx, stand_bottom],
        fill="white", width=3,
    )
    base_w = mic_w
    draw.line(
        [cx - base_w, stand_bottom, cx + base_w, stand_bottom],
        fill="white", width=3,
    )

    return img


class TrayApp:
    """Manages the system tray icon and context menu."""

    def __init__(
        self,
        on_quit: Callable[[], None],
        on_settings: Optional[Callable[[], None]] = None,
    ) -> None:
        self._on_quit = on_quit
        self._on_settings = on_settings
        self._icon: Optional[pystray.Icon] = None

    def _build_menu(self) -> pystray.Menu:
        items = []
        if self._on_settings:
            items.append(pystray.MenuItem("Settings", self._on_settings))
        items.append(pystray.MenuItem("Quit", self._on_quit))
        return pystray.Menu(*items)

    def run(self, setup_callback: Optional[Callable[[pystray.Icon], None]] = None) -> None:
        """Start the tray icon. Blocks the calling thread."""
        self._icon = pystray.Icon(
            name="Speech2Txt",
            icon=_create_icon_image(COLOR_DISABLED),
            title="Speech2Txt — Loading...",
            menu=self._build_menu(),
        )
        self._icon.run(setup=setup_callback)

    def set_state(self, state: str) -> None:
        """Update the tray icon color and tooltip.

        state: 'idle', 'recording', 'processing', 'disabled'
        """
        if self._icon is None:
            return

        colors = {
            "idle": (COLOR_IDLE, "Speech2Txt — Ready"),
            "recording": (COLOR_RECORDING, "Speech2Txt — Recording..."),
            "processing": (COLOR_PROCESSING, "Speech2Txt — Transcribing..."),
            "disabled": (COLOR_DISABLED, "Speech2Txt — Disabled"),
        }
        color, title = colors.get(state, (COLOR_IDLE, "Speech2Txt"))
        self._icon.icon = _create_icon_image(color)
        self._icon.title = title

    def stop(self) -> None:
        """Stop the tray icon."""
        if self._icon is not None:
            self._icon.stop()
