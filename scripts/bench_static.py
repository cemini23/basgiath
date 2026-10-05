#!/usr/bin/env python3
"""Check the college from the files a release ships. No Minecraft client.

The .mcworld is a flat world. The college is placed later by the stage
functions. This script simulates those setblock and fill commands and
fails when the Parapet contract is broken. It replays the phone path: the
stage pass lands only inside the loaded box, then the far retry lands
everything outside it. It also proves that the same checks reject a deleted
span, a filled gap, and a safety floor.
"""

from __future__ import annotations

import json
import sys
import zipfile
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ROOT / "addon/behavior_pack/functions/basgiath"
WORLD = ROOT / "dist/basgiath.mcworld"

# Release contract. These numbers are the map a player has to cross.
DECK_Y = 32
SPAN_Z = 20
SPAN_X0 = 15
SPAN_X1 = 77
GAP_X = (45, 46)
START = (8, 0, 66)
EAST_ROOF = (84, 33, 20)
# The plaza marker is now chiseled_stone_bricks. The signet stone moved to
# the valley floor at 50,-1,130.
LODESTONE = (50, -1, 130)
# A full-health player dies on a fall of 23 blocks. Feet stand at y=33.
# A solid at y=10 or higher under the span makes that fall survivable.
MAX_SAFE_FLOOR_Y = 9

NON_SOLID = {"air", "lantern", "stone_pressure_plate", "bell"}
# A ladder is solid but climbable. It does not block the body and it carries a
# climb up, so the walk check passes through it instead of treating it as a wall.
CLIMBABLE = {"ladder"}
# Phone sim distance 4 reaches about 64 blocks, less from the far edge of a
# chunk. build_map.py uses the same box to split the stage pass from the retry.
LOADED = 48


def fail(message: str) -> None:
    raise SystemExit(message)


def rel_coord(token: str) -> int:
    if token == "~":
        return 0
    if token.startswith("~"):
        return int(token[1:])
    return int(token)


def stage_lines() -> list[str]:
    stages = sorted(FUNCTIONS.glob("stage_*.mcfunction"))
    if not stages:
        fail("no stage functions")
    lines: list[str] = []
    for path in stages:
        lines.extend(path.read_text(encoding="utf-8").splitlines())
    return lines


def far_lines() -> list[str]:
    """The retry pass. A phone only reaches these blocks after the load."""
    fars = sorted(FUNCTIONS.glob("far_*.mcfunction"))
    if not fars:
        fail("no far functions")
    lines: list[str] = []
    for path in fars:
        lines.extend(path.read_text(encoding="utf-8").splitlines())
    return lines


def _box(line: str) -> tuple[int, int, int, int] | None:
    parts = line.split()
    if not parts:
        return None
    if parts[0] == "setblock" and len(parts) >= 4:
        x, z = rel_coord(parts[1]), rel_coord(parts[3])
        return (x, z, x, z)
    if parts[0] == "fill" and len(parts) >= 7:
        x0, z0 = rel_coord(parts[1]), rel_coord(parts[3])
        x1, z1 = rel_coord(parts[4]), rel_coord(parts[6])
        return (min(x0, x1), min(z0, z1), max(x0, x1), max(z0, z1))
    if parts[0] == "summon" and len(parts) >= 5:
        # The name tag is quoted and may hold spaces, so the coordinates are
        # the last three tokens, not fixed positions.
        x, z = rel_coord(parts[-3]), rel_coord(parts[-1])
        return (x, z, x, z)
    return None


def is_far(line: str) -> bool:
    """True when a phone at sim distance 4 may not have this chunk yet."""
    box = _box(line)
    if box is None:
        return False
    x0, z0, x1, z1 = box
    return x0 < -LOADED or z0 < -LOADED or x1 > LOADED or z1 > LOADED


def _summon_tag(line: str) -> tuple[str, str] | None:
    """The (entity type, name tag) of a named summon, else None."""
    parts = line.split(None, 2)
    if len(parts) < 3 or parts[0] != "summon":
        return None
    rest = parts[2]
    if not rest.startswith('"'):
        return None
    end = rest.find('"', 1)
    if end < 0:
        return None
    return parts[1], rest[1:end]


def retry_form(line: str) -> str:
    """The retry form of a far command.

    A fill can run twice safely. A summon cannot: the stage pass may already
    have spawned the entity, so the retry guards it with ``unless entity``.
    """
    tag = _summon_tag(line)
    if tag is None:
        return line
    entity_type, name = tag
    return f'execute unless entity @e[type={entity_type},name="{name}"] run {line}'


