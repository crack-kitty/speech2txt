"""Generate a multi-resolution .ico file with a microphone icon."""

import os
from PIL import Image, ImageDraw


def create_microphone_icon(size: int) -> Image.Image:
    """Create a microphone icon at the given size."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Green gradient background (simulated with two-tone fill)
    # Top color: brighter green, bottom: deeper green
    for y in range(size):
        t = y / size
        r = int(34 * (1 - t) + 16 * t)
        g = int(197 * (1 - t) + 160 * t)
        b = int(94 * (1 - t) + 60 * t)
        draw.line([(0, y), (size - 1, y)], fill=(r, g, b, 255))

    # Round the corners by masking
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    radius = max(size // 5, 3)
    mask_draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=255)
    img.putalpha(mask)

    draw = ImageDraw.Draw(img)

    # Scale factors relative to icon size
    cx = size / 2
    cy = size / 2

    # Microphone body (capsule shape)
    mic_w = size * 0.16
    mic_top = size * 0.15
    mic_bottom = size * 0.52
    mic_radius = mic_w

    # Shadow (slight offset darker shape)
    shadow_offset = max(size // 32, 1)
    shadow_color = (0, 100, 40, 80)
    draw.rounded_rectangle(
        [cx - mic_w + shadow_offset, mic_top + shadow_offset,
         cx + mic_w + shadow_offset, mic_bottom + shadow_offset],
        radius=mic_radius, fill=shadow_color,
    )

    # Mic body (white capsule)
    draw.rounded_rectangle(
        [cx - mic_w, mic_top, cx + mic_w, mic_bottom],
        radius=mic_radius, fill="white",
    )

    # Cradle arc
    arc_w = size * 0.26
    arc_top = size * 0.35
    arc_bottom = size * 0.65
    line_width = max(size // 16, 2)
    draw.arc(
        [cx - arc_w, arc_top, cx + arc_w, arc_bottom],
        start=0, end=180, fill="white", width=line_width,
    )

    # Stand (vertical line from arc bottom center to base)
    stand_top = arc_bottom
    stand_bottom = size * 0.78
    draw.line(
        [(cx, stand_top), (cx, stand_bottom)],
        fill="white", width=line_width,
    )

    # Base (horizontal line)
    base_w = size * 0.16
    draw.line(
        [(cx - base_w, stand_bottom), (cx + base_w, stand_bottom)],
        fill="white", width=line_width,
    )

    return img


def main() -> None:
    sizes = [16, 32, 48, 64, 128, 256]
    images = [create_microphone_icon(s) for s in sizes]

    os.makedirs("assets", exist_ok=True)
    output_path = os.path.join("assets", "speech2txt.ico")

    # Save as multi-resolution .ico (first image is the "main" one)
    images[-1].save(
        output_path,
        format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=images[:-1],
    )
    print(f"Icon saved to {output_path}")
    print(f"Resolutions: {', '.join(f'{s}x{s}' for s in sizes)}")


if __name__ == "__main__":
    main()
