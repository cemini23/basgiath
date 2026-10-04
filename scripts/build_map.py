#!/usr/bin/env python3
"""Emit the college as Bedrock functions.

Run from the repo root:

    python3 scripts/build_map.py

A player then runs /function basgiath/build in a flat world.
"""

from __future__ import annotations

import json
from pathlib import Path

from zones.dorms import build as build_dorms
from zones.parapet import build as build_parapet
from zones.quad import build as build_quad
from zones.valley import build as build_valley

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "addon" / "behavior_pack" / "functions"
BASGIATH = OUT / "basgiath"

MAX_FILL = 32768
MAX_CMDS = 50
# Phone sim distance 4 reaches about 64 blocks, less from the far edge of a chunk.
# Keep the first pass inside this box. Retry everything outside it.
LOADED = 48
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
        for sx0, sx1 in _segments(x0, x1):
            for sz0, sz1 in _segments(z0, z1):
                for box in _split_box(sx0, y0, sz0, sx1, y1, sz1):
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


class ZoneCtx:
    """The fixed input for scripts/zones. build(ctx) returns commands."""

    def __init__(self) -> None:
        self._builder = Builder()
        self.DECK_Y = DECK_Y
        self.SPAN_Z = SPAN_Z
        self.START = START

    def add(self, command: str) -> None:
        self._builder.add(command)

    def fill(self, x0: int, y0: int, z0: int, x1: int, y1: int, z1: int, block: str) -> None:
        self._builder.fill(x0, y0, z0, x1, y1, z1, block)

    def setblock(self, x: int, y: int, z: int, block: str) -> None:
        self._builder.setblock(x, y, z, block)

    def shell(self, x0: int, y0: int, z0: int, x1: int, y1: int, z1: int, block: str) -> None:
        shell(self._builder, x0, y0, z0, x1, y1, z1, block)

    def take(self) -> list[str]:
        lines = self._builder.lines
        self._builder.lines = []
        return lines


def paths(ctx: ZoneCtx) -> None:
    ctx.fill(90, -1, 18, 96, -1, 22, "stone_bricks")
    ctx.fill(108, -1, 79, 112, -1, 89, "stone_bricks")
    ctx.fill(71, -1, 116, 98, -1, 120, "stone_bricks")


def finish(ctx: ZoneCtx) -> None:
    ctx.setblock(45, ctx.DECK_Y, ctx.SPAN_Z, "air")
    ctx.setblock(46, ctx.DECK_Y, ctx.SPAN_Z, "air")
    ctx.setblock(5, ctx.DECK_Y + 1, ctx.SPAN_Z, "stone_pressure_plate")
    ctx.setblock(86, ctx.DECK_Y + 1, ctx.SPAN_Z, "stone_pressure_plate")
    ctx.setblock(128, 0, 46, "stone_pressure_plate")
    ctx.setblock(43, -1, 115, "stone_pressure_plate")
    ctx.add("time set night")
    ctx.add("weather thunder 999999")
    ctx.add("gamerule dodaylightcycle false")
    ctx.add("gamerule doweathercycle false")
    ctx.add("gamerule domobspawning false")
    ctx.add("gamerule keepinventory true")
    ctx.add("gamerule sendcommandfeedback false")
    ctx.add("gamerule commandblockoutput false")
    ctx.add("gamerule doimmediaterespawn true")
    sx, sy, sz = ctx.START
    ctx.add(f"spawnpoint @p ~{sx} ~{sy} ~{sz}")


def geometry() -> list[str]:
    """Join the zones, then the paths and the world rules.

    Phase 0 keeps this order. The command list must match the four-zone world.
    """
    ctx = ZoneCtx()
    lines: list[str] = []
    lines.extend(build_parapet(ctx))
    lines.extend(build_quad(ctx))
    lines.extend(build_dorms(ctx))
    lines.extend(build_valley(ctx))
    paths(ctx)
    finish(ctx)
    lines.extend(ctx.take())
    return lines


def write_named_stages(prefix: str, commands: list[str]) -> int:
    BASGIATH.mkdir(parents=True, exist_ok=True)
    stages = [commands[i : i + MAX_CMDS] for i in range(0, len(commands), MAX_CMDS)]
    names = {f"{prefix}_{index:02d}.mcfunction" for index in range(1, len(stages) + 1)}
    for index, chunk in enumerate(stages, start=1):
        path = BASGIATH / f"{prefix}_{index:02d}.mcfunction"
        path.write_text("\n".join(chunk) + "\n", encoding="utf-8")
    for path in BASGIATH.glob(f"{prefix}_*.mcfunction"):
        if path.name not in names:
            path.unlink()
    return len(stages)


