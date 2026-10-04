# Finish plan — Basgiath

Date: 2026-10-03. Status: shipped. The code in `scripts/` and `addon/` is the spec. Where this plan and the code differ, follow the code.

Commit `65c4e18` changed four things after this plan was written:

- Both packs and the world need Bedrock 1.21.90 or newer.
- The lodestone form listens on `beforeEvents.playerInteractWithBlock`. An empty-hand interact opens it. The script does not need Beta APIs.
- The build places one stone under `build_anchor` and gives that stand resistance.
- The world writes the `gametest` byte and the `beta_apis` byte. Stable script modules do not need the Beta APIs toggle.

The player starts on a glowing path at their feet. The build does not lift them to Y=80. Glowing stairs climb 32 blocks to the span. A fall from the span is fatal. Respawn stays on that path until the east tower.

## Goal

Ship a free fan-made Bedrock map a stranger can install and play.

Proven means a command, a file, or a server log. A real Bedrock client is the only check for the model, the texture, and the form UI.

## Task 0 — repo name

- GitHub repo name: `basgiath`.
- Remote: `https://github.com/cemini23/basgiath.git`.
- Pack ids stay `dragon_rider:*`.
- Geometry id stays `geometry.dragon_rider`.
- Pack UUIDs stay as they are in the two manifests.
- Artifact names: `dist/basgiath.mcaddon` and `dist/basgiath.mcworld`.

## IP

Allowed in the title and in the function folder: the place name Basgiath.

Keep these strings out of `addon/` and `scripts/`:

`fourth wing`, `empyrean`, `iron flame`, `onyx storm`, `dragonkind`, `tairn`, `andarna`, `sgaeyl`, `xaden`, `violet sorrengail`, `yarros`.

No book text. No official art. Original lines only.

In-game credit line (short): `Fan-made. Not official. Not affiliated with any publisher.`

Full credit line (README, listing, clips): `Fan-made. Not official. Not affiliated with Rebecca Yarros, Entangled Publishing, or Red Tower Books.`

## What the player does

1. Open `basgiath.mcworld`, or import `basgiath.mcaddon` into a flat world with cheats on.
2. Run `/function basgiath/build`.
3. Cross the Parapet.
4. Touch the lodestone in the Quad. Answer the signet form.
5. Run `/function basgiath/summon_dragon` in the valley and ride.

## Coordinate contract

`+X` east, `+Y` up, `+Z` south. The anchor is an invisible armor stand named `build_anchor`. Its feet are the origin. Every build command runs `at` that stand and uses relative coordinates.

The world floor is Y=-64. A 40-block chasm must not fill below that. `build.mcfunction` lifts the player first when their feet are at or below Y=-20:

```
execute as @s if entity @s[y=-64,dy=44] run tp @s ~ 80 ~
execute at @s run summon armor_stand "build_anchor" ~ ~ ~
```

`execute at @s` is required after `tp`, because a function does not follow the player.

Surface block is relative Y=-1. The player’s feet on that block are relative Y=0. The Parapet deck is higher, at block Y=8, so feet are Y=9.

## Build staging

Bedrock applies a scoreboard change immediately. A tick file that sets `#stage` and then tests the new value runs every stage in one tick. Use a copy:

```
scoreboard players operation #now map_state = #stage map_state
execute if score #now map_state matches 1 as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_01
execute if score #now map_state matches 1 run scoreboard players set #stage map_state 2
```

One stage per tick. `#now` matches 0 runs `basgiath/live`. Unset scores match nothing, so a world that has not been built does not run live logic.

`scripts/build_map.py` writes the stage files, `build.mcfunction`, `tick.mcfunction`, `live.mcfunction`, `summon_dragon.mcfunction`, and `functions/tick.json`.

Each stage holds at most 50 commands. `fill` volumes are sliced on the longest axis until each box is at most 32768 blocks.

## Map

Clear and rebuild a pad from X=0..170, Z=0..150. Lay grass at Y=-1. Carve the chasm after the ground fill.

### Parapet (the clip)

- Chasm air: X=18..74, Z=8..32, Y=-39..-1, after a deepslate shell.
- Water: Y=-39..-37 inside the chasm. The deepslate floor stays at Y=-40.
- Deck: one block wide, `stone_bricks`, at Y=8, Z=20, X=15..77.
- Gap: X=45 and X=46 stay air. Set them to air again in the last stage.
- No rail and no center support.
- West tower: X=2..14, Z=12..28, deck at Y=8, block stairs up from Y=-1.
- East tower: X=78..90, Z=12..28, deck at Y=8, stairs down to the quad path.

### Quad

- Plaza: X=96..168, Z=4..78, `stone_bricks` at Y=-1.
- Dais: X=124..132, Z=36..44, one block higher.
- Lodestone at X=128, Y=0, Z=40. The signet script already opens on a lodestone.
- Four wool poles in cyan, purple, orange, and light gray.
- Bell tower on the north-east corner of the plaza. A `bell` and a `sea_lantern` on top.
- Lantern posts on the plaza.

