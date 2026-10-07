#!/usr/bin/env python3
"""Two command dialects from one generator.

The zones emit Bedrock command text. Bedrock is the **source dialect**: every
command this generator builds is written for Bedrock first, and the Java edition
is a translation of that same command list. The Bedrock output therefore stays
byte-identical to what already ships, which means the Java port cannot break the
Bedrock release. That is the whole reason the translation sits at the end of the
pipeline instead of inside the zones.

`to_java` is strict. A command it cannot read stops the build. A silent drop
would ship a Java world with holes in it, and a hole is much harder to find in
the game than it is here.

Java target: Minecraft 1.21.1, NeoForge 21.1.256. See docs/JAVA-PORT-PROMPT.md.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

# The Java namespace is the mod id. Bedrock ships the entity under
# dragon_rider:dragon; a Java entity id must be namespaced to the mod, so the
# entity becomes basgiath:dragon. This is the one deliberate id divergence.
JAVA_NAMESPACE = "basgiath"

ENTITY_MAP = {
    "armor_stand": "minecraft:armor_stand",
    "minecraft:armor_stand": "minecraft:armor_stand",
    "dragon_rider:dragon": f"{JAVA_NAMESPACE}:dragon",
}

# Every block id the generator emits is listed here, so an id that is not listed
# stops the build rather than being passed through on the assumption that the two
# editions agree. They mostly do, and `grass_path` is the exception that proves
# the point: Bedrock has kept the old name since 1.17 and Java has not.
#
# `SAME_BLOCK` is the set Java spells identically. `BLOCK_RENAME` is the set it
# does not. An id in neither is a build failure.
SAME_BLOCK = frozenset({
    "air", "allium", "azure_bluet", "bell", "black_wool", "chain",
    "chiseled_stone_bricks", "cobblestone", "cornflower", "cyan_wool",
    "dandelion", "glass", "granite", "grass_block", "ladder", "lantern",
    "lectern", "light_blue_stained_glass", "light_blue_wool",
    "light_gray_wool", "lily_of_the_valley", "lime_wool", "lodestone",
    "moss_block", "oak_leaves", "oak_log", "oak_planks", "oak_stairs",
    "oak_wood", "orange_wool", "oxeye_daisy", "polished_andesite",
    "polished_blackstone", "poppy", "purple_wool", "red_wool",
    "sea_lantern", "short_grass", "smooth_stone", "stone",
    "stone_brick_stairs", "stone_brick_wall", "stone_bricks",
    "stone_pressure_plate", "white_wool", "yellow_wool",
})

BLOCK_RENAME = {
    # Java renamed this in 1.17. Bedrock never did.
    "grass_path": "dirt_path",
}

GAMERULE_MAP = {
    "dodaylightcycle": "doDaylightCycle",
    "doweathercycle": "doWeatherCycle",
    "domobspawning": "doMobSpawning",
    "keepinventory": "keepInventory",
    "sendcommandfeedback": "sendCommandFeedback",
    "commandblockoutput": "commandBlockOutput",
    "doimmediaterespawn": "doImmediateRespawn",
}

PARTICLE_MAP = {
    "minecraft:basic_smoke_particle": "minecraft:smoke",
}

EFFECT_MAP = {
    "invisibility": "minecraft:invisibility",
    "resistance": "minecraft:resistance",
    "slow_falling": "minecraft:slow_falling",
}

# Bedrock block states as Java block states. The two editions disagree on the
# key name and, for a direction, on the value too.
#
# `facing_direction` is Bedrock's six-way state: 0 down, 1 up, 2 north, 3 south,
# 4 west, 5 east. Java has no six-way equivalent, and the generator only ever
# emits the horizontal cases for a wall-mounted block, so those four translate.
#
# `direction` is Bedrock's four-way state on blocks such as the lectern. The
# dorms table that writes it is documented as 1-based compass and shifted down,
# so 0 north, 1 east, 2 south, 3 west. The value passes through as a cardinal.
#
# Both tables are worth a look in the game rather than on paper: a wrong facing
# is cosmetic, and it is not visible in a static check.
STATE_MAP: dict[str, tuple[str, dict[str, str] | None]] = {
    "facing_direction": (
        "facing",
        {"2": "north", "3": "south", "4": "west", "5": "east"},
    ),
    "direction": (
        "facing",
        {"0": "north", "1": "east", "2": "south", "3": "west"},
    ),
}

# Commands whose meaning Java has no equivalent for. Dropping one is a decision,
# not an oversight, so every drop is recorded here with its reason.
DROPPED = {
    "tickingarea": "Java has no ticking areas. Chunk loading follows the player, "
    "and the build already teleports the player to load the far chunks.",
    "schedule:on_area_loaded": "Java cannot schedule on an area load. The far pass "
    "still runs: `open` calls every far stage after the player is moved.",
}


class TranslationError(SystemExit):
    """A command the Java dialect cannot read. Stops the build."""


_TOKEN_RE = re.compile(r'"[^"\\]*(?:\\.[^"\\]*)*"|\[[^\]]*\]|\{[^}]*\}|\S+')
_SELECTOR_RE = re.compile(r"@[a-z]\[[^\]]*\]")
_TYPE_ARG_RE = re.compile(r"type=([a-z_0-9:]+)")

# Ids that belong to Bedrock only. One of these reaching the Java tree means a
# rewrite was missed, and the usual result is a command that silently does
# nothing, or one that fires every tick.
BEDROCK_ONLY = ("dragon_rider:",)


def _tokens(text: str) -> list[str]:
    """Split on spaces, keeping quoted strings and [..] / {..} groups whole."""
    return _TOKEN_RE.findall(text)


def _join(tokens: list[str]) -> str:
    return " ".join(tokens)


def _split_relative_box(token: str) -> tuple[str | None, str]:
    """Pull a relative box out of a selector.

    Bedrock accepts relative coordinates in a selector: ``@a[x=~4,y=~32,z=~14,
    dx=10,dy=3,dz=14]`` means "a box 10 by 3 by 14, starting four blocks east and
    so on from here". Java 1.21.1 rejects the ``~`` and fails to parse the command,
    which takes the whole function down at load time.

    Java reaches the same box a different way: set the execution position with
    ``positioned``, then let a bare ``dx,dy,dz`` selector measure from it. So the
    offset moves out of the selector and into the execute chain.

    Returns (the offset as a ``positioned`` suffix, or None, and the rewritten
    selector). A relative box with no ``dx``/``dy``/``dz`` stops the build: a
    degenerate box has no Java equivalent worth guessing at.
    """
    head, sep, body = token.partition("[")
    if not sep or not token.startswith("@"):
        return None, token
    options = body.rstrip("]").split(",")
    offset: dict[str, str] = {}
    kept: list[str] = []
    for option in options:
        key, _, value = option.partition("=")
        if key in ("x", "y", "z") and value.startswith("~"):
            offset[key] = value
        else:
            kept.append(option)
    if not offset:
        return None, token
    missing = [axis for axis in ("x", "y", "z") if axis not in offset]
    if missing:
        raise TranslationError(
            f"the selector {token!r} gives a relative {offset} without the "
            f"missing {missing}. A partly relative box cannot be hoisted."
        )
    if not any(option.partition("=")[0] in ("dx", "dy", "dz") for option in kept):
        raise TranslationError(
            f"the selector {token!r} gives a relative origin but no dx/dy/dz, so "
            "the box it means is ambiguous. Java cannot express it."
        )
    positioned = f"positioned {offset['x']} {offset['y']} {offset['z']}"
    rewritten = head + ("[" + ",".join(kept) + "]" if kept else "")
    return positioned, rewritten


_CHAIN_SELECTOR_RE = re.compile(r"\b(as|at)\s+(@[a-z]\[[^\]]*\])")


def _hoist_in_chain(prefix: str) -> tuple[bool, str]:
    """Rewrite an execute chain, putting ``positioned`` before each relative box.

    The rewrite is a substitution over the selectors themselves, not a re-tokenise
    and re-join. A re-join would put spaces back into anything it did not parse
    cleanly, and NBT is not whitespace-tolerant in the places that matters.

    Returns (whether anything was hoisted, the rewritten chain).
    """
    hoisted = False

    def replace(match: re.Match[str]) -> str:
        nonlocal hoisted
        keyword, selector = match.group(1), match.group(2)
        positioned, rewritten = _split_relative_box(selector)
        if positioned is None:
            return match.group(0)
        hoisted = True
        # `positioned` belongs before the `as`/`at` it feeds, so the selector still
        # measures from the position it saw.
        return f"{positioned} {keyword} {rewritten}"

    # The substitution must run before `hoisted` is read: a tuple is built left to
    # right, so `return hoisted, sub(...)` would report the value from before the work.
    rewritten = _CHAIN_SELECTOR_RE.sub(replace, prefix)
    return hoisted, rewritten


def _extract_from_command(command: str) -> tuple[str, str | None]:
    """Strip relative boxes out of a run command.

    A ``positioned`` cannot go inside a run command, so the offset comes out and
    the caller appends it to the end of the execute chain, one step before ``run``.
    That is the position the selector would otherwise have measured from.
    """
    positioned: str | None = None

    def replace(match: re.Match[str]) -> str:
        nonlocal positioned
        offset, rewritten = _split_relative_box(match.group(0))
        if offset is not None:
            positioned = offset
        return rewritten

    return _SELECTOR_RE.sub(replace, command), positioned


def _java_selectors(text: str) -> str:
    """Rewrite the selectors in a command for Java.

    Two rewrites, both of which bite silently if they are missed:

    - Bedrock `c=N` is Java `limit=N`. An untranslated `c=` makes the selector
      throw at run time.
    - A `type=` argument carries an entity id, and an entity id is namespaced.
      `unless entity @e[type=dragon_rider:dragon]` guards the dragon summon. Left
      alone on Java the guard never matches anything, so it is always true, and
      the dragon is summoned again on every single tick.
    """

    def fix(match: re.Match[str]) -> str:
        body = re.sub(r"(?<=[,\[])c=(\d+)", r"limit=\1", match.group(0))

        def entity(inner: re.Match[str]) -> str:
            current = inner.group(1)
            return "type=" + ENTITY_MAP.get(current, current)

        return _TYPE_ARG_RE.sub(entity, body)

    return _SELECTOR_RE.sub(fix, text)


def _java_block(token: str) -> str:
    """A block token, plus its states if it carries any.

    Bedrock states are `block["key"=value]` or `block["key"==value]`. Java states
    are `block[key=value]`. The two editions disagree on key names far more than
    on values, so an unmapped key stops the build instead of being guessed at.
    """
    name, sep, rest = token.partition("[")
    name = _check_block(name, token)
    if not sep:
        return name
    states = []
    for part in rest.rstrip("]").split(","):
        if not part:
            continue
        key, _, value = part.partition("==")
        if not _:
            key, _, value = part.partition("=")
        key = key.strip().strip('"')
        if key not in STATE_MAP:
            raise TranslationError(
                f"the Java dialect has no mapping for block state {key!r} in {token!r}. "
                "Add it to STATE_MAP in scripts/editions.py."
            )
        java_key, value_map = STATE_MAP[key]
        if value_map is not None:
            if value not in value_map:
                raise TranslationError(
                    f"the Java dialect has no mapping for {key}={value} in {token!r}. "
                    "Add it to STATE_MAP in scripts/editions.py."
                )
            value = value_map[value]
        states.append(f"{java_key}={value}")
    return f"{name}[{','.join(states)}]"


def _check_block(name: str, token: str) -> str:
    """The Java name for a block id, or a stop.

    An unlisted id is treated as an unknown, not as an id that happens to match.
    That is the difference between this catching `grass_path` at build time and
    the function failing to parse in the game.
    """
    if name in BLOCK_RENAME:
        return BLOCK_RENAME[name]
    if name in SAME_BLOCK:
        return name
    raise TranslationError(
        f"the Java dialect has no mapping for the block {name!r} in {token!r}. "
        "Add it to SAME_BLOCK if Java spells it the same, or to BLOCK_RENAME if it "
        "does not. See scripts/editions.py."
    )


def _java_text(payload: str) -> str:
    """A Bedrock `{"rawtext":[..]}` payload as a Java text component.

    Java takes the component, or an array of components, directly. A lone text
    part collapses to `{"text":".."}`. A part carrying `score` is already
    identical on both editions.
    """
    try:
        doc = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise TranslationError(f"not readable as JSON text: {payload!r} ({exc})") from exc
    if not isinstance(doc, dict) or "rawtext" not in doc:
        return payload
    parts = doc["rawtext"]
    if len(parts) == 1 and set(parts[0]) == {"text"}:
        return json.dumps(parts[0], ensure_ascii=False, separators=(",", ":"))
    return json.dumps(parts, ensure_ascii=False, separators=(",", ":"))


def _java_function(name: str) -> str:
    """`basgiath/stage_01` is Java `basgiath:stage_01`."""
    if "/" not in name:
        raise TranslationError(f"not a namespaced function: {name!r}")
    namespace, _, path = name.partition("/")
    return f"{namespace}:{path}"


def _inner(line: str) -> tuple[str, str]:
    """Split `execute <prefix> run <command>` into (prefix, command).

    The split is on the first top-level `run` token. A `run` inside a selector's
    quoted name, or inside a JSON payload, is part of a larger token and is never
    seen here.
    """
    tokens = _tokens(line)
    if not tokens or tokens[0] != "execute":
        return "", line
    for index, token in enumerate(tokens):
        if index and token == "run":
            return _join(tokens[1:index]), _join(tokens[index + 1 :])
    raise TranslationError(f"an execute with no run: {line!r}")


def to_java(line: str) -> str | None:
    """One Bedrock command as its Java equivalent. None means Java has no form for it."""
    prefix, command = _inner(line)
    tokens = _tokens(command)
    if not tokens:
        return None
    verb, args = tokens[0], tokens[1:]

    out: str | None

    if verb in ("setblock", "fill"):
        # Same argument order on both editions: coordinates, then the block.
        if verb == "setblock":
            if len(args) < 4:
                raise TranslationError(f"short setblock: {line!r}")
            out = _join([verb, *args[:3], _java_block(args[3])])
        else:
            if len(args) < 7:
                raise TranslationError(f"short fill: {line!r}")
            out = _join([verb, *args[:6], _java_block(args[6])])

    elif verb in ("scoreboard", "tag", "spawnpoint", "tp", "weather", "gamemode", "time", "kill"):
        # Identical on both editions. kill @e[type=armor_stand] resolves the
        # default minecraft namespace on Java, so it needs no rewrite.
        out = command

    elif verb == "summon":
        out = _summon(line, args)

    elif verb == "tellraw":
        if len(args) < 2:
            raise TranslationError(f"short tellraw: {line!r}")
        out = _join([verb, args[0], _java_text(_join(args[1:]))])

    elif verb == "titleraw":
        out = _titleraw(line, args)

    elif verb == "gamerule":
        if len(args) != 2:
            raise TranslationError(f"unexpected gamerule shape: {line!r}")
        key = GAMERULE_MAP.get(args[0].lower())
        if key is None:
            raise TranslationError(
                f"the Java dialect has no gamerule mapping for {args[0]!r}. "
                "Add it to GAMERULE_MAP in scripts/editions.py."
            )
        out = _join([verb, key, args[1]])

    elif verb == "function":
        out = _join([verb, _java_function(args[0])])

    elif verb == "particle":
        out = _particle(line, args)

    elif verb == "effect":
        out = _effect(line, args)

    elif verb == "schedule":
        out = _schedule(line, args)

    elif verb == "tickingarea":
        out = None  # recorded in DROPPED

    else:
        raise TranslationError(
            f"the Java dialect does not know the command {verb!r} in {line!r}. "
            "Teach it in scripts/editions.py, or the Java jar ships without it."
        )

    if out is None:
        return None

    # Java cannot read a relative coordinate inside a selector, so each one moves
    # into a `positioned` on the execute chain. A relative box in the run command
    # has no chain of its own, so its offset joins the end of the chain instead.
    out, from_command = _extract_from_command(out)
    if prefix:
        hoisted, prefix = _hoist_in_chain(prefix)
        if from_command:
            if hoisted:
                # A relative box in the chain moves the execution position, and a
                # relative box in the run command would then measure from the moved
                # position. Bedrock does not move the position for `as`, so the run
                # box is relative to where the chain started. Appending the second
                # offset would apply it twice. The generator does not produce this
                # today; if it ever does, it must be thought about rather than
                # silently mistranslated.
                raise TranslationError(
                    f"both the execute chain and its run command carry a relative "
                    f"selector box, and the two would compose. Split the line, or "
                    f"teach the dialect which position the run box means. Line: {line!r}"
                )
            prefix = f"{prefix} {from_command}"
        return f"execute {_java_selectors(prefix)} run {_java_selectors(out)}"
    if from_command:
        return f"execute {from_command} run {_java_selectors(out)}"
    return _java_selectors(out)


def _summon(line: str, args: list[str]) -> str:
    """Bedrock names the entity inline; Java names it in NBT."""
    if not args:
        raise TranslationError(f"short summon: {line!r}")
    entity = ENTITY_MAP.get(args[0])
    if entity is None:
        raise TranslationError(
            f"the Java dialect has no entity mapping for {args[0]!r}. "
            "Add it to ENTITY_MAP in scripts/editions.py."
        )
    rest = list(args[1:])
    name = None
    if rest and rest[0].startswith('"'):
        name = rest[0].strip('"')
        rest = rest[1:]
    if len(rest) < 3:
        raise TranslationError(f"summon without coordinates: {line!r}")
    coords, tail = rest[:3], rest[3:]
    parts = [entity, *coords, *tail]
    if name is not None:
        # Java carries the name as a JSON text component, quoted inside the NBT string.
        parts.append("{CustomName:'" + json.dumps({"text": name}, ensure_ascii=False, separators=(",", ":")) + "'}")
    return _join(["summon", *parts])


def _titleraw(line: str, args: list[str]) -> str:
    """`titleraw` is Java `title`. `times` takes three bare numbers on both."""
    if len(args) < 2:
        raise TranslationError(f"short titleraw: {line!r}")
    target, mode = args[0], args[1]
    if mode not in ("title", "subtitle", "actionbar", "times"):
        raise TranslationError(f"unknown titleraw mode {mode!r} in {line!r}")
    if mode == "times":
        return _join(["title", target, "times", *args[2:]])
    if len(args) < 3:
        raise TranslationError(f"titleraw {mode} without text: {line!r}")
    return _join(["title", target, mode, _java_text(_join(args[2:]))])


def _particle(line: str, args: list[str]) -> str:
    """Java needs the spread, speed, and count that Bedrock leaves out."""
    if len(args) < 4:
        raise TranslationError(f"short particle: {line!r}")
    name = PARTICLE_MAP.get(args[0])
    if name is None:
        raise TranslationError(
            f"the Java dialect has no particle mapping for {args[0]!r}. "
            "Add it to PARTICLE_MAP in scripts/editions.py."
        )
    return _join(["particle", name, *args[1:4], "0", "0", "0", "0", "1", "normal"])


def _effect(line: str, args: list[str]) -> str:
    """Java spells it `effect give`, and namespaces the effect."""
    if len(args) < 2:
        raise TranslationError(f"short effect: {line!r}")
    name = EFFECT_MAP.get(args[1])
    if name is None:
        raise TranslationError(
            f"the Java dialect has no effect mapping for {args[1]!r}. "
            "Add it to EFFECT_MAP in scripts/editions.py."
        )
    return _join(["effect", "give", args[0], name, *args[2:]])


def _schedule(line: str, args: list[str]) -> str | None:
    """Java has one schedule form, and it counts in ticks with a `t` suffix."""
    if not args:
        raise TranslationError(f"short schedule: {line!r}")
    if args[0] == "delay":
        # schedule delay add <function> <ticks>
        if len(args) != 4 or args[1] != "add":
            raise TranslationError(f"unknown schedule delay shape: {line!r}")
        return _join(["schedule", "function", _java_function(args[2]), f"{args[3]}t"])
    if args[0] == "on_area_loaded":
        return None  # recorded in DROPPED
    raise TranslationError(f"unknown schedule form {args[0]!r} in {line!r}")


def drop_key(line: str) -> str:
    """What a dropped line was, named the same way DROPPED names it.

    A dropped command is usually wrapped in an `execute`, so the outer verb is
    always `execute`. The inner verb is the one that matters.
    """
    _, command = _inner(line)
    tokens = _tokens(command)
    if not tokens:
        return "empty"
    if tokens[0] == "schedule" and len(tokens) > 1:
        return f"schedule:{tokens[1]}"
    return tokens[0]


def java_lines(commands: list[str], where: str) -> tuple[list[str], dict[str, int]]:
    """Translate a command list. Returns (lines, drop counts).

    The drop counts are returned so the caller can print them. A dropped command
    is a deliberate edition difference, and it should be visible in the build log.
    """
    out: list[str] = []
    drops: dict[str, int] = {}
    for line in commands:
        java = to_java(line)
        if java is None:
            key = drop_key(line)
            drops[key] = drops.get(key, 0) + 1
            continue
        out.append(java)
    for key in drops:
        if key not in DROPPED:
            raise TranslationError(
                f"{where} dropped {key!r} with no recorded reason. "
                "Add it to DROPPED in scripts/editions.py."
            )
    return out, drops


def write_java_functions(root: Path, files: dict[str, str], tick_body: str) -> Path:
    """Write the Java datapack tree the mod ships.

    Datapack functions live under `data/<namespace>/function/`, and the tick loop
    is a function tag. Bedrock disables tick.json and lets the script drive
    basgiath/tick; Java uses the minecraft:tick tag to reach the same function.
    """
    base = root / "java" / "src" / "main" / "resources" / "data"
    target = base / JAVA_NAMESPACE / "function"
    target.mkdir(parents=True, exist_ok=True)
    for name, body in files.items():
        for bad in BEDROCK_ONLY:
            if bad in body:
                raise TranslationError(
                    f"{name} still carries the Bedrock-only id {bad!r}. "
                    "A rewrite in scripts/editions.py was missed, and that id "
                    "does not exist on Java."
                )
        (target / name).write_text(body, encoding="utf-8")
    # A stale stage from an earlier, longer build would stay on disk and run.
    wanted = set(files)
    for path in target.glob("*.mcfunction"):
        if path.name not in wanted:
            path.unlink()
    tag_dir = base / "minecraft" / "tags" / "function"
    tag_dir.mkdir(parents=True, exist_ok=True)
    (tag_dir / "tick.json").write_text(
        json.dumps({"values": [f"{JAVA_NAMESPACE}:{tick_body}"]}, indent=2) + "\n",
        encoding="utf-8",
    )
    return target
