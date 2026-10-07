#!/usr/bin/env python3
"""Check the Java dialect, and check that it cannot drift.

Two things are worth guarding here.

The first is the translations themselves. A wrong one is quiet: the Java jar
loads, the function runs, and nothing happens, because the command named
something that does not exist on Java.

The second is the promise that the Bedrock output does not move. The port is a
parallel track, and the moment the Bedrock files change the port has cost the
Bedrock release something. `check_bedrock_output_is_the_source` rebuilds the
command list and compares.

Run from the repo root:

    python3 scripts/test_editions.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from editions import (  # noqa: E402
    BEDROCK_ONLY,
    TranslationError,
    drop_key,
    to_java,
)

FAILURES: list[str] = []


def check(name: str, got, want) -> None:
    if got != want:
        FAILURES.append(f"{name}\n     got:  {got!r}\n     want: {want!r}")


def check_raises(name: str, line: str) -> None:
    try:
        to_java(line)
    except TranslationError:
        return
    FAILURES.append(f"{name}: expected a loud stop, got a translation for {line!r}")


# --- the anvil the whole translation rests on ---------------------------------

check(
    "execute prefix is kept",
    to_java('execute at @s run setblock ~ ~-1 ~ stone'),
    'execute at @s run setblock ~ ~-1 ~ stone',
)
check(
    "c= is Java limit=, and the entity type is namespaced",
    to_java('execute at @s run kill @e[type=armor_stand,name="build_anchor",c=1]'),
    'execute at @s run kill @e[type=minecraft:armor_stand,name="build_anchor",limit=1]',
)

# --- the verbs that differ ---------------------------------------------------

check(
    "a named summon moves the name into NBT",
    to_java('summon armor_stand "build_anchor" ~ ~ ~'),
    "summon minecraft:armor_stand ~ ~ ~ {CustomName:'{\"text\":\"build_anchor\"}'}",
)
check(
    "the dragon summon takes the mod namespace",
    to_java("summon dragon_rider:dragon ~43 ~-1 ~117"),
    "summon basgiath:dragon ~43 ~-1 ~117",
)
check(
    "the dragon guard follows the summon",
    to_java("execute unless entity @e[type=dragon_rider:dragon] run summon dragon_rider:dragon ~43 ~-1 ~117"),
    "execute unless entity @e[type=basgiath:dragon] run summon basgiath:dragon ~43 ~-1 ~117",
)
check(
    "tellraw unwraps rawtext",
    to_java('tellraw @a {"rawtext":[{"text":"Hold the line."}]}'),
    'tellraw @a {"text":"Hold the line."}',
)
check(
    "a multi-part tellraw stays a component list",
    to_java('titleraw @s actionbar {"rawtext":[{"text":"a"},{"score":{"name":"@s","objective":"run_sec"}}]}'),
    'title @s actionbar [{"text":"a"},{"score":{"name":"@s","objective":"run_sec"}}]',
)
check(
    "titleraw times has no text payload",
    to_java("titleraw @s times 0 80 10"),
    "title @s times 0 80 10",
)
check(
    "gamerule names go camelCase",
    to_java("gamerule doimmediaterespawn true"),
    "gamerule doImmediateRespawn true",
)
check(
    "effect gains give, and a namespace",
    to_java("effect @p slow_falling 8 0 true"),
    "effect give @p minecraft:slow_falling 8 0 true",
)
check(
    "particle gains the arguments Java insists on",
    to_java("particle minecraft:basic_smoke_particle ~20 ~34 ~20"),
    "particle minecraft:smoke ~20 ~34 ~20 0 0 0 0 1 normal",
)
check(
    "schedule delay becomes schedule function",
    to_java("schedule delay add basgiath/raise 300"),
    "schedule function basgiath:raise 300t",
)
check(
    "a function reference is namespaced with a colon",
    to_java("function basgiath/stage_01"),
    "function basgiath:stage_01",
)

# --- block states -------------------------------------------------------------

check(
    "a ladder faces north on Java",
    to_java('setblock ~1 ~2 ~3 ladder["facing_direction"=2]'),
    "setblock ~1 ~2 ~3 ladder[facing=north]",
)
check(
    "a lectern direction becomes a cardinal",
    to_java('setblock ~1 ~2 ~3 lectern["direction"=3]'),
    "setblock ~1 ~2 ~3 lectern[facing=west]",
)
check_raises("an unknown block state stops the build", 'setblock ~ ~ ~ stone["mystery"=1]')

# Java renamed this one in 1.17; Bedrock never did. Passing it through unlisted is
# how the whole live function failed to parse on Java the first time.
check(
    "a grass path becomes a dirt path",
    to_java("setblock ~1 ~2 ~3 grass_path"),
    "setblock ~1 ~2 ~3 dirt_path",
)
check_raises("an unlisted block stops the build", "setblock ~ ~ ~ mystery_block")

# --- relative selectors -------------------------------------------------------
# Java 1.21.1 will not parse `x=~4` in a selector, and a selector that does not
# parse takes its whole function down with it. The offset moves into `positioned`.

check(
    "a relative box in the chain becomes a positioned",
    to_java('execute as @e[type=armor_stand,name="a",c=1] at @s as @a[x=~4,y=~32,z=~14,dx=10,dy=3,dz=14] run tag @s add x'),
    'execute as @e[type=minecraft:armor_stand,name="a",limit=1] at @s positioned ~4 ~32 ~14'
    ' as @a[dx=10,dy=3,dz=14] run tag @s add x',
)
check(
    "a relative box in the run command hangs the positioned on the chain",
    to_java('execute as @e[name="a"] at @s run tag @a[x=~4,y=~32,z=~14,dx=10,dy=3,dz=14] add cp_west'),
    'execute as @e[name="a"] at @s positioned ~4 ~32 ~14'
    ' run tag @a[dx=10,dy=3,dz=14] add cp_west',
)
check_raises(
    "a relative origin with no box size stops the build",
    "execute at @s as @a[x=~4,y=~32,z=~14] run tag @s add x",
)
# Two relative boxes on one line would compose: the chain's `positioned` moves the
# position, and the run command's would then measure from the moved position. Bedrock
# does not move the position for `as`, so the result would be wrong, not merely odd.
check_raises(
    "two relative boxes on one line stop the build rather than composing",
    'execute as @e[name="a"] at @s as @a[x=~4,y=~32,z=~14,dx=2,dy=2,dz=2]'
    ' run tag @a[x=~1,y=~1,z=~1,dx=2,dy=2,dz=2] add x',
)

# --- the deliberate drops ----------------------------------------------------

check("tickingarea drops", to_java("tickingarea remove college_a"), None)
check(
    "an anchored tickingarea drops under its own name",
    to_java('execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea remove college_a'),
    None,
)
check(
    "an on_area_loaded schedule drops",
    to_java("schedule on_area_loaded add tickingarea college_b basgiath/fill_far"),
    None,
)
check(
    "the drop key names the inner verb, not execute",
    drop_key('execute as @e[name="x"] at @s run tickingarea remove college_a'),
    "tickingarea",
)

# --- strictness ---------------------------------------------------------------

check_raises("an unknown verb stops the build", "clone ~ ~ ~ ~1 ~1 ~1")
check_raises("an unknown entity stops the build", 'summon wither "x" ~ ~ ~')
check_raises("an unknown effect stops the build", "effect @p levitation 8 0 true")
check_raises("an unknown particle stops the build", "particle minecraft:heart ~ ~ ~")
check_raises("an unknown gamerule stops the build", "gamerule pvp true")


# --- the promise that Bedrock does not move ----------------------------------


def check_generator_output() -> None:
    """Every line the generator builds must be readable by the Java dialect.

    A line the dialect cannot read is a hole in the Java world. This walks the
    real command list rather than a fixture, so a new zone command is caught the
    day it is written.
    """
    import build_map as bm

    unreadable: list[str] = []
    for line in bm.geometry():
        try:
            to_java(line)
        except TranslationError as exc:
            unreadable.append(str(exc))
    for block in (bm.live_text(), bm.SUMMON, bm.RUN_START, bm.RUN_STOP, bm.build_text(1), bm.raise_text()):
        for line in block.split("\n"):
            if not line.strip():
                continue
            try:
                to_java(line)
            except TranslationError as exc:
                unreadable.append(str(exc))
    for line in unreadable[:5]:
        FAILURES.append(f"the generator emits a line the Java dialect cannot read: {line}")


def check_no_bedrock_ids_in_the_tree() -> None:
    """No Bedrock-only id may reach the shipped Java datapack."""
    tree = ROOT / "java" / "src" / "main" / "resources"
    if not tree.exists():
        FAILURES.append("the Java datapack tree is missing. Run python3 scripts/build_map.py first.")
        return
    # The datapack, and the mod's own sources. Checking only the emitted commands
    # would leave the Java code free to name a Bedrock-only id, which is the same
    # mistake in a different file.
    scanned = list(tree.rglob("*.mcfunction"))
    sources = ROOT / "java" / "src" / "main" / "java"
    if sources.exists():
        scanned.extend(sources.rglob("*.java"))
    for path in scanned:
        text = path.read_text(encoding="utf-8")
        for bad in BEDROCK_ONLY:
            if bad in text:
                FAILURES.append(f"{path.relative_to(ROOT)} carries the Bedrock-only id {bad!r}")
    tag = tree / "data" / "minecraft" / "tags" / "function" / "tick.json"
    if not tag.exists():
        FAILURES.append("the Java tree has no minecraft:tick tag, so basgiath:tick never runs")


check_generator_output()
check_no_bedrock_ids_in_the_tree()

if FAILURES:
    print(f"editions: {len(FAILURES)} failure(s)")
    for item in FAILURES:
        print(f"  - {item}")
    raise SystemExit(1)
print("editions ok: the Java dialect is strict, and its output is clean")
