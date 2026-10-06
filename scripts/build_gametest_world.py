#!/usr/bin/env python3
"""Build dist/gametest.mcworld: the shipped world plus the dev GameTest pack.

This is a test artifact, not a ship artifact. It is the one place the Beta APIs
and GameTest experiments are allowed, and it is the only world that carries the
test behavior pack. The shipped world stays exactly as build_world.py writes
it. The level and zip helpers are imported from build_world.py; that file is
not modified.
"""

from __future__ import annotations

import importlib.util
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# build_world.py is a script, not an importable package member. Load it by
# path so a bare `python3 scripts/build_gametest_world.py` works from anywhere.
spec = importlib.util.spec_from_file_location("build_world", ROOT / "scripts/build_world.py")
build_world = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_world)

# The GameTest needs its structure file present before the pack is zipped in.
spec_struct = importlib.util.spec_from_file_location(
    "build_gametest_structure", ROOT / "scripts/build_gametest_structure.py"
)
build_gametest_structure = importlib.util.module_from_spec(spec_struct)
spec_struct.loader.exec_module(build_gametest_structure)

SHIPPED_BP = ROOT / "addon/behavior_pack"
SHIPPED_RP = ROOT / "addon/resource_pack"
TEST_BP = ROOT / "tests/gametest/behavior_pack"
OUT = ROOT / "dist/gametest.mcworld"


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    build_gametest_structure.build()
    root = build_world._level_root()
    # The test world is the one place Beta APIs is allowed.
    root["experiments"] = {
        "experiments_ever_loaded": build_world.Byte(1),
        "beta_apis": build_world.Byte(1),
        "gametest": build_world.Byte(1),
    }
    level = build_world.encode_level_dat(root)
    # Both behavior packs: the shipped pack owns the dragon entity, the test
    # pack owns the GameTest. The shipped resource pack supplies the model.
    behavior = build_world._pack_ref(SHIPPED_BP / "manifest.json") + build_world._pack_ref(
        TEST_BP / "manifest.json"
    )
    resource = build_world._pack_ref(SHIPPED_RP / "manifest.json")
    with zipfile.ZipFile(OUT, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("level.dat", level)
        zf.writestr("levelname.txt", "Basgiath GameTest\n")
        zf.writestr("world_behavior_packs.json", json.dumps(behavior, indent=2))
        zf.writestr("world_resource_packs.json", json.dumps(resource, indent=2))
        build_world._add_tree(zf, SHIPPED_BP, "behavior_packs/basgiath")
        build_world._add_tree(zf, TEST_BP, "behavior_packs/basgiath_tests")
        build_world._add_tree(zf, SHIPPED_RP, "resource_packs/basgiath")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
