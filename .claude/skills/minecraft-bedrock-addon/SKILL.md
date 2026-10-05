---
name: minecraft-bedrock-addon
description: >-
  Basgiath Bedrock add-on rules — pack manifests and UUID pairing, .mcaddon /
  .mcworld packaging, @minecraft/server script facts, the build+bench chain,
  and the fan-project IP boundary. Use when editing pack JSON, the script, the
  generators, the packaging, or the test bench in this repo.
---

# Minecraft Bedrock add-on — Basgiath

Read `docs/IP-RULES.md` first. It wins on any conflict.

## Packaging — the failure that kills distribution

A mismatched or duplicated manifest UUID breaks the Bedrock import dialog and the player never sees the world. Enforce, in `scripts/package.sh`:

1. **Two packs, separate.** `addon/behavior_pack` (gameplay + `@minecraft/server` scripts) and `addon/resource_pack` (textures, models, audio). Distinct folders, distinct manifests.
2. **Four unique UUIDs.** Two `header.uuid` and two `modules[].uuid`. No repeats across either pack.
3. **Dependencies resolve.** Each pack's `dependencies[].uuid` names the **other** pack's `header.uuid` plus a version range.
4. **One `.mcaddon`.** A single zip with both packs, one-click import on Windows, Android, iOS, console. Do not ship a loose folder.
5. **`min_engine_version` is not too high.** It silently blocks older clients. Target Bedrock 1.21.90.

## Script API — pinned facts

- `@minecraft/server` **2.0.0** and `@minecraft/server-ui` **2.0.0**. Backward-compatible within the 2.x line. **Do not bump.**
- **Do not enable Beta APIs.** Stable is enough; Beta breaks at any increment.
- No `setTimeout` / `setInterval`. Use `system.runTimeout` and `system.runInterval` (one-tick precision).
- `server-admin` / `server-net` are **Bedrock Dedicated Server only**. Do not design the free distribution around them.
- Player input **never** reaches `runCommand`. Use `player.sendMessage`. A name is not an injection.

## The bench chain

```
python3 scripts/build_map.py
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh
python3 scripts/test_release.py
python3 scripts/bench_static.py
```

`scripts/bench_bds.sh` boots the official Bedrock dedicated server and probes the built world. It **cannot run on a Mac** — run it on a RunPod x86_64 pod. It proves pack load and block placement. It cannot judge the model, the texture, or a form. A human on a real client is the only check for those.

## Coordinate contract

`+X` east, `+Y` up, `+Z` south. The anchor is an invisible armor stand named `build_anchor`; its feet are the origin. Generated commands are **anchor-relative**. Anything in `main.js` that compares a block position (e.g. a keeper lectern) must resolve the anchor first and add `Math.floor(anchor) + relative` — never compare a bare absolute number.

## Editing tools

- **bridge.** — Bedrock add-on IDE; catches JSON and Molang errors before launch.
- **Blockbench** — the dragon model and texture pipeline; also promo renders.
- **Snowstorm** — author the Parapet wind particles instead of raw commands.

**Do not** build a workflow on the Blockception VS Code Bedrock extension — it was archived 2025-09-28.

## Hard boundary

Free, fan-made. Never monetised, never on the Minecraft Marketplace. No official art, no book text, no series name. Place name **Basgiath** is allowed in the title and function folder only. Original wording for every id and string. **No client-modification code — ever.**