### Dorms

Three spruce-and-stone barracks south of the quad, around Z=88..122. Doorways are air gaps. Bunks are wool, not bed blocks. Lanterns inside.

### Threshing Valley

A bowl west of the dorms and south of the chasm: about X=8..78, Z=86..148. Floor dropped to Y=-6. A ring of stone pillars. A center pad. Gold block at the pad center.

### Checkpoints

`live.mcfunction`, relative to the anchor:

| Place | Feet position | Tag |
| --- | --- | --- |
| West tower deck | 8 9 20 | `cp_west` |
| East tower deck | 84 9 20 | `cp_east` |
| Quad, south of the stone | 128 0 48 | `cp_quad` |
| Valley pad | 43 -5 117 | `cp_valley` |

`spawnpoint` uses the anchor position, not the player position. Tag the player so the success text does not repeat.

Wind, every 4 ticks, only on the deck: `tp @s ~ ~ ~0.18` after `at @s`, plus smoke particles every tick. Rescue: a player inside the chasm box goes to `8 9 20`.

Last stage: night, `weather thunder 999999`, gamerules for a map (no mob spawn, no weather cycle, no daylight cycle, keep inventory, hide command feedback), `gamemode adventure @a`, titles `Welcome, candidate` / `Cross the Parapet`, the short credit line, and `tp` the nearest player to the west deck.

`/function basgiath/summon_dragon` summons `dragon_rider:dragon` above the valley pad. If the anchor is missing, it tells the player to run the build.

Done. The old absolute functions `parapet_wind.mcfunction`, `parapet_checkpoint_a.mcfunction`, and `parapet_checkpoint_b.mcfunction` are deleted. Do not add them back.

## Signet wing

Keep the four original archetypes. On a finished form, append `{name, signet}` to world dynamic property `dragon_rider:wing` (JSON, max 24 entries). Tell the player how many riders the wing has. This is the persistent wing. Do not rename the property ids.

## Dragon

Edit `scripts/build_dragon_model.py` only. Re-run it. It must keep:

- Geometry id `geometry.dragon_rider`
- Format `1.12.0`
- Bone names `body`, `head`, `wing_left`, `wing_right`, `tail`
- Texture path `textures/entity/dragon`
- A chest whose top is Y=32 and whose Z range covers 0, so seat `[0, 2.1, -0.2]` stays valid
- Cube origins in model space, not parent-local space

Add a neck, a snout, a lower jaw, four horns, three wing segments per side, four legs with feet, and a tapering tail with a spade. Wing pivots sit on the shoulders. Left wing pivot X is positive. Right wing pivot X is negative. The flap is a Z rotation, so the wings extend along X.

Texture 128×128. Belly lighter than the back. Membrane has veins. Eyes sit on the side faces of the head. Horns are bone-colored. Save the PNG with no timestamp so two runs match byte for byte.

`visible_bounds_width` at least 14. Do not edit the entity seat.

Idle animation may also move `head` and `jaw`. Wing signs stay opposite.

## World zip

`scripts/nbt_le.py` writes little-endian NBT. `scripts/build_world.py` writes `dist/basgiath.mcworld`.

The zip root contains `level.dat`, `levelname.txt` (`Basgiath`), `world_behavior_packs.json`, `world_resource_packs.json`, and copies of both packs. Do not wrap those files in an extra folder.

`level.dat` header: storage version 10 as uint32 LE, then payload length as uint32 LE, then a named root compound with an empty name.

World settings: flat generator, creative (the build switches to adventure), cheats on, commands on, no mob spawn, night, rain and thunder levels at 1, experiments include `experiments_ever_loaded` and `beta_apis`. Spawn at 0, -60, 0. Flat layers: one bedrock, two dirt, one `minecraft:grass_block`. Pack UUIDs and versions come from the manifests. Do not invent new UUIDs.

`scripts/package.sh` runs the dragon generator, the map generator, the mcaddon zip, and the world zip.

## CI

Keep every current check. Add:

- `git diff --exit-code` on the generated functions and the dragon PNG
- `python3 scripts/test_release.py`
- The wider name list above
- `bash -n` on every script in `scripts/`

`test_release.py` checks fill volumes, the gap coordinates, the lodestone command, required bones, texture size, unique UUIDs, and the forbidden-name grep.

## Docs

A stranger needs: install the mcworld, run one function, play the three beats, and see the full credit line. Update `README.md`, `BUILD_CHECKLIST.md`, `DESIGN.md`, `DISTRIBUTION.md`, and `docs/BLOCKBENCH-SPEC.md`. Add `docs/LISTING.md` with the MCPEDL and CurseForge text, six vertical clip scripts, and the tag list.

## Verify

Local, before each commit:

```
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh
python3 scripts/test_release.py
```

Bedrock Dedicated Server can load the behavior pack, run the build, and summon the entity. It cannot judge the model or the texture. Say that in the final report.

## Out of scope

No Marketplace listing. No paid file. No edits outside this repo. No change to pack UUIDs, pack ids, or the geometry id.
