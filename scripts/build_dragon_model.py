#!/usr/bin/env python3
"""Generate the dragon model and its texture.

Run from the repo root:

    python3 scripts/build_dragon_model.py

Writes:
    addon/resource_pack/models/entity/dragon.geo.json
    addon/resource_pack/textures/entity/dragon.png

The model keeps the bone names the animations depend on:
body, head, wing_left, wing_right, tail.
"""

from __future__ import annotations

import json
import os
import struct
import zlib

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO_PATH = os.path.join(ROOT, "addon/resource_pack/models/entity/dragon.geo.json")
TEX_PATH = os.path.join(ROOT, "addon/resource_pack/textures/entity/dragon.png")

TEX_W = TEX_H = 128
GEOMETRY_ID = "geometry.dragon_rider"

# name -> (parent or None, pivot)
BONES = [
    ("body", None, [0, 24, 0]),
    ("neck", "body", [0, 30, -26]),
    ("head", "neck", [0, 34, -42]),
    ("jaw", "head", [0, 28, -56]),
    ("wing_left", "body", [12, 32, -10]),
    ("wing_left_mid", "wing_left", [34, 32, -10]),
    ("wing_left_tip", "wing_left_mid", [58, 32, -10]),
    ("wing_right", "body", [-12, 32, -10]),
    ("wing_right_mid", "wing_right", [-34, 32, -10]),
    ("wing_right_tip", "wing_right_mid", [-58, 32, -10]),
    ("tail", "body", [0, 22, 20]),
    ("tail_2", "tail", [0, 21, 36]),
    ("tail_3", "tail_2", [0, 20, 50]),
    ("tail_4", "tail_3", [0, 19, 62]),
    ("leg_front_left", "body", [8, 16, -16]),
    ("leg_front_right", "body", [-8, 16, -16]),
    ("leg_back_left", "body", [8, 16, 8]),
    ("leg_back_right", "body", [-8, 16, 8]),
]

