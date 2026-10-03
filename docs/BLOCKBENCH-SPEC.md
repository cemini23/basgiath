# Blockbench spec — the dragon model

This replaces the five-box placeholder in `addon/resource_pack/models/entity/dragon.geo.json` with a real dragon. Read the constraints first. They are what keep the animations, the client entity, and the rider seat working.

## Hard constraints (the contract)

These must not change, or other files break:

| Keep | Why | Referenced by |
|---|---|---|
| Bone names `body`, `head`, `wing_left`, `wing_right`, `tail` | The animations drive these tracks | `animations/dragon.animation.json` |
| Geometry id `geometry.dragon_rider` | The client entity points at it | `entity/dragon.entity.json` |
| `format_version` `1.12.0` | Bedrock model format | the game |
| Texture path `textures/entity/dragon` and the file `textures/entity/dragon.png` | The client entity points at it | `entity/dragon.entity.json` |
| Back surface near `y = 32`, `z ≈ 0` | The rider seat sits there | `entities/dragon.json` |

If you move the back, update the seat position in `addon/behavior_pack/entities/dragon.json` (`minecraft:rideable` → `seats` → `position`, in blocks: `[0, 2.1, -0.2]`).

## Current placeholder (the reference to beat)

All values are Bedrock units (1 unit = 1 pixel = 1/16 block).

| Bone | Parent | Pivot | Cube origin | Cube size | UV |
|---|---|---|---|---|---|
| `body` | — | `[0, 24, 0]` | `[-16, 16, -32]` | `[32, 16, 56]` | `[0, 0]` |
| `head` | `body` | `[0, 28, -32]` | `[-8, 20, -48]` | `[16, 16, 16]` | `[0, 32]` |
| `wing_left` | `body` | `[16, 32, -8]` | `[16, 30, -16]` | `[36, 2, 28]` | `[32, 0]` |
| `wing_right` | `body` | `[-16, 32, -8]` | `[-52, 30, -16]` | `[36, 2, 28]` | `[32, 16]` |
| `tail` | `body` | `[0, 22, 24]` | `[-4, 18, 24]` | `[8, 6, 24]` | `[0, 48]` |

Axis convention: `-Z` is the front (head), `+Z` is the back (tail), `+X` is the left wing, `+Y` is up.

## Target proportions

Aim for a creature about 3.5 blocks long and 2 blocks tall at the back.

- **Body** — keep the 32 wide, 16 tall, 56 long mass, or refine it into a chest and a haunch. Keep the top near `y = 32`.
- **Neck + head** — add a neck bone between `body` and `head` if you want the head to move. Keep `head` as the leaf bone. A 16×16×16 head is the minimum; 20×18×20 reads better for a dragon.
- **Wings** — the placeholder wings are flat 2-unit slabs. Replace with a folded 3-segment wing (shoulder, mid, tip). Keep the two root bones named `wing_left` and `wing_right`. Their pivots must stay at the shoulder so the flap animation swings from the right place.
- **Tail** — split into `tail` (root) plus optional `tail_2`, `tail_3` children. The idle animation only drives `tail`, so extra child bones are free.
- **Legs** — add four legs under `body`. The current rig has none. Legs are not animated, so they are pure geometry.

## Texture and UV plan

Two options.

**Keep 64×64.** Simplest. Change nothing else. Enough for a flat-shaded dragon.

**Move to 128×128.** Better detail. You must then:
1. Resize `textures/entity/dragon.png` to 128×128.
2. Set `texture_width` and `texture_height` to `128` in the geometry description.
3. Re-UV every cube.

Suggested UV regions for 128×128:

| Region | Area | Use |
|---|---|---|
| `0,0 – 64,64` | body wrap | scales, belly |
| `64,0 – 128,32` | head wrap | horns, eyes, jaw |
| `0,64 – 64,128` | wings | membrane, bone |
| `64,64 – 96,128` | tail | plates |
| `96,96 – 128,128` | legs, claws | — |

Use **Box UV** for the body blocks and **Per-face UV** for the wings and head.

## Blockbench walkthrough

1. Open Blockbench. **File → New → Bedrock Model** (entity). Set the texture size to 64 or 128.
2. **File → Import → Bedrock Model** and load `addon/resource_pack/models/entity/dragon.geo.json`. This gives you the exact bones and pivots to build on. Do not rename them.
3. Build the cubes. Keep each cube inside its bone. Set the **pivot** of each bone to the joint you want it to rotate around — `wing_left` and `wing_right` at the shoulder, `tail` at the tail base.
4. Paint the texture. Save it over `addon/resource_pack/textures/entity/dragon.png`.
5. **File → Export → Bedrock Model.** Choose format `1.12.0`. Overwrite `addon/resource_pack/models/entity/dragon.geo.json`.
6. Confirm the geometry id is still `geometry.dragon_rider`.

## Install and verify

```
cd /Users/claudiobarone/Projects/dragon-rider-map
bash scripts/validate.sh          # every JSON parses, UUIDs unique
bash scripts/package.sh           # rebuild dist/dragon-rider-map.mcaddon
```

Then load the pack in a Bedrock 26.20 world and run `/summon dragon_rider:dragon`. Check three things:

1. The model renders with the right texture.
2. You can ride it and steer while flying.
3. The wings flap and the tail sways.

## Common mistakes

- **Renaming bones.** The animations silently stop. Keep `body`, `head`, `wing_left`, `wing_right`, `tail`.
- **Moving the back.** The rider floats or sinks. Re-check the seat `position` in the entity file.
- **Forgetting the texture size.** A 128 texture on a 64 geometry shows scrambled UVs.
- **Exporting as Java model.** Use the Bedrock export, not the Java one.
- **Rotating `wing_right` backward.** The placeholder has the right wing mirrored; keep the sign of the `z` rotation opposite between the two wings.
