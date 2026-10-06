# Design

## The one clip

Every fan project needs one clip that travels. For this map it is **the Parapet**: a one-block-wide stone span over a deep chasm, in wind and rain, that the player must cross. It looks dangerous. It reads in two seconds on a phone. It is the first thing in every dev-log video.

## The world

The player runs `/function basgiath/build`. `scripts/build_map.py` writes the functions. Do not build this by hand.

Seven beats, in the canon order the first year runs them. The zone modules under `scripts/zones/` each own one beat.

### 1. The Parapet
- The player starts on a glowing path at their feet. The build does not lift them into the sky.
- Glowing stairs climb 32 blocks to the roof. A wall on the roof has one gap onto the span.
- The air under the span goes down to the ground. A fall from the span is fatal.
- The player respawns on the ground path. The east tower is the first checkpoint that moves the spawn.
- A one-wide stone path across, broken in the middle by a two-block gap.
- Wind: particles plus a repeating push, so the crossing feels unsafe.
- Rain and thunder locked on for mood.

### 2. Formation — the courtyard
- A walled courtyard behind a 10-block-thick stone ring, 8 blocks tall, with one opening. That opening is the way in from the Parapet.
- Four wings, three sections (Flame, Claw, Tail), three squads each. A square of armour stands teaches the shape.
- Roll call reads the death roll. The lines are original.
- Stepped bleachers, four coloured wool standards, and a bell tower for silhouette.
- The plaza marker is a chiseled stone block under a lectern. It is no longer a lodestone: the signet moved to the dell, after the bond.

### 3. College — the Citadel group
- The Dragon Rotunda: three stories, a polished floor, a glass dome, and four doors between orange and black pillars.
- The keep with one arched door and an original rider-and-dragon line. Not the book line.
- One dorm block, three stories, four rows of beds, and one private room for a bonded rider.
- A classroom shell with lecterns.

### 4. Gauntlet — the cliff
- A stepped stone cliff east of the dorms. Six terraces, each one turn higher than the last.
- Six obstacles, in canon order: a log, rising granite pillars, a stone ring with one gap, cobble clusters, a ladder chimney, and an oak ramp to the summit.
- Chain ropes hang beside every leg. Touching one adds 30 seconds, and the live tick says so.
- A timekeeper stand at the summit.

### 5. Presentation — the flight field
- A box canyon south of the college, its rim cut at the span-deck height.
- A footpath down the middle between a gate, bleachers, and a dais.
- Six wool posts are the dragon line. A line for the eye, not a menu.
- Nothing here summons a dragon and nothing here offers a choice. The walk is for the dragons to look.

### 6. Threshing — the dell
- A forested dell southwest of the courtyard, one block below the college floor, with a moss landing pad.
- Stand in the open and a dragon chooses you. You do not choose it.
- The bond is a scoreboard flag (`#bond map_state`). The relic, the flight trial, and the roll-keeper follow it.
- `/function basgiath/summon_dragon` still places the rideable dragon on the pad for the ride.

### 7. The Signet
- A lodestone on the dell floor at 50, -1, 130. The script opens the form only at that stone, and only after the bond is set. A lodestone anywhere else is left alone.
- No compass is required. The script listens before the block use, and it cancels the lodestone screen.
- Moved here from the plaza: canon puts the signet weeks after the bond, not on day one.

## The signet form

Four questions, eight outcomes. It runs from the signet stone in the dell, and only once the bond is set. Each archetype is offered by two questions, so every outcome is reachable and none is favoured. The script uses stable `@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0. Do not enable Beta APIs. The result is stored as a dynamic property, so it persists across sessions. See `addon/behavior_pack/scripts/main.js`.

The outcomes are the map's own archetypes — Stormcaller, Shadowwalker, Emberwright, Stoneward, Mender, Wardsmith, Chronicler, Tidekeeper. The rules ban character names, book text and official art. They put no limit on which powers the map may have, so this set is free to grow.

## Scope cuts, declared up front

- **No custom dimension.** Bedrock custom dimensions are experimental and void-only. Use an Overworld map plus teleports.
- **No custom block art.** The college is vanilla blocks. The dragon texture is generated, and it is original.

## What persists

The signet result is a player dynamic property. The wing roster is a world dynamic property. Both survive a reload. The roster keeps the last 24 riders.
