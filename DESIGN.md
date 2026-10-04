# Design

## The one clip

Every fan project needs one clip that travels. For this map it is **the Parapet**: a one-block-wide stone span over a deep chasm, in wind and rain, that the player must cross. It looks dangerous. It reads in two seconds on a phone. It is the first thing in every dev-log video.

## The world

The player runs `/function basgiath/build`. `scripts/build_map.py` writes the functions. Do not build this by hand.

Four zones, in journey order.

### 1. The Parapet
- The player starts on a glowing path at their feet. The build does not lift them into the sky.
- Glowing stairs climb 32 blocks to the roof. A wall on the roof has one gap onto the span.
- The air under the span goes down to the ground. A fall from the span is fatal.
- The player respawns on the ground path. The east tower is the first checkpoint that moves the spawn.
- A one-wide stone path across, broken in the middle by a two-block gap.
- Wind: particles plus a repeating push, so the crossing feels unsafe.
- Rain and thunder locked on for mood.

### 2. The Quad
- An open parade ground, about 80 by 80.
- A **Bonding Stone** (a lodestone) at the centre. An empty-hand interact opens the signet form. The script listens before the block use, and it cancels the lodestone screen. No compass is required.
- Stepped bleachers, four coloured wool standards, and a bell tower for silhouette.

### 3. The Dorms
- Three spruce barracks south of the Quad.
- Wool bunks, lanterns, and open doorways.

### 4. The valley
- A sunken bowl with a ring of pillars and a gold pad.
- `/function basgiath/summon_dragon` summons the rideable dragon on that pad.

## The signet form

Three questions, four outcomes. It runs from the Bonding Stone. The script uses stable `@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0. Do not enable Beta APIs. The result is stored as a dynamic property, so it persists across sessions. See `addon/behavior_pack/scripts/main.js`.

The outcomes are original archetypes — Stormcaller, Shadowwalker, Emberwright, Stoneward. They are original names, so the work stays transformative.

## Scope cuts, declared up front

- **No custom dimension.** Bedrock custom dimensions are experimental and void-only. Use an Overworld map plus teleports.
- **No custom block art.** The college is vanilla blocks. The dragon texture is generated, and it is original.

## What persists

The signet result is a player dynamic property. The wing roster is a world dynamic property. Both survive a reload. The roster keeps the last 24 riders.