def assert_far_retry(stage: list[str], retry: list[str]) -> None:
    """Every far stage command must appear in the retry.

    The old check compared the retry against the same ``is_far`` filter that
    built it, so a command class the parser could not see was invisible to
    both sides. This compares the emitted retry against the far stage commands
    in their exact retry form, so a dropped spawn fails the bench.
    """
    expected = sorted(retry_form(line) for line in stage if is_far(line))
    if expected != sorted(retry):
        missing = [line for line in expected if line not in retry]
        extra = [line for line in retry if line not in expected]
        detail = missing[0] if missing else extra[0]
        fail(f"the far retry does not match the far stage pass: {detail}")


def phone_lines() -> list[str]:
    """What the phone runs: the loaded stage pass, then the far retry.

    A stage command outside the loaded box is dropped by the phone, so the
    retry is the only place it lands. The retry must therefore carry every far
    command, air fills included and summons guarded.
    """
    stages = stage_lines()
    retry = far_lines()
    assert_far_retry(stages, retry)
    return [line for line in stages if not is_far(line)] + retry


def solid_blocks(lines: list[str]) -> dict[tuple[int, int, int], str]:
    """Replay setblock and fill. Later commands replace earlier ones."""
    blocks: dict[tuple[int, int, int], str] = {}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0] == "setblock" and len(parts) >= 5:
            cells = [(rel_coord(parts[1]), rel_coord(parts[2]), rel_coord(parts[3]))]
            block = parts[4]
        elif parts[0] == "fill" and len(parts) >= 8:
            x0, y0, z0 = rel_coord(parts[1]), rel_coord(parts[2]), rel_coord(parts[3])
            x1, y1, z1 = rel_coord(parts[4]), rel_coord(parts[5]), rel_coord(parts[6])
            block = parts[7]
            cells = [
                (x, y, z)
                for x in range(min(x0, x1), max(x0, x1) + 1)
                for y in range(min(y0, y1), max(y0, y1) + 1)
                for z in range(min(z0, z1), max(z0, z1) + 1)
            ]
        else:
            continue
        for cell in cells:
            if block in NON_SOLID:
                blocks.pop(cell, None)
            else:
                blocks[cell] = block
    return blocks


def _span_xs() -> list[int]:
    return [x for x in range(SPAN_X0, SPAN_X1 + 1) if x not in GAP_X]


def assert_parapet(blocks: dict[tuple[int, int, int], str]) -> None:
    missing = [x for x in _span_xs() if (x, DECK_Y, SPAN_Z) not in blocks]
    if missing:
        fail(f"Parapet is missing deck blocks at x={missing[:8]}")
    for x in GAP_X:
        if (x, DECK_Y, SPAN_Z) in blocks:
            fail(f"Parapet gap at x={x} is filled with {blocks[(x, DECK_Y, SPAN_Z)]}")
    # The open span is one block wide. Towers sit at x=14 and x=78.
    wide = []
    for x in range(19, 78):
        if x in GAP_X:
            continue
        for z in (SPAN_Z - 1, SPAN_Z + 1):
            if (x, DECK_Y, z) in blocks:
                wide.append((x, z, blocks[(x, DECK_Y, z)]))
    if wide:
        fail(f"Parapet is wider than one block: {wide[:6]}")
    safe = []
    for x in _span_xs():
        highest = max(
            (y for (bx, y, bz) in blocks if bx == x and bz == SPAN_Z and y < DECK_Y),
            default=-64,
        )
        if highest > MAX_SAFE_FLOOR_Y:
            safe.append((x, highest))
    if safe:
        fail(f"a floor under the Parapet makes the fall survivable: {safe[:6]}")


def _can_stand(blocks: dict[tuple[int, int, int], str], x: int, y: int, z: int) -> bool:
    below = blocks.get((x, y - 1, z))
    if below is None or below in NON_SOLID:
        return False
    for dy in (0, 1):
        body = blocks.get((x, y + dy, z))
        if body is not None and body not in NON_SOLID and body not in CLIMBABLE:
            return False
    return True


def _reachable(blocks: dict[tuple[int, int, int], str], start: tuple[int, int, int], goal) -> bool:
    if not _can_stand(blocks, *start):
        return False
    seen = {start}
    queue = deque([start])
    while queue:
        x, y, z = queue.popleft()
        if goal(x, y, z):
            return True
        for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            for ny in (y - 1, y, y + 1):
                nxt = (x + dx, ny, z + dz)
                if nxt in seen or not _can_stand(blocks, *nxt):
                    continue
                seen.add(nxt)
                queue.append(nxt)
    return False