def write_functions(commands: list[str]) -> int:
    count = write_named_stages("stage", commands)
    tick_lines = ["scoreboard players operation #now map_state = #stage map_state"]
    for index in range(1, count + 1):
        nxt = index + 1 if index < count else 0
        name = f"stage_{index:02d}"
        tick_lines.append(
            f'execute if score #now map_state matches {index} as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/{name}'
        )
        tick_lines.append(
            f"execute if score #now map_state matches {index} run scoreboard players set #stage map_state {nxt}"
        )
    tick_lines.append('execute if score #now map_state matches 0 run function basgiath/live')
    (BASGIATH / "tick.mcfunction").write_text("\n".join(tick_lines) + "\n", encoding="utf-8")
    return count


def at_anchor(command: str) -> str:
    return (
        'execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run ' + command
    )


def stage_calls(prefix: str, count: int) -> list[str]:
    return [at_anchor(f"function basgiath/{prefix}_{index:02d}") for index in range(1, count + 1)]


def _segments(a0: int, a1: int, limit: int = LOADED) -> list[tuple[int, int]]:
    """Split an axis so each piece is fully inside or fully outside the loaded box."""
    lo, hi = sorted((a0, a1))
    points = {lo, hi + 1}
    if lo < -limit <= hi:
        points.add(-limit)
    if lo <= limit < hi:
        points.add(limit + 1)
    ordered = sorted(points)
    spans: list[tuple[int, int]] = []
    for start, end_excl in zip(ordered, ordered[1:]):
        end = end_excl - 1
        if start <= end:
            spans.append((start, end))
    return spans


def _box(line: str) -> tuple[int, int, int, int] | None:
    parts = line.split()
    if parts[0] == "setblock" and len(parts) >= 4:
        x = _rel(parts[1])
        z = _rel(parts[3])
        return (x, z, x, z)
    if parts[0] == "fill" and len(parts) >= 7:
        x0, z0 = _rel(parts[1]), _rel(parts[3])
        x1, z1 = _rel(parts[4]), _rel(parts[6])
        return (min(x0, x1), min(z0, z1), max(x0, x1), max(z0, z1))
    return None


def is_far(line: str) -> bool:
    """True when a phone at sim distance 4 may not have this chunk yet."""
    box = _box(line)
    if box is None:
        return False
    x0, z0, x1, z1 = box
    return x0 < -LOADED or z0 < -LOADED or x1 > LOADED or z1 > LOADED


def build_text(stage_count: int) -> str:
    """Place the college from the build command.

    The phone runs this command. It does not run the tick loop.
    A later pass places the stairs and the plaza after those chunks load.
    """
    areas = (
        ("college_a", 40, 40),
        ("college_b", 120, 40),
        ("college_c", 40, 110),
        ("college_d", 120, 110),
    )
    area_lines = []
    for name, x, z in areas:
        area_lines.append(at_anchor(f"tickingarea remove {name}"))
        area_lines.append(at_anchor(f"tickingarea add circle ~{x} ~32 ~{z} 4 {name} true"))
    lines = [
        "titleraw @s times 0 80 10",
        'titleraw @s title {"rawtext":[{"text":"Building"}]}',
        'titleraw @s subtitle {"rawtext":[{"text":"Stay still"}]}',
        "scoreboard objectives add map_state dummy",
        'kill @e[type=armor_stand,name="build_anchor"]',
        "execute at @s run setblock ~ ~-1 ~ stone",
        "execute at @s run setblock ~ ~-1 ~-1 sea_lantern",
        "execute at @s run setblock ~1 ~-1 ~-1 sea_lantern",
        "execute at @s run setblock ~-1 ~-1 ~-1 sea_lantern",
        'execute at @s run summon armor_stand "build_anchor" ~ ~ ~',
        'execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] invisibility 999999 1 true',
        'execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] resistance 999999 255 true',
        "gamerule sendcommandfeedback false",
        "gamemode adventure @a",
        *area_lines,
        "scoreboard players set #done map_state 0",
        "scoreboard players set #pass map_state 1",
        "schedule on_area_loaded add tickingarea college_b basgiath/fill_far",
        "schedule on_area_loaded add tickingarea college_d basgiath/fill_far",
        "schedule delay add basgiath/raise 300",
        *stage_calls("stage", stage_count),
        "scoreboard players set #stage map_state 0",
        'tellraw @s {"rawtext":[{"text":"The college is rising. Stay still for 15 seconds. Fan-made. Not official. Not affiliated with any publisher."}]}',
    ]
    return "\n".join(lines) + "\n"


