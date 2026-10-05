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


def assert_lectern(blob: str, x: int, y: int, z: int, label: str) -> None:
    """The last emitted block at a spot must be a bare lectern.

    A tall grass patch or a tombstone laid over the lectern would still leave
    the word in the blob, so this reads the final setblock at the exact cell.
    """
    last = None
    prefix = f"setblock ~{x} ~{y} ~{z} "
    for raw in blob.splitlines():
        line = raw.strip()
        if line.startswith(prefix):
            last = line[len(prefix) :].split()[0]
    if last != "lectern":
        fail(f"{label} at ({x}, {y}, {z}) is {last!r}, not a lectern")
    print(f"{label} lectern ok at ({x}, {y}, {z})")


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
    if "scoreboard players set #stage map_state 0" not in build:
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
    if "scoreboard players set #done map_state 0" not in build:
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
    if "Welcome, candidate" not in open_fn or "scoreboard players set #done map_state 1" not in open_fn:
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
    summon = (folder / "summon_dragon.mcfunction").read_text()
    if "dragon_rider:dragon" not in summon:
        fail("summon function does not summon dragon_rider:dragon")
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
    # The two keeper lecterns must stand in the emitted world: the Scroll-keeper
    # at the roll desk in the Quad, the Roll-keeper one block north of the stand.
    assert_lectern(blob, 128, 1, 34, "Scroll-keeper")
    assert_lectern(blob, 50, -1, 123, "Roll-keeper")
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
        behavior = json.loads(bundle.read("world_behavior_packs.json"))
        manifest = json.loads((ROOT / "addon/behavior_pack/manifest.json").read_text())
        if behavior[0]["pack_id"] != manifest["header"]["uuid"]:
            fail("behavior pack uuid mismatch")
        if behavior[0]["version"] != manifest["header"]["version"]:
            fail("behavior pack version mismatch")
    print(f"world ok: {world.stat().st_size} bytes")


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


def main() -> None:
    run([sys.executable, "scripts/build_map.py"])
    run([sys.executable, "scripts/build_dragon_model.py"])
    check_names()
    check_map()
    check_signet()
    check_dragon()
    check_uuids()
    check_world()
    print("release checks ok")


if __name__ == "__main__":
    main()
