#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageOps


def build_mask(gray: Image.Image, low: int = 10, high: int = 42) -> Image.Image:
    """Create a soft mask that keeps near-black background pixels untouched."""
    lut = []
    span = max(high - low, 1)
    for value in range(256):
        if value <= low:
            lut.append(0)
        elif value >= high:
            lut.append(255)
        else:
            lut.append(int((value - low) * 255 / span))
    return gray.point(lut, mode="L")


def recolor_to_red(src: Path, dst: Path) -> None:
    img = Image.open(src).convert("RGB")
    gray = ImageOps.grayscale(img)

    # Preserve the original shading and highlights by tinting the luminance map.
    colorized = ImageOps.colorize(
        gray,
        black=(0, 0, 0),
        mid=(185, 18, 18),
        white=(255, 242, 242),
        midpoint=135,
    )

    # Add a small amount of the original red channel back in to retain local nuance.
    red_boost = Image.merge("RGB", (img.getchannel("R"), gray, gray))
    red_boost = Image.blend(colorized, red_boost, 0.12)

    mask = build_mask(gray)
    result = Image.composite(red_boost, img, mask)

    dst.parent.mkdir(parents=True, exist_ok=True)
    result.save(dst)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a red-toned recolor of an image.")
    parser.add_argument("src", type=Path)
    parser.add_argument("dst", type=Path)
    args = parser.parse_args()
    recolor_to_red(args.src, args.dst)


if __name__ == "__main__":
    main()
