#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def lerp(a: int, b: int, t: float) -> int:
    return round(a + (b - a) * t)


def blend(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(lerp(a, b, t) for a, b in zip(c1, c2))


def remap_pixel(r: int, g: int, b: int) -> tuple[int, int, int]:
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    if lum < 5:
        return (0, 0, 0)

    low = (4, 10, 34)
    mid = (44, 96, 210)
    high = (228, 242, 255)

    t = lum / 255.0
    if t < 0.62:
        mapped = blend(low, mid, t / 0.62)
    else:
        mapped = blend(mid, high, (t - 0.62) / 0.38)

    chroma = max(r, g, b) - min(r, g, b)
    preserve = min(0.28, chroma / 255.0 * 0.22)
    return blend(mapped, (r, g, b), preserve)


def recolor_image(source: Path, target: Path) -> None:
    image = Image.open(source).convert("RGB")
    px = image.load()
    width, height = image.size
    recolored = [remap_pixel(*px[x, y]) for y in range(height) for x in range(width)]

    out = Image.new("RGB", image.size)
    out.putdata(recolored)
    out.save(target, quality=95)


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a blue variant of an image.")
    parser.add_argument("source", type=Path)
    parser.add_argument("target", type=Path)
    args = parser.parse_args()

    args.target.parent.mkdir(parents=True, exist_ok=True)
    recolor_image(args.source, args.target)


if __name__ == "__main__":
    main()
