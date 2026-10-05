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
import math
import re
import subprocess
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
# Every command class that places blocks. A class this parser cannot read is a
# blind spot in the walk and parapet checks, so it fails the bench instead of
# being skipped.
BLOCK_COMMANDS = {"setblock", "fill", "clone", "structure", "place"}
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
    """The x/z box of a plain or execute-wrapped positional command, else None.

    Three plain forms: ``setblock``, ``fill``, ``summon``. A wrapped command
    such as ``execute as @e[…] run setblock ~200 ~1 ~200 stone`` names no box
    until the leading ``execute … run `` is stripped, so the tail is parsed.
    The last `` run `` wins. ``assert_far_retry`` still verifies the retry by
    string comparison, so a form this parser cannot see cannot hide here.
    """
    head, _, tail = line.rpartition(" run ")
    parts = (tail if head else line).split()
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
    """Replay setblock and fill. Later commands replace earlier ones.

    A block-placing command this parser cannot read would be invisible to the
    walk and parapet checks, so it fails the bench loudly instead of being
    skipped.
    """
    blocks: dict[tuple[int, int, int], str] = {}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts[0] not in BLOCK_COMMANDS:
            continue
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
            fail(f"solid_blocks cannot read a positional command: {line}")
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
    # The inverse: the ground the span crosses must not be walkable at foot
    # height, or a player walks under the span instead of across it.
    if _reachable(
        blocks,
        START,
        lambda x, y, z: y <= 1 and 15 <= x <= 77 and 12 <= z <= 28,
    ):
        fail("a ground-level walk from the start still crosses the chasm")
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
    expect_fail(
        lines + ["fill ~15 ~-1 ~12 ~77 ~1 ~28 air"],
        "the chasm floor was carved back down to ground level",
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


def prove_parser() -> None:
    """Prove the parser classifies a synthetic wrapped positional command.

    The wrapped form is the known edge: ``_box()`` returned None for it once,
    so ``is_far()`` could not see the command. The fixture is a build anchor
    near the origin whose wrapped setblock lands far outside the loaded box.
    It fails if the parser regresses to the plain three forms only.
    """
    wrapped = (
        'execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run '
        "setblock ~200 ~1 ~200 stone"
    )
    if _box(wrapped) != (200, 200, 200, 200):
        fail(f"the parser cannot see a wrapped positional command: {wrapped}")
    if not is_far(wrapped):
        fail(f"the parser did not classify a far wrapped command: {wrapped}")
    print("proof ok: a wrapped positional command is classified as far")


# The keeper lookup lives in main.js. This harness loads the real script with
# the two @minecraft modules stubbed, so the shipped interact handler runs
# against synthetic entities. It proves the anchor is resolved with Math.floor
# and that a keeper coordinate is compared as origin + relative, not bare. A
# substring check cannot prove the second part: a script that still compares
# bare coordinates would pass it.
KEEPER_PROOF = r"""
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const MAIN = "__MAIN__";
const OFFSET = __OFFSET__;
const KEEPER_BLOCKS = __KEEPERS__;
const ANCHOR = { x: 12.75, y: 70.25, z: -4.5 };
const MOVED = { x: 40.5, y: 80.9, z: 7.25 };
const require = createRequire(import.meta.url);
const errors = [];
const pending = [];
const timed = [];
let interact = null;
const anchor = {
  entity: { nameTag: "build_anchor", location: ANCHOR },
};
let messages = [];

const check = (ok, detail) => {
  if (!ok) errors.push(detail);
};

const isReal = (spec) => {
  try {
    require(spec);
    return true;
  } catch (err) {
    return false;
  }
};

function buildModule() {
  return new vm.SourceTextModule(readFileSync(MAIN, "utf8"), { identifier: MAIN });
}

function stubModule() {
  return new vm.SyntheticModule(
    ["world", "system", "ActionFormData", "MessageFormData", "ModalFormData"],
    function () {
      this.setExport("world", world);
      this.setExport("system", system);
      this.setExport("ActionFormData", forms.ActionFormData);
      this.setExport("MessageFormData", forms.MessageFormData);
      this.setExport("ModalFormData", forms.ModalFormData);
    }
  );
}

class FakePlayer {
  constructor(input, name) {
    this.input = input;
    this.name = name;
    this.id = name;
    this.tags = new Set();
    this.props = new Map();
    this.log = [];
    this.onScreenDisplay = { setTitle: () => {} };
  }
  sendMessage(text) { this.log.push(String(text)); }
  getDynamicProperty(key) { return this.props.get(key); }
  setDynamicProperty(key, value) { this.props.set(key, value); }
  hasTag(tag) { return this.tags.has(tag); }
  addTag(tag) { this.tags.add(tag); }
  removeTag(tag) { this.tags.delete(tag); }
}

const forms = {
  ModalFormData: class {
    constructor() { this.fields = []; }
    title(text) { this.formTitle = text; return this; }
    textField(label, placeholder) { this.fields.push([label, placeholder]); return this; }
    show(player) {
      forms.seen.push({ title: this.formTitle, fields: this.fields, player });
      return Promise.resolve({ canceled: false, formValues: [player.input] });
    }
  },
  ActionFormData: class {
    title() { return this; }
    body() { return this; }
    button() { return this; }
    show() { return Promise.resolve({ canceled: true }); }
  },
  MessageFormData: class {
    title() { return this; }
    body() { return this; }
    button1() { return this; }
    button2() { return this; }
    show() { return Promise.resolve({ canceled: true }); }
  },
};
forms.seen = [];

const world = {
  beforeEvents: { playerInteractWithBlock: { subscribe: (fn) => { interact = fn; } } },
  afterEvents: { scriptEventReceive: { subscribe: () => {} } },
  sendMessage: (text) => { messages.push(String(text)); },
  getDynamicProperty: () => undefined,
  setDynamicProperty: () => {},
  getDimension: () => ({ getEntities: () => (anchor.entity ? [anchor.entity] : []) }),
  getPlayers: () => [],
  runCommand: () => {},
};

const system = {
  run: (fn) => { pending.push(fn); },
  runTimeout: (fn, ticks) => { timed.push({ fn, ticks }); return timed.length; },
  clearRunTimeout: (handle) => {
    const entry = timed[handle - 1];
    if (entry) entry.cancelled = true;
  },
  runInterval: () => 0,
  afterEvents: { scriptEventReceive: { subscribe: () => {} } },
};

const settle = () => new Promise((resolve) => setImmediate(resolve));

const flush = async () => {
  const queued = pending.splice(0);
  await Promise.all(queued.map((fn) => Promise.resolve().then(fn)));
  await settle();
};

const eventAt = async (block, player) => {
  const event = {
    isFirstEvent: true,
    player,
    block: { typeId: "minecraft:lectern", location: block },
    cancel: false,
  };
  interact(event);
  await flush();
  return event;
};

const absolute = (block, origin) => ({
  x: origin.x + block.x,
  y: origin.y + block.y,
  z: origin.z + block.z,
});

const main = buildModule();
await main.link((spec) => (isReal(spec) ? require(spec) : stubModule()));
await main.evaluate();

async function run() {
  check(typeof interact === "function", "main.js did not subscribe to playerInteractWithBlock");
  if (typeof interact !== "function") return;

  check(
    OFFSET.x === 12 && OFFSET.y === 70 && OFFSET.z === -5,
    `the origin is floored to ${JSON.stringify(OFFSET)}, not (12, 70, -5)`
  );

  const player = new FakePlayer("Rider", "rider");
  // The roll keeper gates on the bond tag. The fixture carries it so both
  // keeper forms open; the gate itself is not what this proof tests.
  player.addTag("bonded");
  for (const [id, block] of Object.entries(KEEPER_BLOCKS)) {
    const at = absolute(block, OFFSET);
    forms.seen.length = 0;
    const event = await eventAt(at, player);
    check(event.cancel, `${id} lectern at ${JSON.stringify(at)} was not cancelled`);
    check(forms.seen.length === 1, `${id} lectern at ${JSON.stringify(at)} opened ${forms.seen.length} forms`);
    const title = forms.seen[0]?.title;
    const want = id === "scroll" ? "The scroll" : "The roll";
    check(title === want, `${id} lectern opened ${JSON.stringify(title)}, not ${JSON.stringify(want)}`);
  }

  // The pre-fix comparison. A bare keeper coordinate is not the keeper once
  // the build anchor sits off the origin, so the click must fall through.
  const bare = KEEPER_BLOCKS.scroll;
  forms.seen.length = 0;
  const stale = await eventAt(bare, player);
  check(!stale.cancel, "a bare keeper coordinate opened a form at a non-origin anchor");
  check(forms.seen.length === 0, `the bare keeper coordinate opened ${forms.seen.length} forms`);

  // A moved anchor must move the keeper with it. A cached origin fails here.
  anchor.entity = { nameTag: "build_anchor", location: MOVED };
  const moved = absolute(KEEPER_BLOCKS.scroll, {
    x: Math.floor(MOVED.x),
    y: Math.floor(MOVED.y),
    z: Math.floor(MOVED.z),
  });
  forms.seen.length = 0;
  const shifted = await eventAt(moved, player);
  check(shifted.cancel && forms.seen.length === 1, `the keeper did not follow the moved anchor to ${JSON.stringify(moved)}`);
  forms.seen.length = 0;
  const old = await eventAt(bare, player);
  check(!old.cancel, "the keeper stayed at the previous anchor position");
  anchor.entity = { nameTag: "build_anchor", location: ANCHOR };

  // The roll keeper takes the dragon name, so it must not read the rider roll.
  const rollAt = absolute(KEEPER_BLOCKS.roll, OFFSET);
  timed.length = 0;
  await eventAt(rollAt, player);
  check(timed.length === 0, "the roll keeper scheduled a rider roll call");
  check(!player.hasTag("rollcall_done"), "the roll keeper stamped the rider roll-call tag");

  // Naming at the scroll desk. One naming, one roll line, carrying the name.
  const scrollAt = absolute(KEEPER_BLOCKS.scroll, OFFSET);
  messages = [];
  timed.length = 0;
  await eventAt(scrollAt, player);
  const writeLine = player.log.filter((line) => line.includes("The scribe writes it down"));
  check(writeLine.length === 1, `the write message did not fire exactly once: ${writeLine.length}`);
  check(writeLine[0]?.includes("Stand in your row."), `the first write message is wrong: ${writeLine[0]}`);
  check(!messages.some((line) => line.includes("Roll call.")), "the roll call fired before the three-second beat");
  check(timed.length === 1, `the scroll keeper scheduled ${timed.length} timeouts, not 1`);
  const beat = timed.splice(0)[0];
  check(beat?.ticks === 60, `the roll call was scheduled for ${beat?.ticks} ticks, not 60`);
  beat?.fn();
  const calls = messages.filter((line) => line.includes("Roll call."));
  check(calls.length === 1, `one naming produced ${calls.length} roll-call lines, not 1`);
  check(calls[0]?.includes("Roll call. §fRider§7"), `the roll-call line does not carry the name: ${calls[0]}`);
  check(player.hasTag("rollcall_done"), "the roll call did not stamp the once-per-life tag");

  // The tag gates the read: the same beat run again must stay silent.
  messages = [];
  beat?.fn();
  check(messages.length === 0, `a repeat read repeated the roll call: ${messages[0]}`);

  // The rename path: the old name is struck, the tag is cleared, and the new
  // name is read at the next call.
  player.input = "Rider Two";
  messages = [];
  timed.length = 0;
  player.log = [];
  await eventAt(scrollAt, player);
  const strike = player.log.filter((line) => line.includes("strikes the old name"));
  check(strike.length === 1, `the rename message did not fire exactly once: ${strike.length}`);
  check(!player.hasTag("rollcall_done"), "a rename left the roll-call tag set");
  const second = timed.splice(0)[0];
  check(second?.ticks === 60, `the rename scheduled ${second?.ticks} ticks, not 60`);
  second?.fn();
  const renamed = messages.filter((line) => line.includes("Roll call."));
  check(renamed.length === 1, `the rename produced ${renamed.length} roll-call lines, not 1`);
  check(renamed[0]?.includes("§fRider Two§7"), `the rename roll-call line is wrong: ${renamed[0]}`);

  // Two quick writes inside the beat must leave one live callback. The second
  // write cancels the first timeout instead of stacking a second read.
  player.input = "Rider Three";
  timed.length = 0;
  await eventAt(scrollAt, player);
  player.input = "Rider Four";
  await eventAt(scrollAt, player);
  const live = timed.filter((entry) => !entry.cancelled);
  check(timed.length === 2, `two quick writes scheduled ${timed.length} timeouts, not 2`);
  check(live.length === 1, `two quick writes left ${live.length} live callbacks, not 1`);
  messages = [];
  live[0]?.fn();
  const finalCalls = messages.filter((line) => line.includes("Roll call."));
  check(finalCalls.length === 1, `the surviving callback produced ${finalCalls.length} roll-call lines`);
  check(finalCalls[0]?.includes("§fRider Four§7"), `the surviving roll-call line is wrong: ${finalCalls[0]}`);

  // No dynamic property, no call. The test bypass opens the path with no name.
  const stranger = new FakePlayer("", "stranger");
  messages = [];
  timed.length = 0;
  await eventAt(scrollAt, stranger);
  check(!stranger.hasTag("rollcall_done"), "an empty name stamped the roll-call tag");
  check(timed.length === 0, "an empty name scheduled a roll call");

  if (errors.length) {
    for (const line of errors) console.error(`keeper proof failed: ${line}`);
    process.exit(1);
  }
  console.log("proof ok: the keeper lookup floors the anchor and adds the relative block");
  console.log("proof ok: naming at the scroll desk yields one roll-call line with the name");
}

await run();
"""


def keeper_source() -> tuple[dict[str, dict[str, int]], dict[str, int]]:
    """Read the keeper blocks and the floored origin out of main.js.

    The harness must not hard-code the numbers under test, or it would agree
    with any wrong table. The coordinates come from the shipped script; the
    harness only supplies an off-origin anchor and asserts the floor.
    """
    script = (ROOT / "addon/behavior_pack/scripts/main.js").read_text(encoding="utf-8")
    table = re.search(r"const KEEPERS = \[(.*?)\n\];", script, re.S)
    if not table:
        fail("main.js has no KEEPERS table to prove")
    keepers: dict[str, dict[str, int]] = {}
    for entry in re.finditer(
        r'id:\s*"(\w+)".*?block:\s*\{\s*x:\s*(-?\d+),\s*y:\s*(-?\d+),\s*z:\s*(-?\d+)\s*\}',
        table.group(1),
        re.S,
    ):
        keepers[entry.group(1)] = {
            "x": int(entry.group(2)),
            "y": int(entry.group(3)),
            "z": int(entry.group(4)),
        }
    if sorted(keepers) != ["roll", "scroll"]:
        fail(f"main.js keeper table is {sorted(keepers)}, not the two keepers")
    if not re.search(
        r"function buildOrigin\(\)\s*\{.*?Math\.floor\(\s*e\.location\.x\s*\)",
        script,
        re.S,
    ):
        fail("main.js has no buildOrigin() that floors the anchor location")
    # The probe anchor (12.75, 70.25, -4.5) floors to (12, 70, -5). floor, not
    # int(): a negative coordinate truncates toward zero there.
    return keepers, {
        "x": math.floor(12.75),
        "y": math.floor(70.25),
        "z": math.floor(-4.5),
    }


def prove_keeper_origin() -> None:
    """Run the shipped keeper handler against a synthetic, off-origin anchor.

    The generator writes anchor-relative commands, so a keeper comparison that
    ignores the anchor agrees with the world only when the player stood on the
    origin. The Bedrock bench summons its anchor at (0, 80, 0) and probes
    blocks, so it cannot see that. This loads the real main.js with the two
    @minecraft modules stubbed and drives the real interact subscription.
    """
    keepers, offset = keeper_source()
    script = ROOT / "addon/behavior_pack/scripts/main.js"
    source = (
        KEEPER_PROOF.replace("__OFFSET__", json.dumps(offset))
        .replace("__KEEPERS__", json.dumps(keepers))
        .replace("__MAIN__", str(script))
    )
    result = subprocess.run(
        ["node", "--experimental-vm-modules", "--input-type=module", "-e", source],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        # Node prints an ExperimentalWarning for vm modules on stderr. Keep the
        # first line that is not that warning, so the failure names the check.
        detail = [
            line
            for line in (result.stderr or result.stdout).splitlines()
            if line.strip()
            and "ExperimentalWarning" not in line
            and "trace-warnings" not in line
        ]
        fail(f"keeper origin proof failed: {detail[0] if detail else 'no output'}")
    for line in result.stdout.strip().splitlines():
        print(line)


def main() -> None:
    lines = phone_lines()
    prove_guard(stage_lines(), far_lines())
    prove_parser()
    prove_keeper_origin()
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
