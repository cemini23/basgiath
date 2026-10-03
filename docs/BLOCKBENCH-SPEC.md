# Blockbench spec — the dragon model

The dragon in the pack is generated. `scripts/build_dragon_model.py` writes the geometry and the texture. Read the constraints first. They keep the animations, the client entity, and the rider seat working.

## Hard constraints (the contract)

These must not change, or other files break:

| Keep | Why | Referenced by |
|---|---|---|
| Bone names `body`, `head`, `neck`, `jaw`, `wing_left`, `wing_right`, `tail` | The animations drive `head`, `jaw`, `tail`, `wing_left`, and `wing_right` | `animations/dragon.animation.json` |
| Geometry id `geometry.dragon_rider` | The client entity points at it | `entity/dragon.entity.json` |
| `format_version` `1.12.0` | Bedrock model format | the game |
| Texture path `textures/entity/dragon` and the file `textures/entity/dragon.png` | The client entity points at it | `entity/dragon.entity.json` |
| Back surface near `y = 32`, `z ≈ 0` | The rider seat sits there | `entities/dragon.json` |

If you move the back, update the seat position in `addon/behavior_pack/entities/dragon.json` (`minecraft:rideable` → `seats` → `position`, in blocks: `[0, 2.1, -0.2]`).

## Current model

Change `scripts/build_dragon_model.py`, then run it. Do not hand-export over the generated files. CI checks that the geometry, the texture, and the map functions match the scripts.

All values are Bedrock units (1 unit = 1 pixel = 1/16 block). Cube origins are in model space, not parent-local space.

Axis convention: `-Z` is the front (head), `+Z` is the back (tail), `+X` is the left wing, `+Y` is up.

| Bone | Parent | Pivot |
|---|---|---|
| `body` | — | `[0, 24, 0]` |
| `neck` | `body` | `[0, 30, -26]` |
| `head` | `neck` | `[0, 34, -42]` |
| `jaw` | `head` | `[0, 28, -56]` |
| `wing_left` / `wing_left_mid` / `wing_left_tip` | body, then each child | `[12, 32, -10]`, `[34, 32, -10]`, `[58, 32, -10]` |
| `wing_right` / `wing_right_mid` / `wing_right_tip` | the mirror | `[-12, 32, -10]`, `[-34, 32, -10]`, `[-58, 32, -10]` |
| `tail` / `tail_2` / `tail_3` / `tail_4` | each child on the last | from `[0, 22, 20]` toward `+Z` |
| `leg_front_left`, `leg_front_right`, `leg_back_left`, `leg_back_right` | `body` | shoulders near `Y=16`, feet at `Y=0` |

The chest top is `Y=32` and its Z range covers `0`, so the seat stays valid. The texture is 128×128. Belly faces use a sand color. Wing membranes have veins. Eyes sit on the side faces of the skull. Horns use the bone color. The script packs per-face UVs. Two runs of the script must write the same PNG bytes.

## Blockbench walkthrough

1. Edit the bone list and the cube list in `scripts/build_dragon_model.py`.
2. Run `python3 scripts/build_dragon_model.py` from the repo root.
3. Open the written `dragon.geo.json` in Blockbench if you want to look at it. Do not rename bones.
4. If you paint in Blockbench, copy the idea back into the script. A hand-saved PNG will fail the byte check in CI.
5. Confirm the geometry id is still `geometry.dragon_rider` and the texture size is still 128.

## Install and verify

```
bash scripts/validate.sh          # every JSON parses, UUIDs unique
bash scripts/package.sh           # rebuild dist/basgiath.mcaddon
```

Then load the pack in a Bedrock 26.20 world and run `/summon dragon_rider:dragon`. Check three things:

1. The model renders with the right texture.
2. You can ride it and steer while flying.
3. The wings flap and the tail sways.

## Common mistakes

- **Renaming bones.** The animations silently stop. Keep `body`, `head`, `jaw`, `wing_left`, `wing_right`, and `tail`.
- **Moving the back.** The rider floats or sinks. Re-check the seat `position` in the entity file. Do not change it unless the chest top moves.
- **Forgetting the texture size.** A 128 texture on a 64 geometry shows scrambled UVs.
- **Exporting as a Java model.** Use the Bedrock geometry format `1.12.0`.
- **Rotating `wing_right` the same way as `wing_left`.** The flap is a Z rotation. The two signs stay opposite. Left pivot X is positive. Right pivot X is negative.
