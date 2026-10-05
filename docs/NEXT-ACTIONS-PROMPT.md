# Basgiath — next actions prompt

**Paste this whole file into a fresh session in this repo** (`/Users/claudiobarone/Projects/dragon-rider-map`, GitHub `cemini23/basgiath`). It is written for a Claude Code or Grok Build session that can shell out.

---

## Where the project stands (2026-10-05)

- **The build is green.** `scripts/bench_bds.sh` passed against the official Bedrock dedicated server `bedrock-server-1.26.52.3`: `pack_error=none`, the `.mcworld` loads, the span / both gaps / column are correct, and both keeper lecterns are present.
- **The story beats exist.** Parapet, Quad + signet form, dorms, Threshing valley, the two keepers (scroll + roll, anchor-relative), the Gauntlet with real scoring, and the rideable dragon.
- **The gate chain is in place.** `package.sh → validate.sh → node --check → test_release.py → bench_static.py`. CI runs it. `bench_bds.sh` runs on a RunPod pod, not on a Mac.
- **Not yet done:** the add-on packaging is **not hardened**, and there is **no headless test of behaviour** (only of world shape and pack load).

## Read first

1. `docs/IP-RULES.md` — **non-negotiable. This file wins on any conflict.**
2. `README.md`
3. `DESIGN.md`
4. `DISTRIBUTION.md` and `docs/LISTING.md`
5. `BUILD_CHECKLIST.md`
6. `scripts/package.sh`, `scripts/validate.sh`, `scripts/test_release.py`, `scripts/bench_bds.sh`

## Task order

Do these in order. Finish a whole numbered task before starting the next. If you run out of room, stop at a clean boundary and report exactly what you completed.

### 1. Harden the add-on packaging (highest value)

`scripts/package.sh` builds `dist/basgiath.mcaddon` and `dist/basgiath.mcworld` but does **not** validate the manifests. A duplicate or mismatched UUID breaks the Bedrock import dialog and the player never sees the world — the single biggest drop-off source on the path to fan reach.

Add a manifest validator to `scripts/package.sh` (or a new `scripts/validate_manifests.py` the script calls). It must **fail the build** if any of these is false:

- There are exactly **two packs**: `addon/behavior_pack/manifest.json` and `addon/resource_pack/manifest.json`.
- Every `header.uuid` and every `modules[].uuid` is a valid UUID and **unique across both packs** (four UUIDs, no repeats). *State today: all four are unique and valid — this check protects that.*
- **The packs are linked.** The behavior pack declares a `dependencies` entry on the resource pack's `header.uuid` (with a version range), so a player who enables only the behavior pack still loads the resources. **State today: no cross-pack dependency exists — add it, then validate it resolves.** Every `dependencies[].uuid` must resolve to a pack's `header.uuid`; a dangling dependency is a build failure.
- Both packs declare the dependency on `@minecraft/server` at `2.0.0` and `@minecraft/server-ui` at `2.0.0`, and the versions are **not bumped**.
- `min_engine_version` is at most the release the shipped world targets (currently Bedrock **1.21.90**). A too-high minimum silently blocks older clients.
- The `.mcaddon` contains **both** packs, so it imports in one click on Windows, Android, iOS, and console.

Do **not** change any existing UUID. Adding a dependency is allowed; changing a `header.uuid` is not.

Keep the existing checks. Add a `test_release.py` assertion that the validator ran and passed.

### 2. Add a behaviour test layer (Bedrock GameTest)

The bench proves the world loads and the blocks are where they should be. It cannot prove **behaviour**: dragon flight, spawn, entity synchronisation, the rider seat. Do that with **Bedrock's own GameTest** path (`@minecraft/server-gametest` in a dev/test pack), **not** a Java toolchain — Java Fabric cannot compile to Bedrock.

Start with **one** test that proves a real behaviour: summon `dragon_rider:dragon` on the valley pad and assert the entity exists, is rideable, and moves when driven. Do not invent a big framework. One honest test beats four that pass trivially.

