# Design

## The one clip

Every fan project needs one clip that travels. For this map it is **the Parapet**: a one-block-wide stone span over a deep chasm, in wind and rain, that the player must cross. It looks dangerous. It reads in two seconds on a phone. It is the first thing in every dev-log video.

## The world (v0 scope)

Three build zones, in order.

### 1. The Parapet
- A chasm about 40 blocks deep and 60 blocks wide.
- A one-wide stone path across, broken in the middle by a two-block gap.
- Wind: particles plus a repeating push, so the crossing feels unsafe.
- Rain and thunder locked on for mood.
- A checkpoint at each end.

### 2. The Quad
- An open parade ground, about 80 by 80.
- A **Bonding Stone** (a lodestone) at the centre. Interacting with it opens the signet form.
- Bleachers, banners, and a bell tower for silhouette.

### 3. The Dorms (stretch)
- Simple barracks. Cut this first if time is short.

## The signet form

Three questions, four outcomes. It runs from the Bonding Stone. The result is stored as a dynamic property, so it persists across sessions. See `addon/behavior_pack/scripts/main.js`.

The outcomes are original archetypes — Stormcaller, Shadowwalker, Emberwright, Stoneward. They are **not** the book's signets. This keeps the work transformative.

## Scope cuts, declared up front

- **No rideable dragon in v0.** It is the hardest part. Ship the map first.
- **No custom dimension.** Bedrock custom dimensions are experimental and void-only. Use an Overworld map plus teleports.
- **No custom art.** Use vanilla blocks. The resource pack carries text only.

## What v1 adds

A rideable dragon, a Threshing Valley, and a persistent wing that grows across sessions. That is the thing the official 10-minute experience is not.