# bone, origin, size, material, side_material, down_material
CUBES = [
    # chest and hips. Down faces are sand. Top of the chest is Y=32. Z covers 0.
    ("body", [-12, 16, -28], [24, 16, 32], "scale", None, "belly"),
    ("body", [-10, 16, 2], [20, 14, 22], "scale", None, "belly"),
    # spine ridges
    ("body", [-2, 32, -20], [4, 3, 6], "scale", None, None),
    ("body", [-2, 32, -8], [4, 3, 6], "scale", None, None),
    ("body", [-1, 30, 6], [3, 3, 6], "scale", None, None),
    ("body", [-1, 30, 14], [3, 2, 5], "scale", None, None),
    # neck
    ("neck", [-5, 24, -42], [10, 12, 18], "scale", None, None),
    # skull. East and west use the eye material. Snout stays on the head.
    ("head", [-7, 28, -58], [14, 12, 16], "scale", "eye", None),
    ("head", [-4, 28, -70], [8, 7, 14], "scale", None, None),
    # two short brow horns and two swept horns (two cubes each), bone colored
    ("head", [-7, 40, -54], [3, 4, 3], "bone", None, None),
    ("head", [4, 40, -54], [3, 4, 3], "bone", None, None),
    ("head", [-8, 38, -50], [3, 8, 3], "bone", None, None),
    ("head", [-8, 45, -46], [2, 6, 3], "bone", None, None),
    ("head", [5, 38, -50], [3, 8, 3], "bone", None, None),
    ("head", [6, 45, -46], [2, 6, 3], "bone", None, None),
    # lower jaw is a child bone, not a head cube
    ("jaw", [-4, 24, -68], [8, 4, 12], "jaw", None, None),
    # left wing: arm from X=12, 22 long; mid joint at X=34; tip joint at X=58
    ("wing_left", [12, 30, -14], [22, 4, 8], "scale", None, None),
    ("wing_left_mid", [34, 30, -13], [24, 3, 6], "bone", None, None),
    ("wing_left_mid", [34, 29, -10], [24, 1, 22], "membrane", None, None),
    ("wing_left_tip", [58, 30, -12], [22, 2, 4], "bone", None, None),
    ("wing_left_tip", [58, 29, -8], [24, 1, 16], "membrane", None, None),
    # right wing is the X mirror. Pivot X is negative. Do not invert the wing lengths.
    ("wing_right", [-34, 30, -14], [22, 4, 8], "scale", None, None),
    ("wing_right_mid", [-58, 30, -13], [24, 3, 6], "bone", None, None),
    ("wing_right_mid", [-58, 29, -10], [24, 1, 22], "membrane", None, None),
    ("wing_right_tip", [-80, 30, -12], [22, 2, 4], "bone", None, None),
    ("wing_right_tip", [-82, 29, -8], [24, 1, 16], "membrane", None, None),
    # tail root, then three child segments tapering toward +Z, plus a flat spade
    ("tail", [-6, 17, 20], [12, 8, 16], "scale", None, None),
    ("tail_2", [-5, 17, 36], [10, 7, 14], "scale", None, None),
    ("tail_3", [-4, 17, 50], [8, 6, 12], "scale", None, None),
    ("tail_4", [-3, 17, 62], [6, 5, 10], "scale", None, None),
    ("tail_4", [-9, 20, 70], [18, 1, 14], "scale", None, None),
    # four legs. Each has a thigh, a shin, and a foot. Feet sit on Y=0.
    ("leg_front_left", [5, 8, -19], [6, 8, 6], "scale", None, None),
    ("leg_front_left", [6, 2, -18], [5, 6, 5], "scale", None, None),
    ("leg_front_left", [5, 0, -23], [6, 2, 8], "scale", None, None),
    ("leg_front_left", [5, 0, -26], [2, 2, 3], "bone", None, None),
    ("leg_front_left", [9, 0, -26], [2, 2, 3], "bone", None, None),
    ("leg_front_right", [-11, 8, -19], [6, 8, 6], "scale", None, None),
    ("leg_front_right", [-11, 2, -18], [5, 6, 5], "scale", None, None),
    ("leg_front_right", [-11, 0, -23], [6, 2, 8], "scale", None, None),
    ("leg_front_right", [-11, 0, -26], [2, 2, 3], "bone", None, None),
    ("leg_front_right", [-7, 0, -26], [2, 2, 3], "bone", None, None),
    ("leg_back_left", [5, 8, 5], [6, 8, 6], "scale", None, None),
    ("leg_back_left", [6, 2, 6], [5, 6, 5], "scale", None, None),
    ("leg_back_left", [5, 0, 4], [6, 2, 9], "scale", None, None),
    ("leg_back_left", [5, 0, 1], [2, 2, 3], "bone", None, None),
    ("leg_back_left", [9, 0, 1], [2, 2, 3], "bone", None, None),
    ("leg_back_right", [-11, 8, 5], [6, 8, 6], "scale", None, None),
    ("leg_back_right", [-11, 2, 6], [5, 6, 5], "scale", None, None),
    ("leg_back_right", [-11, 0, 4], [6, 2, 9], "scale", None, None),
    ("leg_back_right", [-11, 0, 1], [2, 2, 3], "bone", None, None),
    ("leg_back_right", [-7, 0, 1], [2, 2, 3], "bone", None, None),
]

MATERIALS = {
    "scale": (52, 22, 30),
    "jaw": (68, 32, 40),
    "belly": (216, 190, 146),
    "membrane": (116, 52, 82),
    "eye": (230, 170, 46),
    "bone": (228, 212, 178),
}
PUPIL = (18, 10, 12)


def patch_size(size):
    w, h, d = size
    return max(w, d), max(h, d)


def pack(pairs):
    """Shelf-pack (key, w, h) into TEX_W x TEX_H. Returns key -> (x, y)."""
    items = sorted(pairs, key=lambda p: -p[2])
    placed, x, y, shelf = {}, 0, 0, 0
    for key, w, h in items:
        if x + w > TEX_W:
            x, y, shelf = 0, y + shelf, 0
        if y + h > TEX_H:
            raise RuntimeError(f"atlas full placing {key} ({w}x{h})")
        placed[key] = (x, y)
        x += w
        shelf = max(shelf, h)
    return placed


def build_geometry():
    regions = {}
    for i, (bone, origin, size, mat, side, down) in enumerate(CUBES):
        regions[(i, mat)] = patch_size(size)
        if side:
            regions[(i, side)] = patch_size(size)
        if down:
            regions[(i, down)] = patch_size(size)
    placed = pack([(k, w, h) for k, (w, h) in regions.items()])

    bones = {name: {"name": name, "pivot": pivot, "cubes": []} for name, _, pivot in BONES}
    for name, parent, pivot in BONES:
        if parent:
            bones[name]["parent"] = parent

    for i, (bone, origin, size, mat, side, down) in enumerate(CUBES):
        w, h, d = size
        base = placed[(i, mat)]
        uv = {
            "north": {"uv": list(base), "uv_size": [w, h]},
            "south": {"uv": list(base), "uv_size": [w, h]},
            "up": {"uv": list(base), "uv_size": [w, d]},
        }
        if down:
            uv["down"] = {"uv": list(placed[(i, down)]), "uv_size": [w, d]}
        else:
            uv["down"] = {"uv": list(base), "uv_size": [w, d]}
        side_uv = placed[(i, side)] if side else base
        uv["east"] = {"uv": list(side_uv), "uv_size": [d, h]}
        uv["west"] = {"uv": list(side_uv), "uv_size": [d, h]}
        bones[bone]["cubes"].append({"origin": list(origin), "size": list(size), "uv": uv})

    geometry = {
        "format_version": "1.12.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": GEOMETRY_ID,
                    "texture_width": TEX_W,
                    "texture_height": TEX_H,
                    "visible_bounds_width": 14,
                    "visible_bounds_height": 5,
                    "visible_bounds_offset": [0, 2, 0],
                },
                "bones": [bones[name] for name, _, _ in BONES],
            }
        ],
    }
    return geometry, placed, regions


