#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from PIL import Image


INPUT_PATH = Path("/home/user/attachments/rs.jpeg")
OUTPUT_PATH = Path("/home/user/output/rs_green.png")


def shift_to_green(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    out = Image.new("RGB", rgb.size)

    src = rgb.load()
    dst = out.load()
    width, height = rgb.size

    for y in range(height):
        for x in range(width):
            r, g, b = src[x, y]
            max_c = max(r, g, b)

            # Preserve the black background and near-black shadow detail.
            if max_c < 10:
                dst[x, y] = (r, g, b)
                continue

            # Rebuild the palette around green while preserving brightness.
            green = max_c
            red = min(int(max_c * 0.78), int(g * 0.80 + r * 0.12 + b * 0.08))
            blue = min(int(max_c * 0.74), int(g * 0.60 + b * 0.22 + r * 0.06))

            # Keep specular highlights metallic instead of over-saturating them.
            if max_c > 215:
                lift = max_c - 215
                red = min(255, red + lift)
                blue = min(255, blue + lift)

            dst[x, y] = (red, green, blue)

    return out


def main() -> None:
    image = Image.open(INPUT_PATH)
    transformed = shift_to_green(image)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    transformed.save(OUTPUT_PATH, format="PNG", optimize=True)
    print(f"saved {OUTPUT_PATH}")
    print(f"size={transformed.size} mode={transformed.mode}")


if __name__ == "__main__":
    main()
