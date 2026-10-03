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
    builder.fill(0, 0, 0, 170, 22, 150, "air")


def chasm(builder: Builder) -> None:
    builder.fill(17, -40, 7, 75, -1, 33, "deepslate")
    builder.fill(18, -39, 8, 74, -1, 32, "air")
    # Keep the deepslate floor at y=-40. Water on that layer would fall.
    builder.fill(18, -39, 8, 74, -37, 32, "water")
    for x, z in ((20, 10), (40, 30), (60, 10), (70, 30)):
        builder.setblock(x, -20, z, "crying_obsidian")


def tower(builder: Builder, x0: int, z0: int, x1: int, z1: int) -> None:
    builder.fill(x0, -1, z0, x1, 8, z1, "stone_bricks")
    builder.fill(x0 + 1, 0, z0 + 1, x1 - 1, 7, z1 - 1, "air")
    builder.setblock((x0 + x1) // 2, 9, z0 + 2, "lantern")


def west_stairs(builder: Builder) -> None:
    for step in range(10):
        y = -1 + step
        z = 14 + step
        builder.setblock(4, y, z, "stone_bricks")
        builder.setblock(4, y + 1, z, "air")
        builder.setblock(4, y + 2, z, "air")
    builder.setblock(8, 0, 28, "air")
    builder.setblock(8, 1, 28, "air")
    builder.setblock(9, 0, 28, "air")
    builder.setblock(9, 1, 28, "air")


def east_stairs(builder: Builder) -> None:
    for step in range(10):
        builder.setblock(91 + step, 8 - step, 20, "stone_bricks")


def parapet(builder: Builder) -> None:
    for x in range(15, 78):
        if x in (45, 46):
            continue
        block = "polished_blackstone" if x in (44, 47) else "stone_bricks"
        if block == "stone_bricks" and (x - 15) % 4 == 0:
            block = "chiseled_stone_bricks"
        builder.setblock(x, 8, 20, block)


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
    builder.fill(16, -6, 94, 70, -6, 140, "grass_block")
    builder.fill(16, -5, 94, 70, -1, 140, "air")
    for x in range(18, 69, 10):
        builder.fill(x, -5, 96, x, 2, 96, "stone_bricks")
        builder.fill(x, -5, 138, x, 2, 138, "stone_bricks")
    for z in range(106, 139, 10):
        builder.fill(18, -5, z, 18, 2, z, "stone_bricks")
        builder.fill(68, -5, z, 68, 2, z, "stone_bricks")
    builder.fill(38, -6, 112, 48, -6, 122, "stone_bricks")
    builder.setblock(43, -6, 117, "gold_block")
    # Five steps from the east path down to the bowl floor.
    for step in range(1, 6):
        y = -1 - step
        for z in (117, 118):
            builder.setblock(71 - step, y, z, "stone_bricks")
            builder.setblock(71 - step, y + 1, z, "air")
            builder.setblock(71 - step, y + 2, z, "air")


def paths(builder: Builder) -> None:
    builder.fill(90, -1, 18, 96, -1, 22, "stone_bricks")
    builder.fill(108, -1, 79, 112, -1, 89, "stone_bricks")
    builder.fill(71, -1, 116, 98, -1, 120, "stone_bricks")


def finish(builder: Builder) -> None:
    builder.setblock(45, 8, 20, "air")
    builder.setblock(46, 8, 20, "air")
    builder.setblock(8, 9, 18, "stone_pressure_plate")
    builder.setblock(84, 9, 18, "stone_pressure_plate")
    builder.setblock(128, 0, 46, "stone_pressure_plate")
    builder.setblock(43, -5, 115, "stone_pressure_plate")
    builder.add("time set night")
    builder.add("weather thunder 999999")
    builder.add("gamerule dodaylightcycle false")
    builder.add("gamerule doweathercycle false")
    builder.add("gamerule domobspawning false")
    builder.add("gamerule keepinventory true")
    builder.add("gamerule sendcommandfeedback false")
    builder.add("gamerule commandblockoutput false")
    builder.add("gamemode adventure @a")
    builder.add('titleraw @p title {"rawtext":[{"text":"Welcome, candidate"}]}')
    builder.add('titleraw @p subtitle {"rawtext":[{"text":"Cross the Parapet"}]}')
    builder.add(
        'tellraw @a {"rawtext":[{"text":"Fan-made. Not official. Not affiliated with any publisher. Touch the stone in the Quad. Then run /function basgiath/summon_dragon"}]}'
    )
    builder.add("tp @p ~8 ~9 ~20")


def geometry() -> list[str]:
    builder = Builder()
    ground(builder)
    chasm(builder)
    tower(builder, 2, 12, 14, 28)
    west_stairs(builder)
    tower(builder, 78, 12, 90, 28)
    east_stairs(builder)
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


BUILD = """scoreboard objectives add map_state dummy
kill @e[type=armor_stand,name="build_anchor"]
execute as @s if entity @s[y=-64,dy=44] run tp @s ~ 80 ~
execute at @s run setblock ~ ~-1 ~ stone
execute at @s run summon armor_stand "build_anchor" ~ ~ ~
execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] invisibility 999999 1 true
execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] resistance 999999 255 true
scoreboard players set #stage map_state 1
tellraw @s {"rawtext":[{"text":"The college is rising. Stay still. Fan-made. Not official. Not affiliated with any publisher."}]}
"""

LIVE = """scoreboard players add #wind map_state 1
execute if score #wind map_state matches 4.. run scoreboard players set #wind map_state 0
execute if score #wind map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s positioned ~15 ~9 ~19 as @a[dx=63,dy=2,dz=2] at @s run tp @s ~ ~ ~0.18
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~20 ~10 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~40 ~10 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~55 ~10 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~4,y=~8,z=~14,dx=10,dy=3,dz=14,tag=!cp_west] run spawnpoint @s ~8 ~9 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~4,y=~8,z=~14,dx=10,dy=3,dz=14] add cp_west
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~78,y=~8,z=~14,dx=12,dy=3,dz=14,tag=!cp_east] run spawnpoint @s ~84 ~9 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~78,y=~8,z=~14,dx=12,dy=3,dz=14] add cp_east
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~124,y=~0,z=~44,dx=10,dy=3,dz=8,tag=!cp_quad] run spawnpoint @s ~128 ~0 ~48
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~124,y=~0,z=~44,dx=10,dy=3,dz=8] add cp_quad
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~38,y=~-6,z=~112,dx=12,dy=4,dz=12,tag=!cp_valley] run spawnpoint @s ~43 ~-5 ~117
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~38,y=~-6,z=~112,dx=12,dy=4,dz=12] add cp_valley
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tp @a[x=~18,y=~-40,z=~8,dx=56,dy=36,dz=24] ~8 ~9 ~20
scoreboard players add #storm map_state 1
execute if score #storm map_state matches 200.. run scoreboard players set #storm map_state 0
execute if score #storm map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] run weather thunder 999999
"""

SUMMON = """execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run summon dragon_rider:dragon ~43 ~-5 ~117
execute as @e[type=armor_stand,name="build_anchor",c=1] run tellraw @a {"rawtext":[{"text":"A dragon waits on the gold pad. Mount it and fly."}]}
execute unless entity @e[type=armor_stand,name="build_anchor"] run tellraw @s {"rawtext":[{"text":"Raise the college first. Run /function basgiath/build"}]}
"""

README = """# Functions

`/function basgiath/build` raises the college around an armor stand named `build_anchor`.

The stand is the origin. Every later command is relative to it. The build runs one stage per tick.

`/function basgiath/summon_dragon` summons `dragon_rider:dragon` on the valley pad.

`functions/tick.json` runs `basgiath/tick`. After the build, that tick runs `basgiath/live` for wind, checkpoints, chasm rescue, and the storm.

Do not run the old placeholder functions. They are gone. Coordinates live in `scripts/build_map.py`.
"""


def main() -> None:
    commands = geometry()
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
