#!/usr/bin/env python3
"""Read, and append to, the Bedrock world database under ``db/``.

A Bedrock world keeps its state in a LevelDB database. ``CURRENT`` names the
active ``MANIFEST-*``; the manifest lists the live ``*.ldb`` table files and
the current journal number; ``*.log`` hold writes that are not yet in a table.
Mojang's fork replaces Snappy with zlib -- both the table blocks and the
stored values -- so stock LevelDB tools cannot open it.

This module is the offline half of the bench. It can read every live record
(the server is the oracle for the format), and it can append a record to the
journal, so world state can be set or checked without a client.

The NBT payloads are read with ``scripts/nbt_le.py``; this module handles only
the LevelDB framing around them.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

try:  # the NBT payloads are parsed by the sibling module
    from nbt_le import TAG_COMPOUND, _decode_compound_body, _read_string
except ImportError:  # pragma: no cover - only when imported from elsewhere
    TAG_COMPOUND = None

# ------------------------------------------------------------------ varints


def read_varint(data: bytes | bytearray, offset: int) -> tuple[int, int]:
    result = 0
    shift = 0
    while True:
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return result, offset
        shift += 7


def write_varint(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def write_length_prefixed(value: bytes) -> bytes:
    return write_varint(len(value)) + value


# ------------------------------------------------------------- crc32c (Castagnoli)

_CRC32C_TABLE: list[int] = []


def _crc32c_table() -> list[int]:
    if _CRC32C_TABLE:
        return _CRC32C_TABLE
    poly = 0x82F63B78
    for i in range(256):
        crc = i
        for _ in range(8):
            crc = (crc >> 1) ^ poly if crc & 1 else crc >> 1
        _CRC32C_TABLE.append(crc)
    return _CRC32C_TABLE


def crc32c(data: bytes) -> int:
    table = _crc32c_table()
    crc = 0xFFFFFFFF
    for byte in data:
        crc = table[(crc ^ byte) & 0xFF] ^ (crc >> 8)
    return crc ^ 0xFFFFFFFF


def _mask(crc: int) -> int:
    """LevelDB rotates the CRC before storing it."""
    return ((crc >> 15) | (crc << 17)) + 0xA282EAD8 & 0xFFFFFFFF


# ------------------------------------------------------------------- journal

BLOCK_SIZE = 32768
HEADER_SIZE = 7  # crc(4) + length(2) + type(1)

FULL, FIRST, MIDDLE, LAST = 1, 2, 3, 4


def journal_records(data: bytes) -> list[bytes]:
    """Assemble the logical records from a LevelDB log file."""
    records: list[bytes] = []
    pending = bytearray()
    offset = 0
    while offset < len(data):
        block_left = BLOCK_SIZE - (offset % BLOCK_SIZE)
        if block_left < HEADER_SIZE:
            offset += block_left
            continue
        header = data[offset : offset + HEADER_SIZE]
        if len(header) < HEADER_SIZE:
            break
        _crc, length, rtype = struct.unpack("<IHB", header)
        offset += HEADER_SIZE
        chunk = data[offset : offset + length]
        if len(chunk) < length:
            break
        offset += length
        if rtype == FULL:
            records.append(bytes(chunk))
        elif rtype == FIRST:
            pending = bytearray(chunk)
        elif rtype == MIDDLE:
            pending += chunk
        elif rtype == LAST:
            pending += chunk
            records.append(bytes(pending))
            pending = bytearray()
    return records


def parse_write_batch(payload: bytes) -> list[tuple[int, str, bytes | None]]:
    """Decode a WriteBatch into (sequence, key, value) rows. A None value is a
    deletion."""
    offset = 0
    sequence, offset = struct.unpack_from("<Q", payload, offset)[0], offset + 8
    count, offset = struct.unpack_from("<I", payload, offset)[0], offset + 4
    rows = []
    for _ in range(count):
        kind = payload[offset]
        offset += 1
        key_len, offset = read_varint(payload, offset)
        key = payload[offset : offset + key_len].decode("latin-1")
        offset += key_len
        value = None
        if kind == 1:  # kTypeValue
            value_len, offset = read_varint(payload, offset)
            value = payload[offset : offset + value_len]
            offset += value_len
        rows.append((sequence, key, value))
        sequence += 1
    return rows


def build_write_batch(sequence: int, key: str, value: bytes | None) -> bytes:
    """Encode one WriteBatch holding a single put (value) or delete (None)."""
    out = bytearray()
    out += struct.pack("<Q", sequence)
    out += struct.pack("<I", 1)
    out.append(0 if value is None else 1)
    out += write_length_prefixed(key.encode("latin-1"))
    if value is not None:
        out += write_length_prefixed(value)
    return bytes(out)


def frame_journal(record: bytes, start_offset: int = 0) -> bytes:
    """Frame one logical record as FULL blocks, or FIRST/MIDDLE/LAST runs.

    LevelDB never lets a fragment span a block boundary, so a long record is
    split across blocks.
    """
    out = bytearray()
    offset = start_offset
    remaining = record
    first = True
    while True:
        block_left = BLOCK_SIZE - (offset % BLOCK_SIZE)
        if block_left < HEADER_SIZE:
            pad = block_left
            out += b"\x00" * pad
            offset += pad
            block_left = BLOCK_SIZE
        room = block_left - HEADER_SIZE
        take = min(room, len(remaining))
        chunk = remaining[:take]
        remaining = remaining[take:]
        if first and not remaining:
            rtype = FULL
        elif first:
            rtype = FIRST
        elif remaining:
            rtype = MIDDLE
        else:
            rtype = LAST
        header = struct.pack("<IHB", _mask(crc32c(chunk)), take, rtype)
        out += header + chunk
        offset += HEADER_SIZE + take
        first = False
        if not remaining:
            return bytes(out)


# -------------------------------------------------------------- table (.ldb)

TABLE_MAGIC = 0xDB4775248B80FB57


def _decompress(raw: bytes, kind: int) -> bytes:
    if kind == 0:
        return raw
    if kind == 2:
        return zlib.decompress(raw)
    raise ValueError(f"unsupported LevelDB block compression type {kind}")


def _block_at(data: bytes, offset: int, size: int) -> bytes:
    body = data[offset : offset + size]
    trailer = data[offset + size : offset + size + 5]
    kind = trailer[0]
    return _decompress(body, kind)


def _decode_block(block: bytes) -> list[tuple[bytes, bytes]]:
    """Decode a prefix-compressed data block into (key, value) entries."""
    if len(block) < 4:
        return []
    num_restarts = struct.unpack_from("<I", block, len(block) - 4)[0]
    end = len(block) - 4 - num_restarts * 4
    offset = 0
    key = b""
    entries = []
    while offset < end:
        shared, offset = read_varint(block, offset)
        non_shared, offset = read_varint(block, offset)
        value_len, offset = read_varint(block, offset)
        key = key[:shared] + block[offset : offset + non_shared]
        offset += non_shared
        value = block[offset : offset + value_len]
        offset += value_len
        entries.append((key, value))
    return entries


def read_table(path: Path) -> list[tuple[bytes, bytes]]:
    """Every (internal key, value) entry in an .ldb file."""
    data = path.read_bytes()
    if len(data) < 48:
        return []
    if struct.unpack_from("<Q", data, len(data) - 8)[0] != TABLE_MAGIC:
        raise ValueError(f"{path} is not a LevelDB table (bad magic)")
    footer = data[-48:-8]
    offset = 0
    _meta_off, offset = read_varint(footer, offset)
    _meta_size, offset = read_varint(footer, offset)
    index_off, offset = read_varint(footer, offset)
    index_size, offset = read_varint(footer, offset)
    index = _decode_block(_block_at(data, index_off, index_size))
    entries: list[tuple[bytes, bytes]] = []
    for _sep, handle in index:
        h_off, h_off_2 = read_varint(handle, 0)
        h_size, _ = read_varint(handle, h_off_2)
        entries.extend(_decode_block(_block_at(data, h_off, h_size)))
    return entries


def split_internal_key(internal: bytes) -> tuple[str, int, int]:
    """An SST key is ``user_key + (sequence<<8 | type)``, little endian."""
    user = internal[:-8]
    packed = struct.unpack("<Q", internal[-8:])[0]
    return user.decode("latin-1"), packed >> 8, packed & 0xFF


# ------------------------------------------------------------------ manifest

# VersionEdit tags
_COMPARATOR, _LOG_NUMBER, _NEXT_FILE, _LAST_SEQUENCE = 1, 2, 3, 4
_COMPACT_POINTER, _DELETED_FILE, _NEW_FILE, _PREV_LOG_NUMBER = 5, 6, 7, 9


def parse_manifest(records: list[bytes]) -> dict:
    """Fold the VersionEdit records into the live file set and counters."""
    live: set[int] = set()
    state = {"log_number": 0, "next_file": 0, "last_sequence": 0}
    for payload in records:
        offset = 0
        while offset < len(payload):
            tag, offset = read_varint(payload, offset)
            if tag == _COMPARATOR:
                length, offset = read_varint(payload, offset)
                offset += length
            elif tag in (_LOG_NUMBER, _NEXT_FILE, _LAST_SEQUENCE, _PREV_LOG_NUMBER):
                value, offset = read_varint(payload, offset)
                if tag == _LOG_NUMBER:
                    state["log_number"] = value
                elif tag == _NEXT_FILE:
                    state["next_file"] = value
                elif tag == _LAST_SEQUENCE:
                    state["last_sequence"] = value
            elif tag == _COMPACT_POINTER:
                length, offset = read_varint(payload, offset)
                offset += length
                _v, offset = read_varint(payload, offset)
            elif tag == _DELETED_FILE:
                _level, offset = read_varint(payload, offset)
                number, offset = read_varint(payload, offset)
                live.discard(number)
            elif tag == _NEW_FILE:
                _level, offset = read_varint(payload, offset)
                number, offset = read_varint(payload, offset)
                _size, offset = read_varint(payload, offset)
                for _ in range(2):  # smallest and largest user keys
                    length, offset = read_varint(payload, offset)
                    offset += length
                live.add(number)
            else:
                raise ValueError(f"unknown VersionEdit tag {tag}")
    return {"live": live, **state}


def read_db(dbdir: Path) -> dict[str, bytes]:
    """Every live key -> value in a Bedrock world database, newest wins."""
    current = (dbdir / "CURRENT").read_text().strip()
    manifest = dbdir / current
    manifest_state = parse_manifest(journal_records(manifest.read_bytes()))

    found: dict[str, tuple[int, bytes]] = {}

    def put(key: str, sequence: int, value: bytes | None) -> None:
        existing = found.get(key)
        if existing is not None and existing[0] >= sequence:
            return
        if value is None:
            found.pop(key, None)
        else:
            found[key] = (sequence, value)

    for number in sorted(manifest_state["live"]):
        path = dbdir / f"{number:06d}.ldb"
        if not path.exists():
            continue
        for internal, value in read_table(path):
            key, sequence, _kind = split_internal_key(internal)
            put(key, sequence, value)

    for log in sorted(dbdir.glob("*.log")):
        number = int(log.stem)
        if number < manifest_state["log_number"]:
            continue
        for payload in journal_records(log.read_bytes()):
            for sequence, key, value in parse_write_batch(payload):
                put(key, sequence, value)

    return {key: value for key, (_, value) in found.items()}


def write_record(dbdir: Path, key: str, value: bytes, sequence: int) -> Path:
    """Append one put to a fresh journal file that recovery will replay.

    LevelDB replays every log numbered at or above the manifest's log_number,
    so a new file with a higher number is picked up on the next open.
    """
    current = (dbdir / "CURRENT").read_text().strip()
    state = parse_manifest(journal_records((dbdir / current).read_bytes()))
    number = max(state["next_file"], max((int(p.stem) for p in dbdir.glob("*.log")), default=0) + 1)
    path = dbdir / f"{number:06d}.log"
    batch = build_write_batch(sequence, key, value)
    path.write_bytes(frame_journal(batch))
    return path


def decode_value(value: bytes) -> tuple[str, dict]:
    """A stored value to (root name, NBT). The value is zlib-compressed NBT."""
    raw = value
    if value[:1] == b"\x78":  # zlib header (0x78 0x01 / 0x9c / 0xda)
        raw = zlib.decompress(value)
    if TAG_COMPOUND is None:
        raise RuntimeError("nbt_le is not importable from here")
    if raw[0] != TAG_COMPOUND:
        raise ValueError(f"stored value is not a compound (tag {raw[0]})")
    name, offset = _read_string(raw, 1)
    body, _ = _decode_compound_body(raw, offset)
    return name, body


def escape_key(key: str) -> str:
    """Render a key readably. Locational keys are binary, not text."""
    return "".join(
        ch if 32 <= ord(ch) < 127 and ch != "\\" else f"\\x{ord(ch):02x}" for ch in key
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dbdir", type=Path)
    parser.add_argument("--keys", action="store_true", help="list keys instead of dumping")
    parser.add_argument("--grep", help="only show keys containing this text")
    parser.add_argument("--hex", metavar="KEY", help="dump one key's value as hex")
    parser.add_argument("--decode", metavar="KEY", help="zlib+NBT decode one key's value")
    args = parser.parse_args()

    data = read_db(args.dbdir)

    if args.decode:
        value = data.get(args.decode)
        if value is None:
            raise SystemExit(f"key not found: {args.decode!r}")
        name, body = decode_value(value)
        print(f"{args.decode!r}  root={name!r}  ({len(value)} compressed bytes)")
        import pprint

        pprint.pprint(body, width=110, depth=5)
        return

    if args.hex:
        value = data.get(args.hex)
        if value is None:
            raise SystemExit(f"key not found: {args.hex!r}")
        print(f"{args.hex} ({len(value)} bytes, zlib header {value[:2]!r})")
        print(value.hex())
        return

    for key in sorted(data):
        if args.grep and args.grep not in key:
            continue
        shown = escape_key(key)
        if args.keys:
            print(f"{shown}  ({len(data[key])} bytes)")
        else:
            print(f"{shown} = {data[key][:60].hex()}")


if __name__ == "__main__":
    main()
