# Z1 — Threshing (valley)

Zone: `scripts/zones/valley.py` (stage range 49–60, not written by this module).
Reported by: Threshing zone agent. Date: 2026-10-04.

## What I built

### Land: a forested dell, not a summoning pad

The old module emitted a pillar ring, a stone platform at `x=38..48, z=112..122`,
and a `gold_block` at `43, -2, 117`. All of that is gone. The new `build(ctx)`
places a shallow bowl inside `x=16..70, z=94..140`:

- **Floor** stays at `y=-2`. One `fill` of `grass_block` for the whole
  footprint (55 x 1 x 47 = 2585 blocks, one command). One `fill` of `air` at
  `y=-1` opens the dell one step below the college ground. Nothing is dug below
  `y=-2`.
- **The pad** at `x=42..44, z=116..118` is `moss_block` at `y=-2`. No
  `gold_block` anywhere. `y=-1..1` over the 3 by 3 is clear, so a cadet can
  stand on it and the old summon aim at `43, -1, 117` still lands.
- **29 squat oaks** (`oak_log` trunk three tall, flat `oak_leaves` canopy, one
  leaf cross above). They form bands on the north rim, the west and east
  flanks, and a run of greenery south. Every trunk and every leaf block is
  inside the zone.
- **Open ground in the middle**: `x=36..54, z=110..126`, plus a one-block
  margin, takes no tree and no ground cover.
- **The lodestone box** `x=48..52, z=128..132` takes no tree, no leaf, and no
  ground cover. The courtyard agent's lodestone drops into bare grass.
- **66 ground-cover blocks**: `short_grass` (weighted), `dandelion`, `poppy`,
  `cornflower`, `oxeye_daisy`, `azure_bluet`, `allium`,
  `lily_of_the_valley`. Placement is a fixed pattern, not random, and skips
  every trunk, the open middle, the lodestone box, and the keeper post.
- **Roll-keeper**: one `stone_bricks` block at `50, -2, 124` and
  `summon armor_stand "Roll-keeper" ~50 ~-1 ~124`. The stand at `y=-1` stands
  on the stone.

Budget: **187 commands** for the whole zone (cap 400). Largest `fill` is the
floor, 2585 blocks (cap 32768). Air fill volume from this zone is 2585 (the
release test's own cap is 80000). No water block. Vanilla blocks only.

### Event: `live_lines()`

Thirteen lines, each one already prefixed with the anchor execute
(`execute as @e[type=armor_stand,name="build_anchor",c=1] at @s ...`). They are
not called from `build()`; the integrator appends them to
`basgiath/live.mcfunction`. The chain is a tag ladder, so each step fires once
and never repeats on the next tick:

| Step | Selector | Commands |
| --- | --- | --- |
| 1. the choosing | `@a` in the open centre, `tag=!bonded` | add `bonded`; then for `tag=bonded,tag=!bondcall`: summon `dragon_rider:dragon` at `~1 ~ ~` beside the player, `scoreboard players set #bond map_state 1`, one tellraw, add `bondcall` |
| 2. the relic | `tag=bondcall,tag=!relic` | one tellraw, add `relic` |
| 3. the trial | `tag=relic,tag=!trial` | one tellraw, add `trial` |
| 4. the pad | `@a[x=~42,y=~-2,z=~116,dx=2,dy=3,dz=2,tag=trial,tag=!flew]` | one tellraw, add `flew` |
| 5. the roll-keeper | `@a[x=~48,y=~-2,z=~122,dx=4,dy=3,dz=4,tag=flew,tag=!named]` | one tellraw, add `named` |

In every step the "done" tag is added by the **last** command of that step.
That is deliberate: the tellraw, the summon and the score run first, and the
guard lands after them, so a single tick cannot double-fire. If the anchor
stand is missing, every line is a no-op instead of an error.

The five tellraw lines are original. No person name, no dragon name, no book
text, no series title:

1. "A dragon has chosen you. You did not choose it. Stand still and let it look."
2. "A relic mark burns onto your arm, shaped like the one that chose you."
3. "Hold your seat. The dragon will fly and turn. Do not let go."
4. "You held. Walk south to the roll-keeper and give only the colour."
5. "Say the colour, nothing more. The full name stays with you and the roll-keeper."

The dragon acts on the player; the player never picks it. There is no
"choose a dragon" command anywhere in the file.

## Files touched

- `scripts/zones/valley.py` — rewritten (build + `live_lines`).
- `reports/zones/z1-threshing.md` — this report.

No other repository file was created, edited, or deleted. Nothing outside the
zone and this report was written. `build_map.py`, `package.sh`, and
`test_release.py` were not run. No `git checkout`, `git restore`, `git reset`,
or `git clean`. Nothing committed or pushed. No key printed. No external model
was called.

## Commands I ran

- `python3 /tmp/verify_z1.py` — a throwaway harness (outside the repo) that
  loads `scripts/zones/valley.py` through a stub context with the same
  `MAX_FILL` splitting as the driver, then checks:
  - command count 187 < 400;
  - every fill and setblock inside `x=16..70, z=94..140` and at or above `y=-2`;
  - no `gold_block`, no water;
  - no `oak_log` / `oak_leaves` in the lodestone box, on the pad, or in the
    open middle;
  - the pad's walk level (`y=-1..1`) is clear and its floor is `moss_block`;
  - every `fill` volume <= 32768;
  - all 13 live lines start with the anchor execute and are single-line.
- `python3 -m py_compile scripts/zones/valley.py`.

## What I could not do

- **No in-game run.** I did not run `build_map.py` or the Bedrock client, so
  the dell's look and the tick behaviour are checked statically, not played.
- **`live_lines()` is not wired in.** The task says the integrator appends it
  to the live function. Until then the event does not run.
- **The objective is assumed.** `map_state` is created by
  `build_text()` in `scripts/build_map.py`, and the tick loop only reaches
  `basgiath/live` after the build, so `scoreboard players set #bond map_state 1`
  is safe. A zone may not add objectives of its own, so I did not.
- **`#bond` reading.** The zones README says the shared signal is
  `#bond map_state` (0 = no bond, 1 = a dragon chose the player), so that is
  exactly what line 3 sets. I did not also set a per-player score on
  `map_state`; if the signet agent needs a per-player value, tell me and I will
  add `scoreboard players set @s map_state 1` in the same step.
- **Block id assumption.** `short_grass` is the current Bedrock id (the
  manifest targets `min_engine_version` 1.21.90, and the rename landed in
  1.20.80). If the target client is older, this id must fall back to `grass`.
- **Summon syntax.** The Roll-keeper line uses the same name-before-position
  order as the existing `summon armor_stand "build_anchor" ~ ~ ~`, which
  Bedrock's optional-parameter reordering accepts. I could not test it on a
  device.
- **Removed geometry is not restored.** The old stone platform and the
  `gold_block` pad are intentionally gone. Any other agent that assumed that
  pad no longer has it; the task required the rework.
