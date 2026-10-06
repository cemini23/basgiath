#!/usr/bin/env python3
"""Check the map, the dragon, and the world zip. No Minecraft client required."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
def _phrase(*parts: str) -> str:
    return "".join(parts)


FORBIDDEN = (
    _phrase("fourth", " wing"),
    _phrase("empy", "rean"),
    _phrase("iron", " flame"),
    _phrase("onyx", " storm"),
    _phrase("dragon", "kind"),
    _phrase("xa", "den"),
    _phrase("violet", " sorrengail"),
    _phrase("yar", "ros"),
)
FILL = re.compile(
    r"^fill (~?-?\d*) (~?-?\d*) (~?-?\d*) (~?-?\d*) (~?-?\d*) (~?-?\d*) \S+"
)
# Character and dragon names must not appear in the docs either, not only in
# the shipped pack. The series titles and the author line are different: the
# label and listing copy carry them, and docs/IP-RULES.md rule 5 requires the
# author's name in the disclaimer, so those stay out of this list.
DOC_DENY = (
    _phrase("xa", "den"),
    _phrase("violet", " sorrengail"),
    _phrase("tair", "n"),
    _phrase("andar", "na"),
    _phrase("sgae", "yl"),
)
# The two reference docs exist to name what the ban forbids. They are the only
# files allowed to hold a denylist.
POLICY_DOCS = {"docs/CANON.md", "docs/IP-RULES.md"}
# The tag a cadet carries during a timed run. The course clock owns the action
# bar while it is set, and the flight readout stands down, so both names must
# be the same string.
COURSE_TAG_NAME = "timed_run"
REQUIRED_BONES = (
    "body",
    "head",
    "neck",
    "jaw",
    "wing_left",
    "wing_left_mid",
    "wing_left_tip",
    "wing_right",
    "wing_right_mid",
    "wing_right_tip",
    "tail",
    "tail_2",
    "tail_3",
    "tail_4",
    "leg_front_left",
    "leg_front_right",
    "leg_back_left",
    "leg_back_right",
)


def coord(token: str) -> int:
    if token == "~":
        return 0
    return int(token[1:])


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode != 0:
        fail(f"command failed: {' '.join(cmd)}")


def forbidden_in(path: Path) -> None:
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    for name in FORBIDDEN:
        if name in text:
            fail(f"forbidden name {name!r} in {path}")


def check_names() -> None:
    roots = [ROOT / "addon", ROOT / "scripts"]
    for root in roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in {".png", ".mcaddon", ".mcworld"}:
                continue
            forbidden_in(path)
    # A name pasted into the docs shipped unnoticed for five audits. Read the
    # top-level docs and docs/ too, skipping only the policy files that hold the
    # denylist on purpose.
    doc_paths = [
        ROOT / "README.md",
        ROOT / "DESIGN.md",
        ROOT / "BUILD_CHECKLIST.md",
        ROOT / "DISTRIBUTION.md",
    ]
    doc_paths.extend(sorted((ROOT / "docs").rglob("*")))
    for path in doc_paths:
        if not path.is_file():
            continue
        if path.suffix.lower() in {".png", ".mcaddon", ".mcworld"}:
            continue
        if path.relative_to(ROOT).as_posix() in POLICY_DOCS:
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for name in DOC_DENY:
            if name in text:
                fail(f"forbidden name {name!r} in {path}")


def _signed(token: str) -> int:
    if token == "~":
        return 0
    if token.startswith("~"):
        return int(token[1:])
    return int(token)


def gauntlet_box(name: str) -> tuple[int, int, int, int, int, int]:
    """Read a scoring-zone box straight out of the shipped zone module.

    The release check must not hard-code the numbers it verifies, or it would
    agree with any wrong copy. ``scripts`` is added temporarily because the
    generator runs with its own directory as the import root.
    """
    scripts = str(ROOT / "scripts")
    if scripts not in sys.path:
        sys.path.insert(0, scripts)
    try:
        from zones import gauntlet
        return getattr(gauntlet, name)()
    finally:
        if scripts in sys.path:
            sys.path.remove(scripts)


def emitted_lecterns(blob: str) -> set[tuple[int, int, int]]:
    """The cells whose last emitted setblock is a bare lectern.

    A lectern with a block state (the classroom desks) is not a keeper lectern,
    so only the final bare ``lectern`` at a cell counts. The map side is read
    from the commands alone; it never sees the keeper table.
    """
    final: dict[tuple[int, int, int], str] = {}
    for raw in blob.splitlines():
        parts = raw.strip().split()
        if len(parts) < 5 or parts[0] != "setblock":
            continue
        cell = (_signed(parts[1]), _signed(parts[2]), _signed(parts[3]))
        # Keep the block state in the value: a classroom lectern carries
        # [facing_direction=...] and is not a keeper lectern.
        final[cell] = " ".join(parts[4:])
    return {cell for cell, block in final.items() if block == "lectern"}


def keeper_blocks() -> set[tuple[int, int, int]]:
    """The KEEPERS[].block cells read straight out of main.js.

    The script side is parsed from the source, not from the emitted commands,
    so a drift between the table and the world cannot hide.
    """
    script = (ROOT / "addon/behavior_pack/scripts/main.js").read_text(encoding="utf-8")
    table = re.search(r"const KEEPERS = \[(.*?)\n\];", script, re.S)
    if not table:
        fail("main.js has no KEEPERS table")
    cells = set()
    for entry in re.finditer(
        r'id:\s*"(\w+)".*?block:\s*\{\s*x:\s*(-?\d+),\s*y:\s*(-?\d+),\s*z:\s*(-?\d+)\s*\}',
        table.group(1),
        re.S,
    ):
        cells.add((int(entry.group(2)), int(entry.group(3)), int(entry.group(4))))
    if not cells:
        fail("main.js KEEPERS table names no blocks")
    return cells


def check_map() -> None:
    functions = ROOT / "addon/behavior_pack/functions"
    tick = json.loads((functions / "tick.json").read_text())
    if tick.get("values") != []:
        fail(f"tick.json values are {tick.get('values')}")
    script = (ROOT / "addon/behavior_pack/scripts/main.js").read_text()
    if 'runCommand("function basgiath/tick")' not in script:
        fail("script does not run the map tick")
    if "beforeEvents.playerInteractWithBlock" not in script:
        fail("script does not subscribe to playerInteractWithBlock")
    for needle in (
        "dragon_rider:rider_name",
        "dragon_rider:dragon_name",
        'id: "scroll"',
        'id: "roll"',
        "ModalFormData",
    ):
        if needle not in script:
            fail(f"script is missing the keeper marker {needle!r}")
    # The generator writes anchor-relative commands, so a keeper comparison
    # that uses the bare table entry agrees with the world only when the build
    # anchor stands on the origin. The lookup must resolve the anchor and floor
    # it before it adds the relative block. scripts/bench_static.py runs the
    # handler against an off-origin anchor; this is the cheap source guard.
    if "build_anchor" not in script:
        fail("the keeper lookup does not resolve the build_anchor entity")
    if "function buildOrigin()" not in script or "Math.floor(" not in script:
        fail("the keeper lookup does not floor the anchor location")
    lookup = re.search(
        r"const keeper = KEEPERS\.find\((.*?)\n  \);", script, re.S
    )
    if not lookup or "origin." not in lookup.group(1):
        fail("the keeper lookup compares a block location without the origin")
    # The roll call reads the rider's own name and sends it with
    # world.sendMessage. A command string would parse the name.
    if 'const ROLLCALL_TAG = "rollcall_done"' not in script:
        fail("the roll call tag is missing or renamed")
    for needle in ("function readRollCall(", "world.sendMessage("):
        if needle not in script:
            fail(f"the roll call is missing {needle!r}")
    if "readRollCall(player)" not in script:
        fail("the scroll keeper never calls readRollCall")
    # A write hears the roll again, and the call is a separate beat. Sixty
    # ticks is three seconds. A pending call is cancelled first, so two quick
    # writes cannot leave two live callbacks. The Roll-keeper branch is
    # unchanged and never reads the rider roll.
    if "removeTag(ROLLCALL_TAG)" not in script:
        fail("a name write does not clear the roll-call tag")
    if "scheduleRollCall(player)" not in script:
        fail("a name write does not schedule the roll call")
    scheduler = re.search(r"function scheduleRollCall\(player\) \{(.*?)\n\}", script, re.S)
    if not scheduler:
        fail("main.js has no scheduleRollCall helper")
    scheduler_body = scheduler.group(1)
    if "system.clearRunTimeout(prior)" not in scheduler_body:
        fail("a new name write does not cancel the pending roll call")
    if "readRollCall(player)" not in scheduler_body or "}, 60)" not in scheduler_body:
        fail("the roll call is not a three-second beat after the write")
    roll_branch = re.search(
        r'else \{\s*player\.sendMessage\("§7The keeper closes the roll\..*?\n  \}',
        script,
        re.S,
    )
    if not roll_branch:
        fail("the Roll-keeper branch is missing")
    if "readRollCall" in roll_branch.group(0):
        fail("the Roll-keeper branch reads the rider roll")
    # A player-typed name must never reach a command string. The only
    # runCommand in the script is the fixed map tick.
    commands = re.findall(r"runCommand\(\s*([^)]*)\)", script)
    if commands != ['"function basgiath/tick"']:
        fail(f"script runs a command that is not the fixed map tick: {commands}")
    folder = functions / "basgiath"
    build = (folder / "build.mcfunction").read_text()
    if 'titleraw @s title {"rawtext":[{"text":"Building"}]}' not in build:
        fail("build function does not show the Building title")
    if "gamerule sendcommandfeedback false" not in build:
        fail("build function leaves command feedback on for the stages")
    if 'summon armor_stand "build_anchor"' not in build:
        fail("build function does not summon the anchor")
    if "~ 80 ~" in build:
        fail("build function still lifts the player into the sky")
    if "setblock ~ ~-1 ~ stone" not in build:
        fail("build function does not place a stone under the player")
    if "resistance 999999 255" not in build:
        fail("build function does not give the anchor resistance")
    if "scoreboard players set bg_stage map_state 0" not in build:
        fail("build function leaves the stage running")
    if "#wait" in build:
        fail("build function waits for a tick the phone does not run")
    # Derive the stage count from build.mcfunction. A hard-coded stage_20
    # breaks the moment a zone grows past 32 stages.
    stage_numbers = [int(number) for number in re.findall(r"basgiath/stage_(\d+)", build)]
    if not stage_numbers or stage_numbers != list(range(1, len(stage_numbers) + 1)):
        fail("build function does not place the college stages in order")
    if "tickingarea add circle" not in build:
        fail("build function does not load the college chunks")
    if "schedule on_area_loaded add tickingarea college_b basgiath/fill_far" not in build:
        fail("build function does not fill the plaza when the stair chunks load")
    if "schedule on_area_loaded add tickingarea college_d basgiath/fill_far" not in build:
        fail("build function does not fill the valley when those chunks load")
    if "schedule delay add basgiath/raise 300" not in build:
        fail("build function has no timed second pass")
    if "scoreboard players set bg_done map_state 0" not in build:
        fail("build function does not arm the welcome")
    tick_fn = (folder / "tick.mcfunction").read_text()
    if "#wait" in tick_fn:
        fail("tick function still waits")
    fill_far = (folder / "fill_far.mcfunction").read_text()
    if "function basgiath/far_01" not in fill_far:
        fail("fill_far does not place the far college")
    raise_fn = (folder / "raise.mcfunction").read_text()
    if "slow_falling" not in raise_fn or "tp @p ~120 ~8 ~40" not in raise_fn:
        fail("raise function does not move the player onto the plaza")
    if "schedule delay add basgiath/open 80" not in raise_fn:
        fail("raise function does not place the plaza after the move")
    open_fn = (folder / "open.mcfunction").read_text()
    if "function basgiath/far_01" not in open_fn:
        fail("open function does not place the far college")
    if "Welcome, candidate" not in open_fn or "scoreboard players set bg_done map_state 1" not in open_fn:
        fail("open function does not welcome the player")
    if "run execute " in open_fn:
        fail("open function nests execute")
    far_blob = "\n".join(path.read_text() for path in sorted(folder.glob("far_*.mcfunction")))
    if "fill ~ ~-2 ~ ~170 " in far_blob:
        fail("far pass still refills the whole ground plane")
    live = (folder / "live.mcfunction").read_text()
    for needle in ("spawnpoint", "cp_west", "cp_east", "cp_quad", "cp_valley", "~0.18"):
        if needle not in live:
            fail(f"live function missing {needle}")
    # The Gauntlet scores for real. The objectives are created once at build
    # time, the clock lives in the live pass, and the penalty is per cadet.
    for objective in ("gate_time", "gate_sec", "gate_start", "gate_pen", "gate_best"):
        if f"scoreboard objectives add {objective} dummy" not in build:
            fail(f"the build does not create the {objective} objective")
    if "scoreboard players set bg_twenty map_state 20" not in build:
        fail("the build never sets the divisor the seconds objective needs")
    if "scoreboard objectives setdisplay sidebar gate_sec" not in build:
        fail("the build does not put the cadet's time on the sidebar")
    if "scoreboard players add bg_clock map_state 1" not in live:
        fail("the live pass has no clock")
    for needle in ("gate_time", "gate_sec", "gate_start", "gate_pen", "gate_best", "gate_run", "gate_done"):
        if needle not in live:
            fail(f"the live pass never touches {needle}")
    if "operation @s gate_sec /= bg_twenty map_state" not in live:
        fail("the live pass never turns ticks into seconds")
    # The cadet course clock. The objective must exist before the live pass
    # writes it, and the action bar line must carry the seconds, not ticks.
    for objective in ("run_tick", "run_sec"):
        if f"scoreboard objectives add {objective} dummy" not in build:
            fail(f"the build does not create the {objective} objective")
    if "scoreboard players add @a[tag=timed_run] run_tick 1" not in live:
        fail("the live pass never advances the course clock")
    # The copy must be scoped per cadet. A bare "@a[tag=timed_run] = @a[tag=timed_run]"
    # resolves the source to one entity, so two runners would share one clock.
    if "execute as @a[tag=timed_run] run scoreboard players operation @s run_sec = @s run_tick" not in live:
        fail("the course clock copies the tick count without scoping it per cadet")
    if '"objective":"run_sec"' not in live:
        fail("the course clock does not show the cadet's time on the action bar")
    for path in (folder / "run_start.mcfunction", folder / "run_stop.mcfunction"):
        if not path.exists():
            fail(f"the course clock is missing {path.name}")
    if f'const COURSE_TAG = "{COURSE_TAG_NAME}"' not in script:
        fail("the script does not name the course tag")
    # The start and summit zones come from BANDS in the zone module, not from
    # rewritten numbers. This compares the emitted boxes against the module's
    # own geometry, and the bench additionally proves they sit on the cliff.
    def box_text(box: tuple[int, int, int, int, int, int]) -> str:
        x0, y0, z0, x1, y1, z1 = box
        return (
            f"x=~{x0},y=~{y0},z=~{z0},"
            f"dx={x1 - x0 + 1},dy={y1 - y0 + 1},dz={z1 - z0 + 1}"
        )
    for name, box in (("start", gauntlet_box("start_box")), ("summit", gauntlet_box("summit_box"))):
        if box_text(box) not in live:
            fail(f"the live pass does not gate on the derived {name} box {box_text(box)}")
    # The penalty must land on the cadet, and it must be 30 seconds of ticks.
    penalties = re.findall(r"run scoreboard players add (@\w+|#\w+) gate_pen (\d+)", live)
    if not penalties:
        fail("the live pass never adds to gate_pen")
    for target, amount in penalties:
        if amount != "600":
            fail(f"the rope penalty is {amount} ticks, not 600")
        if not target.startswith("@"):
            fail(f"the rope penalty lands on {target}, not on the cadet")
    if "#gauntlet" in live or "#gauntlet" in build:
        fail("the old global #gauntlet counter is still there")
    # The time is computed, never guessed: exactly three operations write
    # gate_time, and the last one adds the cadet's own penalty. The pattern
    # matches gate_time only as the destination, so the gate_best lines that
    # read it are not counted.
    time_write = re.compile(r"scoreboard players (?:operation|set|add|remove) \S+ gate_time\b")
    time_writes = [
        line.split(" run ", 1)[1]
        for line in live.splitlines()
        if time_write.search(line)
    ]
    if time_writes != [
        "scoreboard players operation @s gate_time = bg_clock map_state",
        "scoreboard players operation @s gate_time -= @s gate_start",
        "scoreboard players operation @s gate_time += @s gate_pen",
    ]:
        fail(f"the live pass computes gate_time as {time_writes}")
    # The finish line. The `titleraw` score component was withheld until a
    # server log accepted it; `bench_bds.sh` now drives this exact shape at the
    # anchor stand on every bench run, so it ships and this gate requires it.
    # If that probe ever starts failing, drop the component back to a plain
    # line and relax this gate together.
    if "Gauntlet complete" not in live:
        fail("the live pass does not announce the finish")
    if '"score"' not in live:
        fail("the finish line no longer carries the cadet's time")
    if '"objective":"gate_sec"' not in live:
        fail("the finish line does not show the cadet's time in seconds")
    # Bedrock's titleraw takes a title location before the JSON. Without it the
    # command is a syntax error, which is what the bench caught the first time
    # this shipped. The gate is cheap; the bug reached a live pass once.
    if "titleraw @s title " not in live:
        fail("the finish line titleraw has no title location")
    # The bond must be gated on the crossing. The live pass earns the tag on the
    # span or the roof, and the bond selector requires it.
    if "tag @s add crossed" not in live:
        fail("the live pass never earns the crossed tag")
    if "tag=crossed,tag=!bonded" not in live:
        fail("the bond selector does not require the crossed tag")
    summon = (folder / "summon_dragon.mcfunction").read_text()
    if "dragon_rider:dragon" not in summon:
        fail("summon function does not summon dragon_rider:dragon")
    # The bond already summons a dragon. The manual summon must not add a second.
    if "execute unless entity @e[type=dragon_rider:dragon]" not in summon:
        fail("summon_dragon can produce a second dragon")
    blob = "\n".join(path.read_text() for path in sorted(folder.glob("*.mcfunction")))
    for needle in (
        "lodestone",
        "setblock ~45 ~32 ~20 air",
        "setblock ~46 ~32 ~20 air",
        "setblock ~44 ~32 ~20",
        "setblock ~47 ~32 ~20",
        "weather thunder",
        "Cross the Parapet",
        "spawnpoint @p ~8 ~0 ~66",
        "tp @p ~8 ~0 ~66 180 0",
        "doimmediaterespawn true",
    ):
        if needle not in blob:
            fail(f"map commands missing {needle}")
    if " water" in blob or blob.startswith("water"):
        fail("the span pit still contains water")
    # Cross-validate the keeper table against the world. Each side is read
    # independently: the cells from the emitted setblock lines, the table from
    # main.js. A drift between them fails here instead of shipping a keeper
    # whose lectern is somewhere else and never opens.
    emitted = emitted_lecterns(blob)
    keepers = keeper_blocks()
    for cell in sorted(keepers - emitted):
        fail(f"main.js KEEPERS names {cell} but no bare lectern stands there")
    for cell in sorted(emitted - keepers):
        fail(f"a bare lectern at {cell} is not a keeper in main.js")
    print(f"keeper lecterns ok: {len(keepers)} cells agree with main.js")
    if 'tp @a[x=~18,y=~-40,z=~8' in live:
        fail("live function still rescues a fall from the span")
    air_volume = 0
    for line in blob.splitlines():
        match = FILL.match(line.strip())
        if not match:
            continue
        xs = [coord(token) for token in match.groups()]
        volume = abs(xs[3] - xs[0]) + 1
        volume *= abs(xs[4] - xs[1]) + 1
        volume *= abs(xs[5] - xs[2]) + 1
        if volume > 32768:
            fail(f"fill volume {volume} exceeds 32768: {line}")
        if line.strip().endswith(" air"):
            air_volume += volume
    # The air gate counts every *.mcfunction, so far air appears in both the
    # stage pass and the far retry. A phone runs both passes, so the count is
    # conservative, not wrong. Do not read the double count as a bug.
    if air_volume > 80000:
        fail(f"air fill volume {air_volume} is large enough to stall a phone")
    stages = sorted(folder.glob("stage_*.mcfunction"))
    if not stages:
        fail("no stage functions")
    for path in stages:
        count = sum(
            1
            for line in path.read_text().splitlines()
            if line.strip() and not line.startswith("#")
        )
        if count > 50:
            fail(f"{path.name} has {count} commands")
    for obsolete in (
        "parapet_wind.mcfunction",
        "parapet_checkpoint_a.mcfunction",
        "parapet_checkpoint_b.mcfunction",
    ):
        if (functions / obsolete).exists():
            fail(f"obsolete function still present: {obsolete}")
    print(f"map ok: {len(stages)} stages")


def check_dragon() -> None:
    geo_path = ROOT / "addon/resource_pack/models/entity/dragon.geo.json"
    geo = json.loads(geo_path.read_text())
    desc = geo["minecraft:geometry"][0]
    if desc["description"]["identifier"] != "geometry.dragon_rider":
        fail("geometry id changed")
    if desc["description"]["texture_width"] != 128:
        fail("texture width is not 128")
    bones = desc["bones"]
    by_name = {bone["name"]: bone for bone in bones}
    for name in REQUIRED_BONES:
        if name not in by_name:
            fail(f"missing bone {name}")
    if by_name["wing_left"]["pivot"][0] <= 0:
        fail("left wing pivot is not on +X")
    if by_name["wing_right"]["pivot"][0] >= 0:
        fail("right wing pivot is not on -X")
    if by_name["head"].get("parent") != "neck":
        fail("head is not parented to neck")
    back_ok = False
    for cube in by_name["body"]["cubes"]:
        _, y, z = cube["origin"]
        _, h, d = cube["size"]
        if y + h == 32 and z <= 0 <= z + d:
            back_ok = True
    if not back_ok:
        fail("no body cube has its top at y=32 across z=0")
    try:
        from PIL import Image
    except ImportError:
        fail("Pillow is not installed")
    image = Image.open(ROOT / "addon/resource_pack/textures/entity/dragon.png")
    if image.size != (128, 128):
        fail(f"texture size is {image.size}")
    print(f"dragon ok: {len(bones)} bones")


def check_world() -> None:
    sys.path.insert(0, str(ROOT))
    from scripts.nbt_le import decode_level_dat

    run([sys.executable, "scripts/build_world.py"])
    world = ROOT / "dist/basgiath.mcworld"
    if not world.exists() or world.stat().st_size < 1000:
        fail("mcworld is missing or too small")
    with zipfile.ZipFile(world) as bundle:
        names = bundle.namelist()
        for required in (
            "level.dat",
            "levelname.txt",
            "world_behavior_packs.json",
            "world_resource_packs.json",
        ):
            if required not in names:
                fail(f"mcworld missing {required}")
        if not any(name.startswith("behavior_packs/basgiath/manifest.json") for name in names):
            fail("behavior pack is not at the zip root")
        if not any(name.startswith("resource_packs/basgiath/manifest.json") for name in names):
            fail("resource pack is not at the zip root")
        level = decode_level_dat(bundle.read("level.dat"))
        if level.get("LevelName") != "Basgiath":
            fail("level name is not Basgiath")
        if level.get("Generator") != 2 or level.get("commandsEnabled") != 1:
            fail("world is not a flat world with commands")
        if level.get("sendcommandfeedback") != 1:
            fail("command errors are hidden before the build runs")
        if "grass_block" not in str(level.get("FlatWorldLayers")):
            fail("flat layers are missing")
        # The world header, not the manifest, is what turns the experiments on.
        # Checking the dependency versions is what let this survive four audits.
        experiments = level.get("experiments") or {}
        for key in ("beta_apis", "gametest"):
            if experiments.get(key) != 0:
                fail(f"world enables the {key} experiment: {experiments.get(key)!r}")
        if level.get("GameType") != 2:
            fail(f"world GameType is {level.get('GameType')!r}, not adventure (2)")
        if level.get("ForceGameType") != 1:
            fail("world does not force the game type on join")
        behavior = json.loads(bundle.read("world_behavior_packs.json"))
        manifest = json.loads((ROOT / "addon/behavior_pack/manifest.json").read_text())
        if behavior[0]["pack_id"] != manifest["header"]["uuid"]:
            fail("behavior pack uuid mismatch")
        if behavior[0]["version"] != manifest["header"]["version"]:
            fail("behavior pack version mismatch")
    print(f"world ok: {world.stat().st_size} bytes")


def check_signets() -> None:
    """The signet set holds together.

    The script gates the form on one block position. If that is not the
    lodestone the build places, the form never opens anywhere; if a quiz choice
    names an archetype the table does not define, that answer can never win;
    and an archetype no question offers can never be reached at all.
    """
    script = (ROOT / "addon/behavior_pack/scripts/main.js").read_text()

    stone = re.search(
        r"const SIGNET_STONE = \{ x: (-?\d+), y: (-?\d+), z: (-?\d+) \};", script
    )
    if not stone:
        fail("main.js has no SIGNET_STONE")
    gated = tuple(int(group) for group in stone.groups())

    folder = ROOT / "addon/behavior_pack/functions/basgiath"
    blob = "\n".join(path.read_text() for path in sorted(folder.glob("*.mcfunction")))
    # The stage pass and the far retry both place the stone, so count cells, not
    # commands.
    placed = {
        (coord(parts[1]), coord(parts[2]), coord(parts[3]))
        for parts in (line.split() for line in blob.splitlines())
        if len(parts) >= 5 and parts[0] == "setblock" and parts[4] == "lodestone"
    }
    if len(placed) != 1:
        fail(f"the build places a lodestone at {len(placed)} cells: {sorted(placed)}")
    stone_cell = next(iter(placed))
    if gated != stone_cell:
        fail(f"the signet is gated on {gated}, but the build places the stone at {stone_cell}")

    table = re.search(r"const SIGNETS = \{(.*?)\n\};", script, re.S)
    if not table:
        fail("main.js has no SIGNETS table")
    defined = set(re.findall(r"^\s{2}(\w+): \{", table.group(1), re.M))
    if len(defined) < 8:
        fail(f"expected at least 8 signet archetypes, found {len(defined)}")

    offered = set(re.findall(r'signet: "(\w+)"', script))
    if not offered:
        fail("no quiz choice names an archetype")
    unknown = sorted(offered - defined)
    if unknown:
        fail(f"quiz choices name archetypes with no table entry: {unknown}")
    unreachable = sorted(defined - offered)
    if unreachable:
        fail(f"these archetypes can never win: {unreachable}")

    print(f"signets ok: {len(defined)} archetypes, all reachable, stone {gated}")


def check_signet() -> None:
    script = (ROOT / "addon/behavior_pack/scripts/main.js").read_text()
    if "beforeEvents.playerInteractWithBlock" not in script:
        fail("signet listener is not on beforeEvents.playerInteractWithBlock")
    if "afterEvents.playerInteractWithBlock" in script:
        fail("signet listener still uses afterEvents.playerInteractWithBlock")
    print("signet listener ok")


def check_uuids() -> None:
    uuids = []
    for path in (
        ROOT / "addon/behavior_pack/manifest.json",
        ROOT / "addon/resource_pack/manifest.json",
    ):
        data = json.loads(path.read_text())
        uuids.append(data["header"]["uuid"])
        for module in data["modules"]:
            uuids.append(module["uuid"])
    if len(uuids) != len(set(uuids)):
        fail(f"pack UUIDs are not unique: {uuids}")


def check_manifests() -> None:
    """The release gate runs the manifest validator and requires it to pass.

    validate_manifests.py is the single source of the manifest contract the
    Bedrock import dialog reads. This asserts it ran here, not only inside
    package.sh, so a broken manifest fails the gate even on a build path that
    skips the packaging step.
    """
    run([sys.executable, "scripts/validate_manifests.py"])
    print("pack manifests ok")


def check_hud() -> None:
    """Check the flight readout's easing curve and stamina bar.

    check_hud.mjs lifts the shipped functions out of main.js, so it tests the
    code that ships, not a copy. It cannot check the picture on a screen --
    only a client can -- but it checks the maths the display depends on.
    """
    run(["node", "scripts/check_hud.mjs"])
    print("flight readout ok")


def check_currency() -> None:
    """The coin items, their icons, and the conversion recipes hold together.

    An item whose icon key is not in the atlas renders as a missing texture,
    and a recipe that names an item this pack does not define simply
    disappears. Both are silent in game, so they are checked here.
    """
    items_dir = ROOT / "addon/behavior_pack/items"
    atlas = json.loads(
        (ROOT / "addon/resource_pack/textures/item_texture.json").read_text()
    )
    registered = atlas["texture_data"]

    defined = set()
    for path in sorted(items_dir.glob("*.json")):
        item = json.loads(path.read_text())["minecraft:item"]
        identifier = item["description"]["identifier"]
        if not identifier.startswith("dragon_rider:"):
            fail(f"{path.name} is not a dragon_rider item: {identifier}")
        defined.add(identifier)
        texture = item["components"]["minecraft:icon"]["textures"]["default"]
        if texture not in registered:
            fail(f"{identifier} icon {texture!r} is not in item_texture.json")
        on_disk = ROOT / "addon/resource_pack" / (registered[texture]["textures"] + ".png")
        if not on_disk.exists():
            fail(f"{identifier} texture is missing on disk: {on_disk}")
    if len(defined) < 4:
        fail(f"expected at least 4 currency items, found {len(defined)}")

    recipes = sorted((ROOT / "addon/behavior_pack/recipes").glob("*.json"))
    if not recipes:
        fail("no conversion recipes")
    for path in recipes:
        recipe = json.loads(path.read_text())
        body = recipe.get("minecraft:recipe_shaped") or recipe.get("minecraft:recipe_shapeless")
        if not body:
            fail(f"{path.name} is neither a shaped nor a shapeless recipe")
        if body.get("tags") != ["crafting_table"]:
            fail(f"{path.name} is not a crafting-table recipe: {body.get('tags')!r}")
        referenced = [body["result"]["item"]]
        referenced += [entry["item"] for entry in body.get("key", {}).values()]
        referenced += [entry["item"] for entry in body.get("ingredients", [])]
        for ref in referenced:
            if ref not in defined:
                fail(f"{path.name} names {ref}, which this pack does not define")

    # The vault desk: a custom block. Its texture must be in the terrain atlas
    # and on disk, or the block renders as a missing texture, and the script
    # must name that exact block id or nothing opens the desk.
    block = json.loads(
        (ROOT / "addon/behavior_pack/blocks/vault_desk.json").read_text()
    )["minecraft:block"]
    block_id = block["description"]["identifier"]
    terrain = json.loads(
        (ROOT / "addon/resource_pack/textures/terrain_texture.json").read_text()
    )["texture_data"]
    block_texture = block["components"]["minecraft:material_instances"]["*"]["texture"]
    if block_texture not in terrain:
        fail(f"{block_id} texture {block_texture!r} is not in terrain_texture.json")
    block_png = ROOT / "addon/resource_pack" / (terrain[block_texture]["textures"] + ".png")
    if not block_png.exists():
        fail(f"{block_id} block texture is missing on disk: {block_png}")
    script = (ROOT / "addon/behavior_pack/scripts/main.js").read_text()
    if f'"{block_id}"' not in script:
        fail(f"main.js never names {block_id}, so nothing opens the desk")

    print(f"pack items ok: {len(defined)} defined, {len(recipes)} recipes, 1 block")


def check_lore() -> None:
    """The readable items have a codex entry with pages, and an icon to show.

    The CODICES table is the list of readable items. An item is readable only
    if the script names it there: matching on any mention would count the
    currency items, whose ids also appear in this file. An entry with no title,
    or fewer than two pages, opens a dead screen. The page text itself is
    covered by check_names, which scans this file for the denylist.
    """
    script = (ROOT / "addon/behavior_pack/scripts/main.js").read_text()
    table = re.search(r"const CODICES = \{(.*?)\n\};", script, re.S)
    if not table:
        fail("main.js has no CODICES table")
    entries = re.findall(
        r'"(dragon_rider:[a-z_]+)":\s*\{(.*?)\n  \},', table.group(1), re.S
    )
    if len(entries) < 3:
        fail(f"expected at least 3 readable items, found {len(entries)}")

    atlas = json.loads(
        (ROOT / "addon/resource_pack/textures/item_texture.json").read_text()
    )["texture_data"]
    items = {}
    for path in sorted((ROOT / "addon/behavior_pack/items").glob("*.json")):
        item = json.loads(path.read_text())["minecraft:item"]
        items[item["description"]["identifier"]] = item

    for identifier, body in entries:
        if identifier not in items:
            fail(f"the codex names {identifier}, but no item defines it")
        icon = items[identifier]["components"]["minecraft:icon"]["textures"]["default"]
        if icon not in atlas:
            fail(f"{identifier} icon {icon!r} is not in item_texture.json")
        if "title:" not in body:
            fail(f"{identifier} has no codex title")
        pages = re.findall(r'^\s{6}"', body, re.M)
        if len(pages) < 2:
            fail(f"{identifier} has {len(pages)} page(s), need at least 2")

    print(f"lore ok: {len(entries)} readable items")


def main() -> None:
    run([sys.executable, "scripts/build_map.py"])
    run([sys.executable, "scripts/build_dragon_model.py"])
    check_names()
    check_map()
    check_signet()
    check_signets()
    check_dragon()
    check_uuids()
    check_manifests()
    check_hud()
    check_currency()
    check_lore()
    check_world()
    print("release checks ok")


if __name__ == "__main__":
    main()
