# Dragon Rider Map

A free, fan-made Minecraft **Bedrock** map and add-on, built for the *Empyrean* fandom.

**Not official. Not affiliated with Rebecca Yarros, Entangled Publishing, or Red Tower Books. Not monetised. No official art.**

## Why this exists

The fandom is peaking right now. The official "Dragonkind" experience launched 2026-10-01 and drew half a million people on day one. TikTok is full of "which dragon claims you" clips. This project rides that attention with a free, clippable Minecraft world, and grows into a persistent Rider's Quadrant later.

## What ships first (v0)

A walkable war-college map with one strong clippable moment.

1. **The Parapet** — a narrow, swaying stone crossing over a chasm, in bad weather, with wind that pushes you. This is the clip.
2. **The Quad** — an open parade ground with a Bonding Stone that runs the "Which signet are you?" form.
3. **The Bonding Stone** — an in-game block that gives a shareable signet result.

A rideable dragon is phase 2. It is the hardest part and it is not needed for the first wave.

## Why Bedrock

- It runs on phones, tablets, and consoles. The fandom is on phones.
- Free distribution through MCPEDL and CurseForge.
- Java is PC-only, so it cuts off most of the audience.

## Layout

```
README.md              this file
DESIGN.md              the map spec and the Parapet moment
BUILD_CHECKLIST.md     step-by-step in-game build
DISTRIBUTION.md        where it ships and how it gets found
docs/IP-RULES.md       the non-negotiable fan-project rules
docs/BLOCKBENCH-SPEC.md the dragon model spec (bones, UV, export)
addon/
  behavior_pack/       manifest, dragon entity, Parapet functions, scripts/main.js
  resource_pack/       manifest, client entity, model, animations, texture
scripts/               validate.sh, package.sh
briefs/                the research and build handoffs
```

## How to build

1. Install **Minecraft Bedrock** (Windows 11 or a device) and enable the in-game **Bedrock Editor**.
2. Copy `addon/behavior_pack` and `addon/resource_pack` into the game's development packs folder.
3. Create a flat world. Enable both packs and the **Beta APIs** toggle.
4. Build from `BUILD_CHECKLIST.md`.
5. Export the world as `.mcworld` and the packs as `.mcaddon`.

## How to ship

MCPEDL and CurseForge. Free only. See `DISTRIBUTION.md`.

## Status

v1 code added. The dragon is a placeholder box until art exists. Nothing is built in-world yet. The signet script still needs an in-game test.

## Version note

Bedrock uses year versioning. Current stable is **26.20**. The manifests here target `@minecraft/server` 2.x. If the game rejects the pack, bump the dependency versions to match your game build.
