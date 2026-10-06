#!/usr/bin/env python3
"""Draw the academy currency: three coin tiers and a bank note.

16x16, like a vanilla item icon. Everything is drawn from scratch here, so the
assets are original and regenerate byte-for-byte from this file. The shapes are
deliberately plain: a circle for a coin, a rectangle for a note, so they read at
icon size.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "addon/resource_pack/textures/item"

SIZE = 16
TRANSPARENT = (0, 0, 0, 0)

# (name, face, rim, shine)
COINS = (
    ("copper_mark", (176, 106, 65, 255), (120, 68, 40, 255), (222, 158, 116, 255)),
    ("silver_mark", (188, 194, 200, 255), (124, 132, 140, 255), (238, 242, 246, 255)),
    ("gold_mark", (226, 188, 66, 255), (162, 128, 34, 255), (250, 232, 152, 255)),
)

# (name, paper, border, seal)
NOTE = ("bank_note", (196, 206, 178, 255), (86, 98, 78, 255), (150, 66, 58, 255))


def coin(face, rim, shine) -> Image.Image:
    image = Image.new("RGBA", (SIZE, SIZE), TRANSPARENT)
    pixels = image.load()
    centre = (SIZE - 1) / 2
    radius = SIZE / 2 - 1
    for y in range(SIZE):
        for x in range(SIZE):
            distance = ((x - centre) ** 2 + (y - centre) ** 2) ** 0.5
            if distance > radius:
                continue
            if distance > radius - 1.2:
                pixels[x, y] = rim
            elif (x - 5) ** 2 + (y - 5) ** 2 <= 3:
                pixels[x, y] = shine
            else:
                pixels[x, y] = face
    return image


def note(paper, border, seal) -> Image.Image:
    image = Image.new("RGBA", (SIZE, SIZE), TRANSPARENT)
    pixels = image.load()
    for y in range(3, SIZE - 3):
        for x in range(1, SIZE - 1):
            edge = y in (3, SIZE - 4) or x in (1, SIZE - 2)
            pixels[x, y] = border if edge else paper
    # A seal, so the note does not read as a plain card.
    for y in range(7, 11):
        for x in range(6, 10):
            if (x - 7.5) ** 2 + (y - 8.5) ** 2 <= 3.5:
                pixels[x, y] = seal
    return image


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    written = []
    for name, face, rim, shine in COINS:
        path = OUT / f"{name}.png"
        coin(face, rim, shine).save(path)
        written.append(path)
    name, paper, border, seal = NOTE
    path = OUT / f"{name}.png"
    note(paper, border, seal).save(path)
    written.append(path)
    for path in written:
        print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
