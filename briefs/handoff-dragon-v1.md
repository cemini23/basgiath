# Routed handoff — Dragon Rider Map v1 (dragon + Parapet + packaging)

LANE: hard
PROFILE: claudio
WORKDIR: repo root (GitHub: basgiath)
EXECUTOR: Grok CLI implements. Plan is filled below, so skip the Grok plan step.

## WorkDir

repo root (GitHub: basgiath)

## Target

Build the v1 code for the Dragon Rider Map: a custom rideable flying dragon entity, the Parapet gameplay functions, and a packaging + validation script. The world geometry is built by hand in the Bedrock Editor and is not part of this task.

## Summary

The repo has a working v0 scaffold: two pack manifests, `scripts/main.js` (the signet form), and docs. This task adds the code for a custom rideable dragon and the Parapet mechanics, plus a build and package script. No art. Use a placeholder box geometry.

## Success criteria

1. Behavior pack gains a custom entity `dragon_rider:dragon` with `minecraft:rideable` (one seat, player control), flying movement and navigation, and rider control.
2. Resource pack gains a client entity JSON, a placeholder box geometry, a render controller, an idle and a fly animation, and a language string naming the dragon.
3. Every entity and resource JSON parses and uses valid Bedrock schema shape (`format_version`, `minecraft:entity`, `minecraft:client_entity`).
4. `scripts/package.sh` builds `dist/basgiath.mcaddon` from the two packs.
5. `scripts/validate.sh` parses every `addon/**/*.json` and exits 0. It exits non-zero on any parse error. It also fails if the pack UUIDs are not unique.
6. The existing signet script still passes `node --check`.
7. No file names the book, its characters, or its signets. Entity id and pack strings use original wording.

## NEVER

- Do not use the series name, character names, or the book's signet names in any file, id, or string.
- Do not add money, donation, or Marketplace hooks.
- Do not download or include third-party art, models, or textures.
- Do not change the pack UUIDs in the existing manifests.
- Do not edit `docs/IP-RULES.md` or `DISTRIBUTION.md`.
- Do not commit or push.

## Plan

Implement in this order. Keep every JSON minimal but valid.

### A. Behavior pack — dragon entity

Create `addon/behavior_pack/entities/dragon.json`. Group `dragon_rider` with description `identifier: "dragon_rider:dragon"`. Include:
- `minecraft:type_family` with family `dragon`.
- `minecraft:health` (about 200), `minecraft:physics`, `minecraft:collision_box`, `minecraft:pushable`, `minecraft:knockback_resistance`.
- `minecraft:navigation.fly`, `minecraft:movement.fly`, and `minecraft:movement` so it flies.
- `minecraft:rideable` with `seat_count: 1`, `family_types: ["player"]`, `controlling_seat: 0`, `pull_in_entities: false`, and `interact_text`.
- `minecraft:behavior.controlled_by_player` so the rider steers while seated.

JSON has no comments. Put tuning notes in `addon/behavior_pack/entities/README.md` instead.

### B. Resource pack — client entity, model, animation

- `addon/resource_pack/entity/dragon.entity.json`: `minecraft:client_entity` with `identifier: "dragon_rider:dragon"`, a geometry ref, a texture ref, a material, `render_controllers`, and `scripts.animate` for idle and fly.
- `addon/resource_pack/models/entity/dragon.geo.json`: a placeholder geometry. A body box, a head box, two wing boxes, and a tail box, in `minecraft:geometry` format `1.12.0`. Use small integer UVs over a blank texture.
- `addon/resource_pack/render_controllers/dragon.render_controllers.json`: one controller that renders the default texture.
- `addon/resource_pack/animations/dragon.animation.json`: `animation.dragon.idle` with a small tail sway, and `animation.dragon.fly` with a wing flap. Bind both from the client entity.
- Append to `addon/resource_pack/texts/en_US.lang`: `entity.dragon_rider:dragon.name=Dragon`.

### C. Parapet functions

Create `addon/behavior_pack/functions/`:
- `parapet_wind.mcfunction`: a short set of commands that push players on the span.
- `parapet_checkpoint_a.mcfunction` and `parapet_checkpoint_b.mcfunction`: set spawn for nearby players.
Exact coordinates are placeholders. List which numbers to replace in `addon/behavior_pack/functions/README.md`.

### D. Scripts

- `scripts/package.sh`: zip `addon/behavior_pack` and `addon/resource_pack` into `dist/basgiath.mcaddon`. Create `dist/`. Make executable.
- `scripts/validate.sh`: parse every `addon/**/*.json` with `python3 -c "import json;json.load(open(f))"` and fail on error. Then read the four UUIDs from the two manifests and fail if any repeat. Make executable.

### E. Docs

- Add `addon/behavior_pack/entities/README.md` and `addon/behavior_pack/functions/README.md`.
- Update the `README.md` status line: v1 code added; the dragon is a placeholder box until art exists.

## Verify

```
# from the repo root
test -f addon/behavior_pack/entities/dragon.json
test -f addon/resource_pack/entity/dragon.entity.json
test -f addon/resource_pack/models/entity/dragon.geo.json
test -f addon/resource_pack/render_controllers/dragon.render_controllers.json
test -f addon/resource_pack/animations/dragon.animation.json
test -f addon/behavior_pack/functions/parapet_wind.mcfunction
test -f scripts/package.sh
test -f scripts/validate.sh
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh && test -f dist/basgiath.mcaddon
grep -ril "fourth wing\|empyrean\|tairn\|andarna\|basgiath" addon/ scripts/ || echo "no IP leak"
```

## Residual / further implementation

Report if: (a) the dragon needs a real geometry from Blockbench, (b) flight needs a test world, (c) the Parapet coordinates are still placeholders.
