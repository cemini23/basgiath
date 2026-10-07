# Basgiath — Java edition

> Fan-made. Not official. Not affiliated with Rebecca Yarros, Entangled Publishing, or Red Tower Books.

A free, fan-made war college for Minecraft. Cross the narrow span, then ride.

This is the **Java edition**, for NeoForge. It is the same map as the Bedrock add-on, raised
by the same generator — the two are one project, published twice.

## What it is

You raise the college with one command, where you are standing. Nothing is a pre-built
world you have to download and drop in: the map is generated from source, so you can raise
it in any world you already have.

- **The Parapet.** Climb to a one-block span over a deep chasm, in a storm, with wind that
  pushes you and a two-block gap in the middle. A fall kills you and sends you back to the
  start. Cross it, and the far tower becomes your respawn point.
- **The bond.** A dragon has to choose you before anything else opens. Walk to the dell
  without crossing the span and nothing happens.
- **The signet.** Answer four questions, get one of eight original results, from Stormcaller
  to Tidekeeper. It stays on your player across deaths and restarts.
- **The wing.** The college keeps a roster of the last 24 riders who earned a signet.
- **The Gauntlet.** A scored cliff run with a stopwatch and a rope penalty.
- **The vault desk.** A working bank, in marks that convert nine for one.
- **Three codices.** Readable items, written for this map.
- **A dragon you can ride.** Fly it from the dell. A flight readout on your action bar shows
  speed, altitude, and stamina.
- **The Vale, its own dimension.** Java-only. A flat world under a fixed midnight, so the
  crossing is always in the dark. Go there with `/basgiath vale`. The Bedrock edition cannot
  do this one, and builds the same map in the overworld instead.

## Requirements

| | |
|---|---|
| Minecraft | **1.21.1** |
| Loader | **NeoForge** 21.1.x (built against 21.1.256) |
| Required mod | **[GeckoLib](https://modrinth.com/mod/geckolib)** 4.9.x |

GeckoLib is required. The dragon's model and its two animations are GeckoLib assets, and
without it the dragon will not render.

## Raising the college

Stand where you want it, then run:

```
/function basgiath:build
```

The college rises around you over about fifteen seconds. Stay still, and close chat.

To summon a dragon on its own, run `/function basgiath:summon_dragon`.

## Notes

- Everything is built from vanilla blocks. No official art, no book text, no series names
  anywhere in the pack. Every line of the codices and every signet result is original
  writing for this map.
- Free, and it stays free. No paid tier, no ads, no Marketplace.
- The Bedrock edition of the same map is on MCPEDL and CurseForge.

## Licence

All rights reserved. See `LICENSE`. Free to download and play; not for sale, and not to be
redistributed as part of anything paid.
