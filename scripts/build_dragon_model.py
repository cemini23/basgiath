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
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO_PATH = os.path.join(ROOT, "addon/resource_pack/models/entity/dragon.geo.json")
TEX_PATH = os.path.join(ROOT, "addon/resource_pack/textures/entity/dragon.png")

TEX_W = TEX_H = 128
GEOMETRY_ID = "geometry.dragon_rider"

# name -> (parent or None, pivot)
BONES = [
    ("body", None, [0, 24, 0]),
    ("neck", "body", [0, 30, -30]),
    ("head", "neck", [0, 32, -44]),
    ("wing_left", "body", [13, 33, -14]),
    ("wing_left_mid", "wing_left", [35, 31, -10]),
    ("wing_left_tip", "wing_left_mid", [61, 31, -8]),
    ("wing_right", "body", [-13, 33, -14]),
    ("wing_right_mid", "wing_right", [-35, 31, -10]),
    ("wing_right_tip", "wing_right_mid", [-61, 31, -8]),
    ("tail", "body", [0, 24, 18]),
    ("tail_2", "tail", [0, 24, 48]),
    ("tail_3", "tail_2", [0, 24, 68]),
    ("leg_front_left", "body", [10, 16, -18]),
    ("leg_front_right", "body", [-10, 16, -18]),
    ("leg_back_left", "body", [10, 16, 14]),
    ("leg_back_right", "body", [-10, 16, 14]),
]

# bone, origin, size, material, alt_material (for east/west faces or None)
CUBES = [
    ("body", [-14, 14, -30], [28, 19, 34], "back", None),
    ("body", [-12, 12, 4], [24, 16, 26], "back", None),
    ("neck", [-5, 26, -44], [10, 12, 18], "back", None),
    ("head", [-7, 24, -62], [14, 14, 18], "head", "eye"),
    ("head", [-4, 26, -74], [8, 8, 12], "head", None),
    ("head", [-4, 20, -72], [8, 4, 10], "jaw", None),
    ("head", [4, 36, -58], [3, 9, 3], "bone", None),
    ("head", [-7, 36, -58], [3, 9, 3], "bone", None),
    ("wing_left", [13, 31, -18], [22, 3, 16], "wing", None),
    ("wing_left_mid", [35, 30, -14], [26, 2, 12], "membrane", None),
    ("wing_left_tip", [61, 30, -12], [30, 2, 10], "membrane", None),
    ("wing_right", [-35, 31, -18], [22, 3, 16], "wing", None),
    ("wing_right_mid", [-61, 30, -14], [26, 2, 12], "membrane", None),
    ("wing_right_tip", [-91, 30, -12], [30, 2, 10], "membrane", None),
    ("tail", [-5, 20, 26], [10, 10, 22], "back", None),
    ("tail_2", [-4, 21, 48], [8, 8, 20], "back", None),
    ("tail_3", [-3, 22, 68], [6, 6, 18], "back", None),
    ("leg_front_left", [7, 0, -21], [6, 16, 6], "limb", None),
    ("leg_front_right", [-13, 0, -21], [6, 16, 6], "limb", None),
    ("leg_back_left", [7, 0, 11], [6, 16, 6], "limb", None),
    ("leg_back_right", [-13, 0, 11], [6, 16, 6], "limb", None),
]

MATERIALS = {
    "back": (96, 32, 44),
    "head": (112, 44, 52),
    "jaw": (196, 168, 132),
    "bone": (222, 210, 180),
    "wing": (88, 28, 40),
    "membrane": (118, 58, 86),
    "limb": (84, 28, 38),
    "eye": (232, 214, 92),
}


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
    for i, (bone, origin, size, mat, alt) in enumerate(CUBES):
        regions[(i, mat)] = patch_size(size)
        if alt:
            regions[(i, alt)] = patch_size(size)
    placed = pack([(k, w, h) for k, (w, h) in regions.items()])

    bones = {name: {"name": name, "pivot": pivot, "cubes": []} for name, _, pivot in BONES}
    for name, parent, pivot in BONES:
        if parent:
            bones[name]["parent"] = parent

    for i, (bone, origin, size, mat, alt) in enumerate(CUBES):
        w, h, d = size
        base = placed[(i, mat)]
        uv = {
            "north": {"uv": list(base), "uv_size": [w, h]},
            "south": {"uv": list(base), "uv_size": [w, h]},
            "up": {"uv": list(base), "uv_size": [w, d]},
            "down": {"uv": list(base), "uv_size": [w, d]},
        }
        side = placed[(i, alt)] if alt else base
        uv["east"] = {"uv": list(side), "uv_size": [d, h]}
        uv["west"] = {"uv": list(side), "uv_size": [d, h]}
        bones[bone]["cubes"].append({"origin": list(origin), "size": list(size), "uv": uv})

    geometry = {
        "format_version": "1.12.0",
        "minecraft:geometry": [
            {
                "description": {
                    "identifier": GEOMETRY_ID,
                    "texture_width": TEX_W,
                    "texture_height": TEX_H,
                    "visible_bounds_width": 10,
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


def membrane_fill(draw, box, color):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=color)
    dark = tuple(max(0, c - 40) for c in color)
    span = max(1, (x1 - x0))
    for k in range(0, span, 6):
        draw.line([x0 + k, y0, x0 + k + 12, y1], fill=dark, width=1)
    draw.rectangle(box, outline=dark)


def paint(placed, regions):
    img = Image.new("RGB", (TEX_W, TEX_H), (24, 16, 20))
    d = ImageDraw.Draw(img)
    for (i, mat), (w, h) in regions.items():
        x, y = placed[(i, mat)]
        box = (x, y, x + w - 1, y + h - 1)
        color = MATERIALS[mat]
        if mat == "membrane":
            membrane_fill(d, box, color)
        elif mat == "eye":
            d.rectangle(box, fill=MATERIALS["head"])
            cx, cy = x + w // 2, y + h // 2
            d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=color)
            d.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=(20, 12, 12))
        else:
            scale_fill(d, box, color)
    return img


def main():
    geometry, placed, regions = build_geometry()
    os.makedirs(os.path.dirname(GEO_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(TEX_PATH), exist_ok=True)
    with open(GEO_PATH, "w", encoding="utf-8") as fh:
        json.dump(geometry, fh, indent=2)
        fh.write("\n")
    paint(placed, regions).save(TEX_PATH)
    print(f"wrote {GEO_PATH}")
    print(f"wrote {TEX_PATH} ({TEX_W}x{TEX_H})")
    print(f"bones: {len(BONES)}  cubes: {len(CUBES)}")


if __name__ == "__main__":
    main()