def assert_walk(blocks: dict[tuple[int, int, int], str]) -> None:
    if not _reachable(
        blocks,
        START,
        lambda x, y, z: y == DECK_Y + 1 and z == SPAN_Z and SPAN_X0 <= x <= 44,
    ):
        fail(f"no walk from {START} onto the Parapet")
    if not _reachable(
        blocks,
        EAST_ROOF,
        lambda x, y, z: y == 0 and x >= 90 and SPAN_Z <= z <= 40,
    ):
        fail("no walk from the east roof down to the quad")


def assert_markers(blocks: dict[tuple[int, int, int], str], text: str) -> None:
    if blocks.get(LODESTONE) != "lodestone":
        fail(f"lodestone at {LODESTONE} is {blocks.get(LODESTONE)!r}")
    for needle in (
        "spawnpoint @p ~8 ~0 ~66",
        "spawnpoint @s ~84 ~33 ~20",
    ):
        if needle not in text:
            fail(f"missing spawn command {needle}")


def assert_dragon() -> None:
    path = ROOT / "addon/behavior_pack/entities/dragon.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    identifier = data["minecraft:entity"]["description"]["identifier"]
    if identifier != "dragon_rider:dragon":
        fail(f"dragon identifier is {identifier}")
    summon = (FUNCTIONS / "summon_dragon.mcfunction").read_text(encoding="utf-8")
    if identifier not in summon:
        fail("summon function does not name the dragon entity")


def assert_world() -> None:
    """The zip is a flat world header. It does not contain the college."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from nbt_le import decode_level_dat

    if not WORLD.exists():
        from build_world import main as build_world

        build_world()
    with zipfile.ZipFile(WORLD) as bundle:
        names = bundle.namelist()
        if "level.dat" not in names:
            fail("mcworld has no level.dat")
        level = decode_level_dat(bundle.read("level.dat"))
    if level.get("LevelName") != "Basgiath":
        fail("level name is not Basgiath")
    if level.get("Generator") != 2 or level.get("commandsEnabled") != 1:
        fail("world is not a flat world with commands")
    # Placed college blocks are not in this zip. Counting them here would pass
    # after the Parapet was deleted.
    db_files = [name for name in names if name.startswith("db/")]
    print(f"world header ok; leveldb files in the zip: {len(db_files)}")


def function_text() -> str:
    parts = []
    for path in sorted(FUNCTIONS.glob("*.mcfunction")):
        parts.append(path.read_text(encoding="utf-8"))
    return "\n".join(parts)


def expect_fail(lines: list[str], label: str) -> None:
    blocks = solid_blocks(lines)
    try:
        assert_parapet(blocks)
        assert_walk(blocks)
    except SystemExit:
        print(f"proof ok: {label}")
        return
    fail(f"checker stayed green after {label}")


def prove(lines: list[str]) -> None:
    """Mutate a copy of the commands. The product files stay as they are."""
    expect_fail(
        lines + [f"fill ~{SPAN_X0} ~{DECK_Y} ~{SPAN_Z} ~{SPAN_X1} ~{DECK_Y} ~{SPAN_Z} air"],
        "the Parapet blocks were deleted",
    )
    expect_fail(
        lines + ["setblock ~45 ~32 ~20 stone", "setblock ~46 ~32 ~20 stone"],
        "the two-block gap was filled",
    )
    expect_fail(
        lines + ["fill ~30 ~20 ~20 ~40 ~20 ~20 stone"],
        "a safety floor was added under the span",
    )


def prove_guard(stage: list[str], retry: list[str]) -> None:
    """Prove the retry check rejects a dropped far summon.

    A dropped fill is caught by the Parapet proofs. The entity contract needs
    its own mutation, because it was the class the old checker could not see.
    """
    guarded = [line for line in retry if "run summon" in line]
    if not guarded:
        fail("no guarded far summon to prove the retry check")
    try:
        assert_far_retry(stage, [line for line in retry if line != guarded[0]])
    except SystemExit:
        print("proof ok: a summon was dropped from the far retry")
        return
    fail("the checker stayed green after a summon was dropped from the far retry")


def main() -> None:
    lines = phone_lines()
    prove_guard(stage_lines(), far_lines())
    blocks = solid_blocks(lines)
    assert_parapet(blocks)
    assert_walk(blocks)
    assert_markers(blocks, function_text())
    assert_dragon()
    assert_world()
    prove(lines)
    span = len(_span_xs())
    print(f"static bench ok: {span} Parapet blocks, gap at x={GAP_X[0]} and x={GAP_X[1]}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit as exc:
        if exc.code not in (None, 0):
            print(exc.code, file=sys.stderr)
            sys.exit(1)
        raise