def welcome_lines() -> list[str]:
    """Run once, after the player is standing in the loaded plaza."""
    sx, sy, sz = START
    once = "execute if score #done map_state matches 0 as @e[type=armor_stand,name=\"build_anchor\",c=1] at @s run "
    return [
        'execute if score #done map_state matches 0 run gamemode adventure @a',
        once + 'titleraw @p title {"rawtext":[{"text":"Welcome, candidate"}]}',
        once + 'titleraw @p subtitle {"rawtext":[{"text":"Cross the Parapet"}]}',
        once
        + 'tellraw @a {"rawtext":[{"text":"Fan-made. Not official. Not affiliated with any publisher. The glowing stairs are in front of you. A fall from the span sends you back here. Touch the stone in the Quad. Then run /function basgiath/summon_dragon"}]}',
        once + f"tp @p ~{sx} ~{sy} ~{sz} 180 0",
        "scoreboard players set #done map_state 1",
    ]


def raise_text() -> str:
    """Move the player onto the plaza so the phone loads those chunks.

    The move is 8 blocks up. Slow falling keeps a miss from killing them.
    The blocks are placed 4 seconds later, then the player returns to the start.
    """
    lines = [
        "effect @p slow_falling 8 0 true",
        "effect @p resistance 8 5 true",
        at_anchor("tp @p ~120 ~8 ~40"),
        "schedule delay add basgiath/open 80",
    ]
    return "\n".join(lines) + "\n"

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

The stand is the origin. Every later command is relative to it. The build stays at your feet. The screen says "Building" at once. It places one stone under the stand, then gives that stand invisibility and resistance. The stone keeps the stand from falling. The same command places every stage. About 15 seconds later the game moves you onto the plaza for a few seconds, places the stairs, then returns you to the start. Close chat. Do not walk until the screen says "Welcome, candidate".

`/function basgiath/summon_dragon` summons `dragon_rider:dragon` on the valley pad.

The script runs `basgiath/tick` every tick. After the build, that tick runs `basgiath/live` for wind, checkpoints, and the storm. A fall from the span is fatal. You respawn on the ground path until you reach the east tower.

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
        lambda x, y, z: y == 0 and x >= 90 and SPAN_Z <= z <= 40,
    ):
        raise SystemExit("no walk from the east roof down to the quad")


def main() -> None:
    commands = geometry()
    assert_walk(commands)
    far = [line for line in commands if is_far(line)]
    if not any(line.startswith("setblock ~91 ") for line in far):
        raise SystemExit("far retry missed the east stairs")
    if not any("lodestone" in line for line in far):
        raise SystemExit("far retry missed the lodestone")
    if any(line.startswith("fill ~ ~-2 ~ ~170 ") for line in far):
        raise SystemExit("far pass still refills the whole ground plane")
    count = write_functions(commands)
    far_count = write_named_stages("far", far)
    if far_count < 1:
        raise SystemExit("far retry has no commands")
    far_calls = stage_calls("far", far_count)
    (BASGIATH / "build.mcfunction").write_text(build_text(count), encoding="utf-8")
    (BASGIATH / "fill_far.mcfunction").write_text("\n".join(far_calls) + "\n", encoding="utf-8")
    (BASGIATH / "raise.mcfunction").write_text(raise_text(), encoding="utf-8")
    (BASGIATH / "open.mcfunction").write_text(
        "\n".join(["scoreboard players set #pass map_state 2", *far_calls, *welcome_lines()]) + "\n",
        encoding="utf-8",
    )
    (BASGIATH / "live.mcfunction").write_text(LIVE, encoding="utf-8")
    (BASGIATH / "summon_dragon.mcfunction").write_text(SUMMON, encoding="utf-8")
    # The phone does not run tick.json. main.js runs basgiath/tick instead.
    (OUT / "tick.json").write_text(
        json.dumps({"values": []}, indent=2) + "\n",
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
