#!/usr/bin/env python3
"""Little-endian uncompressed NBT for Bedrock level.dat (no gzip)."""

from __future__ import annotations

import struct
from typing import Any, Sequence


TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11


class Byte:
    """Force TAG_Byte."""

    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value = int(value)


class Long:
    """Force TAG_Long (signed int64)."""

    __slots__ = ("value",)

    def __init__(self, value: int) -> None:
        self.value = int(value)


class Float:
    """Force TAG_Float (float32)."""

    __slots__ = ("value",)

    def __init__(self, value: float) -> None:
        self.value = float(value)


class IntList:
    """Force TAG_List of TAG_Int."""

    __slots__ = ("values",)

    def __init__(self, values: Sequence[int]) -> None:
        self.values = [int(v) for v in values]


def _write_string(buf: bytearray, text: str) -> None:
    data = text.encode("utf-8")
    buf += struct.pack("<H", len(data))
    buf += data


def _tag_type(value: Any) -> int:
    if isinstance(value, Byte):
        return TAG_BYTE
    if isinstance(value, Long):
        return TAG_LONG
    if isinstance(value, Float):
        return TAG_FLOAT
    if isinstance(value, IntList):
        return TAG_LIST
    if isinstance(value, bool):
        return TAG_BYTE
    if isinstance(value, int):
        return TAG_INT
    if isinstance(value, float):
        return TAG_FLOAT
    if isinstance(value, str):
        return TAG_STRING
    if isinstance(value, list):
        return TAG_LIST
    if isinstance(value, dict):
        return TAG_COMPOUND
    raise TypeError(f"unsupported NBT value: {type(value).__name__}")


def _encode_payload(buf: bytearray, value: Any) -> None:
    if isinstance(value, Byte):
        buf += struct.pack("<b", value.value)
        return
    if isinstance(value, Long):
        buf += struct.pack("<q", value.value)
        return
    if isinstance(value, Float):
        buf += struct.pack("<f", value.value)
        return
    if isinstance(value, IntList):
        buf += struct.pack("<bi", TAG_INT, len(value.values))
        for item in value.values:
            buf += struct.pack("<i", item)
        return
    if isinstance(value, bool):
        buf += struct.pack("<b", 1 if value else 0)
        return
    if isinstance(value, int):
        buf += struct.pack("<i", value)
        return
    if isinstance(value, float):
        buf += struct.pack("<f", value)
        return
    if isinstance(value, str):
        _write_string(buf, value)
        return
    if isinstance(value, list):
        if not all(isinstance(item, int) and not isinstance(item, bool) for item in value):
            raise TypeError(f"unsupported list elements: {value!r}")
        buf += struct.pack("<bi", TAG_INT, len(value))
        for item in value:
            buf += struct.pack("<i", item)
        return
    if isinstance(value, dict):
        _encode_compound_body(buf, value)
        return
    raise TypeError(f"unsupported NBT value: {type(value).__name__}")


def _encode_compound_body(buf: bytearray, mapping: dict) -> None:
    for name, value in mapping.items():
        buf += struct.pack("<B", _tag_type(value))
        _write_string(buf, name)
        _encode_payload(buf, value)
    buf += struct.pack("<B", TAG_END)


def encode_level_dat(root_dict: dict) -> bytes:
    """Return Bedrock level.dat bytes: version 10 header + empty-named root compound."""
    payload = bytearray()
    payload += struct.pack("<B", TAG_COMPOUND)
    _write_string(payload, "")
    _encode_compound_body(payload, root_dict)
    return struct.pack("<II", 10, len(payload)) + bytes(payload)


def _read_string(data: bytes, offset: int) -> tuple[str, int]:
    (length,) = struct.unpack_from("<H", data, offset)
    offset += 2
    text = data[offset : offset + length].decode("utf-8")
    return text, offset + length


def _decode_payload(data: bytes, offset: int, tag_type: int) -> tuple[Any, int]:
    if tag_type == TAG_BYTE:
        (value,) = struct.unpack_from("<b", data, offset)
        return int(value), offset + 1
    if tag_type == TAG_SHORT:
        (value,) = struct.unpack_from("<h", data, offset)
        return int(value), offset + 2
    if tag_type == TAG_INT:
        (value,) = struct.unpack_from("<i", data, offset)
        return int(value), offset + 4
    if tag_type == TAG_LONG:
        (value,) = struct.unpack_from("<q", data, offset)
        return int(value), offset + 8
    if tag_type == TAG_FLOAT:
        (value,) = struct.unpack_from("<f", data, offset)
        return float(value), offset + 4
    if tag_type == TAG_DOUBLE:
        (value,) = struct.unpack_from("<d", data, offset)
        return float(value), offset + 8
    if tag_type == TAG_STRING:
        return _read_string(data, offset)
    if tag_type == TAG_LIST:
        elem_type, count = struct.unpack_from("<bi", data, offset)
        offset += 5
        items = []
        for _ in range(count):
            item, offset = _decode_payload(data, offset, elem_type)
            items.append(item)
        return items, offset
    if tag_type == TAG_COMPOUND:
        return _decode_compound_body(data, offset)
    if tag_type == TAG_BYTE_ARRAY:
        (count,) = struct.unpack_from("<i", data, offset)
        offset += 4
        return list(data[offset : offset + count]), offset + count
    if tag_type == TAG_INT_ARRAY:
        (count,) = struct.unpack_from("<i", data, offset)
        offset += 4
        items = list(struct.unpack_from(f"<{count}i", data, offset))
        return items, offset + 4 * count
    raise ValueError(f"unsupported tag type: {tag_type}")


def _decode_compound_body(data: bytes, offset: int) -> tuple[dict, int]:
    result: dict[str, Any] = {}
    while True:
        (tag_type,) = struct.unpack_from("<B", data, offset)
        offset += 1
        if tag_type == TAG_END:
            return result, offset
        name, offset = _read_string(data, offset)
        value, offset = _decode_payload(data, offset, tag_type)
        result[name] = value


def decode_level_dat(blob: bytes) -> dict:
    """Parse Bedrock level.dat into plain Python values."""
    if len(blob) < 8:
        raise ValueError("level.dat too short")
    _storage_version, payload_length = struct.unpack_from("<II", blob, 0)
    payload = blob[8 : 8 + payload_length]
    if len(payload) != payload_length:
        raise ValueError("truncated level.dat payload")
    (tag_type,) = struct.unpack_from("<B", payload, 0)
    if tag_type != TAG_COMPOUND:
        raise ValueError(f"expected root compound, got {tag_type}")
    name, offset = _read_string(payload, 1)
    if name != "":
        raise ValueError("root compound name must be empty")
    root, _offset = _decode_compound_body(payload, offset)
    return root
