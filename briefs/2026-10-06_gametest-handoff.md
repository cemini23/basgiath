# SIP handoff — Bedrock GameTest behaviour layer (task 2)

## WorkDir

`/Users/claudiobarone/Projects/dragon-rider-map`

## Success criteria

- A new dev test behavior pack lives at `tests/gametest/behavior_pack/`. It is **not** under `addon/` and **not** in `dist/`.
- The pack registers exactly one GameTest, `basgiath:dragon_rides`. It summons `dragon_rider:dragon`, then asserts the entity exists, is rideable (`minecraft:rideable`), and is flyable (`minecraft:input_air_controlled`). Then it succeeds. No other tests.
- `tests/gametest/behavior_pack/manifest.json`: one `script` module (`entry: scripts/dragon_test.js`), and a `dependencies` array with (a) a pack dependency on the shipped behavior pack uuid `7a3f9c2e-1b4d-4e8a-9f21-0c5d6e7a8b90` version `[0,1,6]`, (b) `{"module_name": "@minecraft/server", "version": "1.13.0-beta"}`, (c) `{"module_name": "@minecraft/server-gametest", "version": "1.0.0-beta"}`. Header uuid `32468250-41e8-4bd0-9f44-6c094d6c183e`, module uuid `7b50ca13-ac6a-4138-a3e0-ab55e0d5fcaf`, both `version [1,0,0]`, `min_engine_version [1,21,90]`.
- `scripts/build_gametest_world.py` writes `dist/gametest.mcworld`: the shipped world with the experiments **on** (`gametest: 1`, `beta_apis: 1`) and **both** behavior packs listed in `world_behavior_packs.json` (shipped + tests), plus the shipped resource pack. It imports helpers from `scripts/build_world.py`; it does not modify that file.
- `scripts/bench_gametest.sh` boots the official Linux Bedrock dedicated server against `dist/gametest.mcworld`, runs `gametest run basgiath:dragon_rides` on the console, and writes `gametest_ok=true|false` to `result.txt`. It exits 2 on macOS, like `bench_bds.sh`.
- `tests/gametest/README.md` explains how to run the test in a client and on the bench.

## Verify

- `python3 scripts/build_gametest_world.py` succeeds and writes a world over 1000 bytes.
- `node --check tests/gametest/behavior_pack/scripts/dragon_test.js`
- `bash -n scripts/bench_gametest.sh` and `bash -n scripts/build_gametest_world.py` is not needed (python).
- The existing gate chain stays green and unchanged: `bash scripts/validate.sh`, `python3 scripts/test_release.py`, `python3 scripts/bench_static.py`, `bash scripts/package.sh`.
- On a RunPod pod: `bash scripts/bench_gametest.sh` prints `gametest_ok=true`.

## NEVER

- Do not touch `addon/` (the shipped packs) or any UUID inside `addon/`.
- Do not enable Beta APIs in `addon/`, in `dist/basgiath.mcworld`, or in `scripts/build_world.py`. The experiments belong only to the test world.
- Do not edit `scripts/build_world.py`, `scripts/build_map.py`, `scripts/zones/*`, `scripts/build_dragon_model.py`, or `addon/behavior_pack/scripts/main.js`.
- Do not change `scripts/validate_manifests.py`, `scripts/package.sh`, `scripts/validate.sh`, `scripts/test_release.py`.
- No secrets in any file. No new network calls except the Bedrock server download the bench already does.
- Do not commit or push.

## Plan

**1. `tests/gametest/behavior_pack/manifest.json`** — exactly as specified in Success criteria. `format_version: 2`.

**2. `tests/gametest/behavior_pack/scripts/dragon_test.js`**

```js
import * as GameTest from "@minecraft/server-gametest";

GameTest.register("basgiath", "dragon_rides", (test) => {
  const dragon = test.spawn("dragon_rider:dragon", { x: 2, y: 2, z: 2 });
  test.assert(dragon !== undefined, "the dragon did not spawn");
  test.assert(
    dragon.getComponent("minecraft:rideable") !== undefined,
    "the dragon has no minecraft:rideable component, so a cadet cannot mount it"
  );
  test.assert(
    dragon.getComponent("minecraft:input_air_controlled") !== undefined,
    "the dragon has no minecraft:input_air_controlled component, so it cannot be flown"
  );
  test.succeed();
}).maxTicks(200);
```

No `.structureName()` for the first attempt: the whole point is to discover whether Bedrock needs an `.mcstructure`. If `/gametest run` reports that a structure is required, add `scripts/build_gametest_structure.py` that writes `tests/gametest/behavior_pack/structures/basgiath/dragonpad.mcstructure` (little-endian, uncompressed NBT, no header: root `TAG_Compound` named `""` with `format_version` int 1, `size` int-list `[5,3,5]`, `structure_world_origin` int-list `[0,0,0]`, and `structure` holding `block_indices` = two int-lists, `entities` = empty list, and `palette.default.block_palette` with one stone entry plus empty `block_position_data`) and chain `.structureName("basgiath:dragonpad")`.

**3. `scripts/build_gametest_world.py`** — import the level/zip helpers from `build_world.py`:

```python
import importlib.util, json, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("build_world", ROOT / "scripts/build_world.py")
build_world = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_world)

SHIPPED_BP = ROOT / "addon/behavior_pack"
SHIPPED_RP = ROOT / "addon/resource_pack"
TEST_BP = ROOT / "tests/gametest/behavior_pack"
OUT = ROOT / "dist/gametest.mcworld"

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    root = build_world._level_root()
    # The test world is the one place Beta APIs is allowed.
    root["experiments"] = {"experiments_ever_loaded": build_world.Byte(1),
                           "beta_apis": build_world.Byte(1), "gametest": build_world.Byte(1)}
    level = build_world.encode_level_dat(root)
    behavior = build_world._pack_ref(SHIPPED_BP / "manifest.json") + \
               build_world._pack_ref(TEST_BP / "manifest.json")
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
```

`build_world.Byte` and `build_world.encode_level_dat` are re-exported into `build_world` by its `from nbt_le import ...`; use them directly.

**4. `scripts/bench_gametest.sh`** — copy `scripts/bench_bds.sh` and change three things: default world is `dist/gametest.mcworld`; after "Server started", send `gametest run basgiath:dragon_rides`; then sleep 20, and parse the log. Success = the log contains a line with `dragon_rides` that reports a pass (Bedrock prints a GameTest result line; capture it verbatim into `result.txt`). Write `gametest_ok=true` only when a pass line for `dragon_rides` is present and no fail line is present. Keep the `uname -s != Linux → exit 2` guard, the FIFO console plumbing, and the tool installs. Do not modify `bench_bds.sh`.

**5. `tests/gametest/README.md`** — short: what the test proves, how to run it in a client (Creative flat world, Beta APIs on, add both packs, `/gametest run basgiath:dragon_rides`), and how the bench runs it.

Note for the implementer: the exact GameTest result string in the dedicated-server log is unknown. Make the bench dump the last 60 log lines containing `gametest` or `dragon_rides` so the first pod run can reveal the real format, then tighten the parser.
