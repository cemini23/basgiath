#!/usr/bin/env python3
"""Emit the college as Bedrock functions.

Run from the repo root:

    python3 scripts/build_map.py

A player then runs /function basgiath/build in a flat world.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "addon" / "behavior_pack" / "functions"
BASGIATH = OUT / "basgiath"

MAX_FILL = 32768
MAX_CMDS = 50
# The span sits this many blocks above the player's feet.
# A fall onto the ground is fatal. 23 blocks is the kill line.
DECK_Y = 32
SPAN_Z = 20
START = (8, 0, 66)

OLD_FUNCTIONS = (
    "parapet_wind.mcfunction",
    "parapet_checkpoint_a.mcfunction",
    "parapet_checkpoint_b.mcfunction",
)


def rel(value: int) -> str:
    if value == 0:
        return "~"
    return f"~{value}"


def _split_box(x0: int, y0: int, z0: int, x1: int, y1: int, z1: int):
    x0, x1 = sorted((x0, x1))
    y0, y1 = sorted((y0, y1))
    z0, z1 = sorted((z0, z1))
    dx = x1 - x0 + 1
    dy = y1 - y0 + 1
    dz = z1 - z0 + 1
    if dx * dy * dz <= MAX_FILL:
        yield x0, y0, z0, x1, y1, z1
        return
    spans = sorted(((dx, "x"), (dy, "y"), (dz, "z")), reverse=True)
    axis = spans[0][1]
    if axis == "x":
        mid = x0 + (dx // 2) - 1
        if mid < x0 or mid >= x1:
            raise RuntimeError(f"cannot slice fill {dx}x{dy}x{dz}")
        yield from _split_box(x0, y0, z0, mid, y1, z1)
        yield from _split_box(mid + 1, y0, z0, x1, y1, z1)
    elif axis == "y":
        mid = y0 + (dy // 2) - 1
        if mid < y0 or mid >= y1:
            raise RuntimeError(f"cannot slice fill {dx}x{dy}x{dz}")
        yield from _split_box(x0, y0, z0, x1, mid, z1)
        yield from _split_box(x0, mid + 1, z0, x1, y1, z1)
    else:
        mid = z0 + (dz // 2) - 1
        if mid < z0 or mid >= z1:
            raise RuntimeError(f"cannot slice fill {dx}x{dy}x{dz}")
        yield from _split_box(x0, y0, z0, x1, y1, mid)
        yield from _split_box(x0, y0, mid + 1, x1, y1, z1)


class Builder:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def add(self, command: str) -> None:
        self.lines.append(command)

    def fill(self, x0: int, y0: int, z0: int, x1: int, y1: int, z1: int, block: str) -> None:
        for box in _split_box(x0, y0, z0, x1, y1, z1):
            a = " ".join(rel(n) for n in box[:3])
            b = " ".join(rel(n) for n in box[3:])
            self.add(f"fill {a} {b} {block}")

    def setblock(self, x: int, y: int, z: int, block: str) -> None:
        self.add(f"setblock {rel(x)} {rel(y)} {rel(z)} {block}")


def shell(builder: Builder, x0: int, y0: int, z0: int, x1: int, y1: int, z1: int, block: str) -> None:
    """Solid box, then a hollow interior. The floor stays."""
    builder.fill(x0, y0, z0, x1, y1, z1, block)
    if x1 - x0 > 1 and z1 - z0 > 1 and y1 - y0 > 1:
        builder.fill(x0 + 1, y0 + 1, z0 + 1, x1 - 1, y1 - 1, z1 - 1, "air")


def ground(builder: Builder) -> None:
    builder.fill(0, -2, 0, 170, -2, 150, "stone")
    builder.fill(0, -1, 0, 170, -1, 150, "grass_block")


def chasm(builder: Builder) -> None:
    """Open air under the span. The floor stays at ground level so the fall kills."""
    builder.fill(15, -1, 12, 77, -1, 28, "stone")
    builder.fill(15, 0, 12, 77, DECK_Y - 1, 28, "air")


def tower(builder: Builder, x0: int, z0: int, x1: int, z1: int) -> None:
    builder.fill(x0, -1, z0, x1, DECK_Y, z1, "stone_bricks")
    builder.fill(x0 + 1, 0, z0 + 1, x1 - 1, DECK_Y - 1, z1 - 1, "air")


def _stair(builder: Builder, x0: int, x1: int, y: int, z: int) -> None:
    """One glowing step. x0 and x1 are the walk blocks. Curbs sit one block outside."""
    for x in range(x0, x1 + 1):
        builder.setblock(x, y, z, "sea_lantern")
        builder.setblock(x, y + 1, z, "air")
        builder.setblock(x, y + 2, z, "air")
    for x in (x0 - 1, x1 + 1):
        builder.setblock(x, y, z, "stone_bricks")
        builder.setblock(x, y + 1, z, "sea_lantern")


def west_climb(builder: Builder) -> None:
    """Glowing stairs on the ground, south of the west tower, then a lit roof path."""
    for step in range(DECK_Y + 1):
        _stair(builder, 7, 8, step, 61 - step)
    builder.fill(6, -1, 62, 9, -1, 68, "sea_lantern")
    for z in range(SPAN_Z, 29):
        builder.setblock(7, DECK_Y, z, "sea_lantern")
        builder.setblock(8, DECK_Y, z, "sea_lantern")
    for x in range(7, 15):
        builder.setblock(x, DECK_Y, SPAN_Z, "sea_lantern")
    for z in range(12, 29):
        if z == SPAN_Z:
            continue
        builder.setblock(14, DECK_Y + 1, z, "stone_brick_wall")
        builder.setblock(14, DECK_Y + 2, z, "stone_brick_wall")


def east_climb(builder: Builder) -> None:
    """Lit roof path, then glowing stairs down to a sidewalk into the quad."""
    for x in range(78, 86):
        builder.setblock(x, DECK_Y, SPAN_Z, "sea_lantern")
    for z in range(SPAN_Z, 29):
        builder.setblock(84, DECK_Y, z, "sea_lantern")
        builder.setblock(85, DECK_Y, z, "sea_lantern")
    for step in range(DECK_Y + 1):
        _stair(builder, 84, 85, DECK_Y - step, 29 + step)
    builder.fill(83, -1, 22, 96, -1, 63, "sea_lantern")


def parapet(builder: Builder) -> None:
    for x in range(15, 78):
        if x in (45, 46):
            continue
        if x <= 18:
            block = "sea_lantern"
        elif x in (44, 47):
            block = "polished_blackstone"
        elif (x - 15) % 4 == 0:
            block = "chiseled_stone_bricks"
        else:
            block = "stone_bricks"
        builder.setblock(x, DECK_Y, SPAN_Z, block)


def bleachers(builder: Builder) -> None:
    for row, height in enumerate((3, 2, 1, 0)):
        builder.fill(100, 0, 4 + row, 164, height, 4 + row, "stone_bricks")
        builder.fill(100, 0, 78 - row, 164, height, 78 - row, "stone_bricks")


def wool_poles(builder: Builder) -> None:
    poles = (
        (122, 34, "cyan_wool"),
        (134, 34, "purple_wool"),
        (122, 46, "orange_wool"),
        (134, 46, "light_gray_wool"),
    )
    for x, z, wool in poles:
        builder.fill(x, 0, z, x, 4, z, wool)


def lantern_posts(builder: Builder) -> None:
    for x in (104, 116, 140, 152):
        for z in (20, 60):
            builder.setblock(x, 0, z, "stone_bricks")
            builder.setblock(x, 1, z, "lantern")


def quad(builder: Builder) -> None:
    builder.fill(96, -1, 4, 168, -1, 78, "stone_bricks")
    builder.fill(124, 0, 36, 132, 0, 44, "stone_bricks")
    builder.setblock(128, 0, 40, "lodestone")
    bleachers(builder)
    wool_poles(builder)
    lantern_posts(builder)
    shell(builder, 158, -1, 8, 164, 16, 14, "stone_bricks")
    builder.setblock(161, 15, 11, "bell")
    builder.setblock(161, 16, 11, "sea_lantern")


def dorm(builder: Builder, x0: int, z0: int, x1: int, z1: int) -> None:
    builder.fill(x0, -1, z0, x1, -1, z1, "stone_bricks")
    builder.fill(x0, 0, z0, x1, 4, z1, "spruce_planks")
    builder.fill(x0 + 1, 0, z0 + 1, x1 - 1, 4, z1 - 1, "air")
    builder.fill(x0, 5, z0, x1, 5, z1, "spruce_planks")
    door = (x0 + x1) // 2
    for dx in (0, 1):
        builder.setblock(door + dx, 0, z1, "air")
        builder.setblock(door + dx, 1, z1, "air")
    for x in range(x0 + 2, x1 - 1, 2):
        builder.setblock(x, 0, z0 + 1, "red_wool")
    mid_x = (x0 + x1) // 2
    mid_z = (z0 + z1) // 2
    builder.setblock(mid_x, 0, mid_z, "stone_bricks")
    builder.setblock(mid_x, 1, mid_z, "lantern")


def dorms(builder: Builder) -> None:
    dorm(builder, 98, 90, 118, 102)
    dorm(builder, 122, 90, 142, 102)
    dorm(builder, 98, 108, 118, 120)


def valley(builder: Builder) -> None:
    """A one-block bowl. Deeper would fall through the flat world."""
    builder.fill(16, -2, 94, 70, -2, 140, "grass_block")
    builder.fill(16, -1, 94, 70, -1, 140, "air")
    for x in range(18, 69, 10):
        builder.fill(x, -1, 96, x, 2, 96, "stone_bricks")
        builder.fill(x, -1, 138, x, 2, 138, "stone_bricks")
    for z in range(106, 139, 10):
        builder.fill(18, -1, z, 18, 2, z, "stone_bricks")
        builder.fill(68, -1, z, 68, 2, z, "stone_bricks")
    builder.fill(38, -2, 112, 48, -2, 122, "stone_bricks")
    builder.setblock(43, -2, 117, "gold_block")
    for z in (117, 118):
        builder.setblock(70, -2, z, "stone_bricks")
        builder.setblock(70, -1, z, "air")


def paths(builder: Builder) -> None:
    builder.fill(90, -1, 18, 96, -1, 22, "stone_bricks")
    builder.fill(108, -1, 79, 112, -1, 89, "stone_bricks")
    builder.fill(71, -1, 116, 98, -1, 120, "stone_bricks")


def finish(builder: Builder) -> None:
    builder.setblock(45, DECK_Y, SPAN_Z, "air")
    builder.setblock(46, DECK_Y, SPAN_Z, "air")
    builder.setblock(5, DECK_Y + 1, SPAN_Z, "stone_pressure_plate")
    builder.setblock(86, DECK_Y + 1, SPAN_Z, "stone_pressure_plate")
    builder.setblock(128, 0, 46, "stone_pressure_plate")
    builder.setblock(43, -1, 115, "stone_pressure_plate")
    builder.add("time set night")
    builder.add("weather thunder 999999")
    builder.add("gamerule dodaylightcycle false")
    builder.add("gamerule doweathercycle false")
    builder.add("gamerule domobspawning false")
    builder.add("gamerule keepinventory true")
    builder.add("gamerule sendcommandfeedback false")
    builder.add("gamerule commandblockoutput false")
    builder.add("gamerule doimmediaterespawn true")
    builder.add("gamemode adventure @a")
    builder.add('titleraw @p title {"rawtext":[{"text":"Welcome, candidate"}]}')
    builder.add('titleraw @p subtitle {"rawtext":[{"text":"Cross the Parapet"}]}')
    builder.add(
        'tellraw @a {"rawtext":[{"text":"Fan-made. Not official. Not affiliated with any publisher. The glowing stairs are in front of you. A fall from the span sends you back here. Touch the stone in the Quad. Then run /function basgiath/summon_dragon"}]}'
    )
    sx, sy, sz = START
    builder.add(f"spawnpoint @p ~{sx} ~{sy} ~{sz}")
    builder.add(f"tp @p ~{sx} ~{sy} ~{sz} 180 0")


def geometry() -> list[str]:
    builder = Builder()
    ground(builder)
    chasm(builder)
    tower(builder, 2, 12, 14, 28)
    west_climb(builder)
    tower(builder, 78, 12, 90, 28)
    east_climb(builder)
    parapet(builder)
    quad(builder)
    dorms(builder)
    valley(builder)
    paths(builder)
    finish(builder)
    return builder.lines


def write_functions(commands: list[str]) -> int:
    stages = [commands[i : i + MAX_CMDS] for i in range(0, len(commands), MAX_CMDS)]
    BASGIATH.mkdir(parents=True, exist_ok=True)
    for index, chunk in enumerate(stages, start=1):
        path = BASGIATH / f"stage_{index:02d}.mcfunction"
        path.write_text("\n".join(chunk) + "\n", encoding="utf-8")
    stale = [path for path in BASGIATH.glob("stage_*.mcfunction") if path.name not in {f"stage_{i:02d}.mcfunction" for i in range(1, len(stages) + 1)}]
    for path in stale:
        path.unlink()

    tick_lines = ["scoreboard players operation #now map_state = #stage map_state"]
    for index in range(1, len(stages) + 1):
        nxt = index + 1 if index < len(stages) else 0
        name = f"stage_{index:02d}"
        tick_lines.append(
            f'execute if score #now map_state matches {index} as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/{name}'
        )
        tick_lines.append(
            f"execute if score #now map_state matches {index} run scoreboard players set #stage map_state {nxt}"
        )
    tick_lines.append('execute if score #now map_state matches 0 run function basgiath/live')
    (BASGIATH / "tick.mcfunction").write_text("\n".join(tick_lines) + "\n", encoding="utf-8")
    return len(stages)


BUILD = """titleraw @s times 0 40 5
titleraw @s title {"rawtext":[{"text":"Building"}]}
titleraw @s subtitle {"rawtext":[{"text":"Stay still"}]}
scoreboard objectives add map_state dummy
kill @e[type=armor_stand,name="build_anchor"]
execute at @s run setblock ~ ~-1 ~ stone
execute at @s run setblock ~ ~-1 ~-1 sea_lantern
execute at @s run setblock ~1 ~-1 ~-1 sea_lantern
execute at @s run setblock ~-1 ~-1 ~-1 sea_lantern
execute at @s run summon armor_stand "build_anchor" ~ ~ ~
execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] invisibility 999999 1 true
execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] resistance 999999 255 true
scoreboard players set #stage map_state 1
tellraw @s {"rawtext":[{"text":"The college is rising. Stay still. Fan-made. Not official. Not affiliated with any publisher."}]}
gamerule sendcommandfeedback false
"""

LIVE = """scoreboard players add #wind map_state 1
execute if score #wind map_state matches 4.. run scoreboard players set #wind map_state 0
execute if score #wind map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s positioned ~15 ~33 ~19 as @a[dx=63,dy=2,dz=2] at @s run tp @s ~ ~ ~0.18
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~20 ~34 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~40 ~34 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~55 ~34 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~4,y=~32,z=~14,dx=10,dy=3,dz=14,tag=!cp_west] run tellraw @s {"rawtext":[{"text":"The span is one block wide. A fall sends you back to the ground."}]}
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~4,y=~32,z=~14,dx=10,dy=3,dz=14] add cp_west
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~78,y=~32,z=~14,dx=12,dy=3,dz=14,tag=!cp_east] run spawnpoint @s ~84 ~33 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~78,y=~32,z=~14,dx=12,dy=3,dz=14] add cp_east
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~124,y=~0,z=~44,dx=10,dy=3,dz=8,tag=!cp_quad] run spawnpoint @s ~128 ~0 ~48
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~124,y=~0,z=~44,dx=10,dy=3,dz=8] add cp_quad
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~38,y=~-2,z=~112,dx=12,dy=4,dz=12,tag=!cp_valley] run spawnpoint @s ~43 ~-1 ~117
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~38,y=~-2,z=~112,dx=12,dy=4,dz=12] add cp_valley
scoreboard players add #storm map_state 1
execute if score #storm map_state matches 200.. run scoreboard players set #storm map_state 0
execute if score #storm map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] run weather thunder 999999
"""

SUMMON = """execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run summon dragon_rider:dragon ~43 ~-1 ~117
execute as @e[type=armor_stand,name="build_anchor",c=1] run tellraw @a {"rawtext":[{"text":"A dragon waits on the gold pad. Mount it and fly."}]}
execute unless entity @e[type=armor_stand,name="build_anchor"] run tellraw @s {"rawtext":[{"text":"Raise the college first. Run /function basgiath/build"}]}
"""

README = """# Functions

