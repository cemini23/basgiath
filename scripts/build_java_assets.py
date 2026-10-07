#!/usr/bin/env python3
"""Write the Java mod's assets from the Bedrock pack's own art.

The Java port ships the same items and the same block as the Bedrock add-on, so it
ships the same textures. They are copied, never redrawn: one project, one set of
art, two editions. Nothing here invents art, and nothing here touches the Bedrock
pack.

Java needs three files per item and two per block that Bedrock does not:
a model, and for a block, a blockstate. They are written here so the Java tree is
generated from a script like every other output in this repo, and so CI can check
that the tree matches.

Run from the repo root:

    python3 scripts/build_java_assets.py
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BEDROCK = ROOT / "addon" / "resource_pack"
ASSETS = ROOT / "java" / "src" / "main" / "resources" / "assets" / "basgiath"

# The Bedrock identifier is dragon_rider:<path>. The Java namespace is the mod id.
ITEMS = {
    "copper_mark": "Copper Mark",
    "silver_mark": "Silver Mark",
    "gold_mark": "Gold Mark",
    "bank_note": "Bank Note",
    "flight_manual": "Flight Manual",
    "dragon_codex": "Dragon Codex",
    "academy_archive": "Academy Archive",
}

BLOCKS = {
    "vault_desk": "Vault Desk",
}

CREATIVE_TAB = "Basgiath"


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    for name in ITEMS:
        source = BEDROCK / "textures" / "item" / f"{name}.png"
        if not source.exists():
            raise SystemExit(f"the Bedrock pack has no texture for {name}: {source}")
        target = ASSETS / "textures" / "item" / f"{name}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        write_json(
            ASSETS / "models" / "item" / f"{name}.json",
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"basgiath:item/{name}"}},
        )

    for name in BLOCKS:
        source = BEDROCK / "textures" / "blocks" / f"{name}.png"
        if not source.exists():
            raise SystemExit(f"the Bedrock pack has no texture for {name}: {source}")
        target = ASSETS / "textures" / "block" / f"{name}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        write_json(
            ASSETS / "models" / "block" / f"{name}.json",
            {"parent": "minecraft:block/cube_all", "textures": {"all": f"basgiath:block/{name}"}},
        )
        write_json(
            ASSETS / "blockstates" / f"{name}.json",
            {"variants": {"": {"model": f"basgiath:block/{name}"}}},
        )
        write_json(
            ASSETS / "models" / "item" / f"{name}.json",
            {"parent": f"basgiath:block/{name}"},
        )

    # The dragon. GeckoLib reads the Bedrock geometry and animation formats directly,
    # so the port is a copy and not a rewrite: the same one model and the same two
    # animations serve both editions. Three files, and the paths are the ones
    # DefaultedEntityGeoModel derives from an entity id of basgiath:dragon.
    for source_rel, target_rel in (
        ("textures/entity/dragon.png", "textures/entity/dragon.png"),
        ("models/entity/dragon.geo.json", "geo/entity/dragon.geo.json"),
        ("animations/dragon.animation.json", "animations/entity/dragon.animation.json"),
    ):
        source = BEDROCK / source_rel
        if not source.exists():
            raise SystemExit(f"the Bedrock pack has no dragon asset at {source_rel}")
        target = ASSETS / target_rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)

    lang = {f"item.basgiath.{name}": label for name, label in ITEMS.items()}
    lang.update({f"block.basgiath.{name}": label for name, label in BLOCKS.items()})
    lang["itemGroup.basgiath"] = CREATIVE_TAB
    # Every shipped string is checked against the denylist by the release tests.
    write_json(ASSETS / "lang" / "en_us.json", lang)

    print(f"wrote Java assets: {len(ITEMS)} items, {len(BLOCKS)} block")


if __name__ == "__main__":
    main()