**Do not** enable Beta APIs in the **shipped** behavior pack to do this. Keep any GameTest harness in a separate dev pack that is not part of `dist/`.

### 3. Extend the test bench: the container + NBT pair

Keep the RunPod BDS bench. Add the pair that removes most manual clicking:

- `itzg/docker-minecraft-server` — headless container lifecycle for world-gen and pack-load validation.
- A Bedrock **LevelDB NBT** reader/writer — set an inventory or player state offline, then boot the world and assert it.

Start with those two. Do not wire in the full client-automation layer (`mcpelauncher-agent`) until the container pair proves itself. It is a stepping stone, not the goal.

### 4. Editing ergonomics (install these)

These cut the manual JSON and Molang errors the current chain cannot catch:

| Tool | What it buys | Where |
|------|--------------|-------|
| **bridge.** | Bedrock add-on IDE: compiler, live preview, Molang checks, JSON errors before launch | Standalone app (v2.7.54) — install from its releases page |
| **Blockbench** | Already the dragon pipeline. Also promo renders and 3D typography | v5.2.1, GPL-3.0 |
| **Snowstorm** | Author the Parapet wind particles properly, not as raw commands | v3.2.1 |
| **Bedrock Editor** | In-game scriptable editor for manual map tweaks | Windows only, stable since 2024-12-03 |

**Caution:** the **Blockception VS Code Bedrock extension was archived 2025-09-28**. Do not build a workflow on it.

### 5. Distribution: post the clips

This is the real distributor, not the map. Follow `DISTRIBUTION.md` and `docs/LISTING.md`. Post the six clips in the listed order. Every download page and every clip carries the credit line from `docs/LISTING.md`. **Never** the Minecraft Marketplace.

## Hard constraints (never break)

- **Platform:** Minecraft **Bedrock**, `@minecraft/server` **2.0.0** and `@minecraft/server-ui` **2.0.0**. Do not bump the versions. Do not enable Beta APIs.
- **Free, fan-made only.** No money, no donation, no Marketplace hook, ever.
- **No official art, no book text, no series name.** The denylist in `docs/CANON.md` and `scripts/test_release.py` stays in force. The place name **Basgiath** is allowed in the title and function folder only.
- **No client-modification code.** No anticheat evasion, no hacked clients, no client mods. This boundary holds on every edition.
- **Original code.** No copy-paste from another add-on.
- **Original wording** for every entity id, pack string, and generated asset.

## NEVER

- Do not write outside `/Users/claudiobarone/Projects/dragon-rider-map`. Never touch `~/.pyenv`, `~/.local`, `~/.cemini`, or any home-directory dotfile.
- Do not change the pack UUIDs, pack ids, or the geometry id `geometry.dragon_rider`.
- Do not weaken a check to make it pass. Fix the check, not the result.
- Do not put player input into a command string. Use `player.sendMessage` — never `runCommand`.
- Do not print, write, or commit a key.
- **Do not commit or push** unless the operator asks.

## Verify

```
python3 scripts/build_map.py
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh
python3 scripts/test_release.py
python3 scripts/bench_static.py
```

`bench_bds.sh` cannot run on a Mac. It is verified on RunPod, not locally.

## Out of scope for this prompt

- **The Java port.** That is a separate prompt. Do not start it here. (`addon/behavior_pack/scripts/main.js` → NeoForge, the generator → a Java function emitter, and the dragon model are the three moving parts — and a port started today is easier than ever, because Mojang dropped obfuscation after 1.21.11, so **use official Mojang mappings, never Yarn**.) The open question that decides the dragon-model effort: **does the Java port ship publicly, or is it a capability experiment?**
- The fal MCP generative asset pipeline from `universal-modder`. It routes through a **paid third-party service**. Treat it as a lead, not a decision. Decide the budget first; do not wire it in by default. The free half is the loop, not the API: generate a texture or sound variant, show it in-game, keep or discard.
