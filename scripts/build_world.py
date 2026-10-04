#!/usr/bin/env python3
"""Build dist/basgiath.mcworld from addon packs and a Bedrock level.dat."""

from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = Path(__file__).resolve().parent
DIST = ROOT / "dist"
OUT = DIST / "basgiath.mcworld"

BEHAVIOR_SRC = ROOT / "addon" / "behavior_pack"
RESOURCE_SRC = ROOT / "addon" / "resource_pack"

FLAT_LAYERS = (
    '{"biome_id":1,"block_layers":[{"block_name":"minecraft:bedrock","count":1},'
    '{"block_name":"minecraft:dirt","count":2},'
    '{"block_name":"minecraft:grass_block","count":1}],'
    '"encoding_version":6,"preset_id":"ClassicFlat",'
    '"structure_options":null,"world_version":"version.post_1_18"}'
)

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
from nbt_le import Byte, Float, IntList, Long, encode_level_dat  # noqa: E402


def _pack_ref(manifest_path: Path) -> list[dict]:
    header = json.loads(manifest_path.read_text(encoding="utf-8"))["header"]
    return [{"pack_id": header["uuid"], "version": header["version"]}]


def _add_tree(zf: zipfile.ZipFile, src: Path, prefix: str) -> None:
    for path in sorted(src.rglob("*")):
        if not path.is_file():
            continue
        if path.name == ".DS_Store":
            continue
        rel = path.relative_to(src).as_posix()
        zf.writestr(f"{prefix}/{rel}", path.read_bytes())


def _level_root() -> dict:
    return {
        "StorageVersion": 10,
        "LevelName": "Basgiath",
        "Generator": 2,
        "GameType": 1,
        "Difficulty": 1,
        "commandsEnabled": Byte(1),
        "SpawnX": 0,
        "SpawnY": -60,
        "SpawnZ": 0,
        "RandomSeed": Long(1),
        "FlatWorldLayers": FLAT_LAYERS,
        "lastOpenedWithVersion": IntList([1, 21, 90, 0, 0]),
        "MinimumCompatibleClientVersion": IntList([1, 21, 90, 0, 0]),
        "InventoryVersion": "1.21.90",
        "Time": Long(18000),
        "dodaylightcycle": Byte(0),
        "doweathercycle": Byte(0),
        "domobspawning": Byte(0),
        "keepinventory": Byte(1),
        "falldamage": Byte(1),
        "texturePacksRequired": Byte(1),
        "spawnMobs": Byte(0),
        "sendcommandfeedback": Byte(1),
        "commandblockoutput": Byte(0),
        "commandblocksenabled": Byte(1),
        "rainLevel": Float(1.0),
        "lightningLevel": Float(1.0),
        "experiments": {
            "experiments_ever_loaded": Byte(1),
            "beta_apis": Byte(1),
            "gametest": Byte(1),
        },
        "hasBeenLoadedInCreative": Byte(1),
        "bonusChestEnabled": Byte(0),
        "CenterMapsToOrigin": Byte(1),
        "ForceGameType": Byte(0),
        "LANBroadcast": Byte(1),
        "MultiplayerGame": Byte(1),
        "NetworkVersion": 827,
        "baseGameVersion": "*",
        "worldStartCount": Long(0),
        "LimitedWorldOriginX": 0,
        "LimitedWorldOriginY": 64,
        "LimitedWorldOriginZ": 0,
    }


def main() -> None:
    DIST.mkdir(parents=True, exist_ok=True)
    behavior_json = json.dumps(_pack_ref(BEHAVIOR_SRC / "manifest.json"), indent=2)
    resource_json = json.dumps(_pack_ref(RESOURCE_SRC / "manifest.json"), indent=2)
    level_dat = encode_level_dat(_level_root())

    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("level.dat", level_dat)
        zf.writestr("levelname.txt", "Basgiath\n")
        zf.writestr("world_behavior_packs.json", behavior_json)
        zf.writestr("world_resource_packs.json", resource_json)
        _add_tree(zf, BEHAVIOR_SRC, "behavior_packs/basgiath")
        _add_tree(zf, RESOURCE_SRC, "resource_packs/basgiath")

    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