`/function basgiath/build` raises the college around an armor stand named `build_anchor`.

The stand is the origin. Every later command is relative to it. The build stays at your feet. The screen says "Building" at once. It places one stone under the stand, then gives that stand invisibility and resistance. The stone keeps the stand from falling. The build runs one stage per tick.

`/function basgiath/summon_dragon` summons `dragon_rider:dragon` on the valley pad.

`functions/tick.json` runs `basgiath/tick`. After the build, that tick runs `basgiath/live` for wind, checkpoints, and the storm. A fall from the span is fatal. You respawn on the ground path until you reach the east tower.

Do not run the old placeholder functions. They are gone. Coordinates live in `scripts/build_map.py`.
"""


_NON_SOLID = {"air", "lantern", "stone_pressure_plate", "bell"}


def _rel(token: str) -> int:
    if token == "~":
        return 0
    if token.startswith("~"):
        return int(token[1:])
    return int(token)


def solid_blocks(lines: list[str]) -> dict[tuple[int, int, int], str]:
    blocks: dict[tuple[int, int, int], str] = {}
    for line in lines:
        parts = line.split()
        if len(parts) < 5:
            continue
        if parts[0] == "setblock":
            x, y, z = _rel(parts[1]), _rel(parts[2]), _rel(parts[3])
            block = parts[4]
            cells = [(x, y, z)]
        elif parts[0] == "fill" and len(parts) >= 8:
            x0, y0, z0 = _rel(parts[1]), _rel(parts[2]), _rel(parts[3])
            x1, y1, z1 = _rel(parts[4]), _rel(parts[5]), _rel(parts[6])
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
            if block in _NON_SOLID:
                blocks.pop(cell, None)
            else:
                blocks[cell] = block
    return blocks


def _can_stand(blocks: dict[tuple[int, int, int], str], x: int, y: int, z: int) -> bool:
    below = blocks.get((x, y - 1, z))
    if below is None or below in _NON_SOLID:
        return False
    for dy in (0, 1):
        body = blocks.get((x, y + dy, z))
        if body is not None and body not in _NON_SOLID:
            return False
    return True


def _reachable(blocks: dict[tuple[int, int, int], str], start: tuple[int, int, int], goal) -> bool:
    from collections import deque

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


def assert_walk(lines: list[str]) -> None:
    """Fail the build when the start cannot walk onto the span."""
    if DECK_Y + 1 < 24:
        raise SystemExit(f"span fall is {DECK_Y + 1} blocks, need at least 24")
    blocks = solid_blocks(lines)
    start = START
    if not _reachable(
        blocks,
        start,
        lambda x, y, z: y == DECK_Y + 1 and z == SPAN_Z and 15 <= x <= 44,
    ):
        raise SystemExit(f"no walk from {start} to the span")
    if not _reachable(
        blocks,
        (84, DECK_Y + 1, SPAN_Z),
        lambda x, y, z: y == 0 and x >= 90 and 22 <= z <= 40,
    ):
        raise SystemExit("no walk from the east roof down to the quad")


def main() -> None:
    commands = geometry()
    assert_walk(commands)
    count = write_functions(commands)
    (BASGIATH / "build.mcfunction").write_text(BUILD, encoding="utf-8")
    (BASGIATH / "live.mcfunction").write_text(LIVE, encoding="utf-8")
    (BASGIATH / "summon_dragon.mcfunction").write_text(SUMMON, encoding="utf-8")
    (OUT / "tick.json").write_text(
        json.dumps({"values": ["basgiath/tick"]}, indent=2) + "\n",
        encoding="utf-8",
    )
    (OUT / "README.md").write_text(README, encoding="utf-8")
    for name in OLD_FUNCTIONS:
        path = OUT / name
        if path.exists():
            path.unlink()
    print(f"wrote {count} stages, {len(commands)} build commands")


if __name__ == "__main__":
    main()
