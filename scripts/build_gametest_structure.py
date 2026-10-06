#!/usr/bin/env python3
"""Write the .mcstructure a GameTest runs inside.

Bedrock runs every GameTest inside a structure it copies into the world. When a
test names no structure, the framework looks for
``structures/<namespace>/<testName>.mcstructure`` -- here
``tests/gametest/behavior_pack/structures/basgiath/dragon_rides.mcstructure``.

The file is little-endian NBT, uncompressed, and, unlike level.dat, has no
8-byte header: the first byte is the root TAG_Compound. The root is unnamed.
The pad is a 5x4x5 box with one stone floor layer; the dragon spawns at
relative (2, 2, 2) above it.

The encoder is local to this file on purpose. It writes lists of compounds,
which ``scripts/nbt_le.py`` (used for level.dat) does not support, and it keeps
that shared module unchanged.
"""

from __future__ import annotations

import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tests/gametest/behavior_pack/structures/basgiath/dragon_rides.mcstructure"

SIZE = (5, 4, 5)
# The block data version stored for the palette entry. Stone has not changed in
# years, so any recent value upgrades cleanly.
BLOCK_VERSION = 17959425

TAG_INT = 3
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_END = 0


def _string(text: str) -> bytes:
    data = text.encode("utf-8")
    return struct.pack("<H", len(data)) + data


def _tag(tag_id: int, name: str, payload: bytes) -> bytes:
    return struct.pack("<B", tag_id) + _string(name) + payload


def _compound(name: str, body: bytes) -> bytes:
    return _tag(TAG_COMPOUND, name, body + struct.pack("<B", TAG_END))


def _compound_body(body: bytes) -> bytes:
    """A compound with no tag id and no name, as list elements are stored."""
    return body + struct.pack("<B", TAG_END)


def _int_list(values: list[int]) -> bytes:
    return struct.pack("<bi", TAG_INT, len(values)) + b"".join(
        struct.pack("<i", value) for value in values
    )


def _list_of(element_tag: int, payloads: list[bytes]) -> bytes:
    return struct.pack("<bi", element_tag, len(payloads)) + b"".join(payloads)


def build() -> Path:
    sx, sy, sz = SIZE
    # Index order is X, then Y, then Z: i = sz*sy*X + sz*Y + Z.
    layer0 = [0 if y == 0 else -1 for x in range(sx) for y in range(sy) for z in range(sz)]
    layer1 = [-1] * (sx * sy * sz)

    stone = _compound_body(
        _tag(TAG_STRING, "name", _string("minecraft:stone"))
        + _compound("states", b"")
        + _tag(TAG_INT, "version", struct.pack("<i", BLOCK_VERSION))
    )
    block_palette = _tag(TAG_LIST, "block_palette", _list_of(TAG_COMPOUND, [stone]))
    default = _compound(
        "default", block_palette + _compound("block_position_data", b"")
    )
    palette = _compound("palette", default)

    block_indices = _tag(
        TAG_LIST, "block_indices", _list_of(TAG_LIST, [_int_list(layer0), _int_list(layer1)])
    )
    entities = _tag(TAG_LIST, "entities", _list_of(TAG_COMPOUND, []))
    structure = _compound("structure", block_indices + entities + palette)

    root_body = (
        _tag(TAG_INT, "format_version", struct.pack("<i", 1))
        + _tag(TAG_LIST, "size", _int_list(list(SIZE)))
        + _tag(TAG_LIST, "structure_world_origin", _int_list([0, 0, 0]))
        + structure
    )
    blob = struct.pack("<B", TAG_COMPOUND) + _string("") + root_body + struct.pack("<B", TAG_END)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(blob)
    return OUT


def main() -> None:
    path = build()
    print(f"wrote {path} ({path.stat().st_size} bytes, size={SIZE})")


if __name__ == "__main__":
    main()