def scale_fill(draw, box, color, cell=5):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=color)
    dark = tuple(max(0, c - 34) for c in color)
    light = tuple(min(255, c + 26) for c in color)
    for cy in range(y0, y1, cell):
        for cx in range(x0, x1, cell):
            draw.arc([cx, cy, cx + cell - 1, cy + cell - 1], 180, 360, fill=dark)
            draw.line([cx, cy + cell - 2, cx + cell - 1, cy + cell - 2], fill=light, width=1)


def belly_fill(draw, box, color):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=color)
    light = tuple(min(255, c + 28) for c in color)
    for cy in range(y0, y1 + 1, 4):
        draw.line([x0, cy, x1, cy], fill=light, width=1)


def membrane_fill(draw, box, color):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=color)
    dark = tuple(max(0, c - 40) for c in color)
    span = max(1, (x1 - x0))
    for k in range(0, span, 6):
        draw.line([x0 + k, y0, x0 + k + 12, y1], fill=dark, width=1)
    draw.rectangle(box, outline=dark)


def bone_fill(draw, box, color):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=color)
    edge = tuple(max(0, c - 36) for c in color)
    draw.rectangle(box, outline=edge)


def paint(placed, regions):
    img = Image.new("RGB", (TEX_W, TEX_H), (24, 16, 20))
    d = ImageDraw.Draw(img)
    for (i, mat), (w, h) in regions.items():
        x, y = placed[(i, mat)]
        box = (x, y, x + w - 1, y + h - 1)
        color = MATERIALS[mat]
        if mat == "membrane":
            membrane_fill(d, box, color)
        elif mat == "belly":
            belly_fill(d, box, color)
        elif mat == "bone":
            bone_fill(d, box, color)
        elif mat == "eye":
            d.rectangle(box, fill=MATERIALS["scale"])
            _, _, size, _, _, _ = CUBES[i]
            dw, dh = size[2], size[1]
            cx = x + max(2, dw // 3)
            cy = y + max(2, dh // 3)
            r = max(2, min(dw, dh) // 3)
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
            pr = max(1, r // 2)
            d.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=PUPIL)
        else:
            scale_fill(d, box, color)
    return img


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(tag + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)


def save_png(img, path):
    """Write one stored-block PNG. Pillow's encoder is not stable across machines."""
    rgb = img.convert("RGB")
    width, height = rgb.size
    raw_rows = rgb.tobytes()
    stride = width * 3
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw += raw_rows[y * stride : (y + 1) * stride]
    uncompressed = bytes(raw)
    if len(uncompressed) > 65535:
        raise RuntimeError("texture is too large for one stored PNG block")
    nlen = (~len(uncompressed)) & 0xFFFF
    stored = b"\x01" + struct.pack("<HH", len(uncompressed), nlen) + uncompressed
    adler = zlib.adler32(uncompressed) & 0xFFFFFFFF
    zlib_stream = b"\x78\x01" + stored + struct.pack(">I", adler)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _png_chunk(b"IHDR", ihdr)
    png += _png_chunk(b"IDAT", zlib_stream)
    png += _png_chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


def main():
    geometry, placed, regions = build_geometry()
    os.makedirs(os.path.dirname(GEO_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(TEX_PATH), exist_ok=True)
    with open(GEO_PATH, "w", encoding="utf-8") as fh:
        json.dump(geometry, fh, indent=2)
        fh.write("\n")
    save_png(paint(placed, regions), TEX_PATH)
    print(f"wrote {GEO_PATH}")
    print(f"wrote {TEX_PATH} ({TEX_W}x{TEX_H})")
    print(f"bones: {len(BONES)}  cubes: {len(CUBES)}")


if __name__ == "__main__":
    main()
