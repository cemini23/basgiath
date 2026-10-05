# K282 — Basgiath: packaging and asset automation

**Date:** 2026-10-05 · **Batch:** K282 · **Home:** `Projects/dragon-rider-map/briefs/`
**Source:** `Project Stack Revenue Evaluation.docx` (20 rows) — OSINT K282

## Target

Basgiath. `Projects/dragon-rider-map/`.

## Summary

FILE. Two Basgiath-facing Extract rows. Neither is an install. **The packaging standard is the higher-value one** — it removes a real churn source. **No Minecraft Marketplace. Free fan distribution only.**

## Body

### 1. Package the add-on so import never fails (highest value)

The `xentropaff` Bedrock add-on guide scored `basgiath overlap 0.85` — the highest row in the batch. The failure it describes is exact:

> "Packaging mistakes or manifest UUID mismatches break Bedrock import dialogs, leading to immediate player churn."

A player who cannot import the pack never sees the world. This is the distribution analogue of the K281 test bench: it removes a manual, error-prone step that sits directly on the path to fan reach.

**The three rules to enforce in `scripts/package.sh`:**

1. **Behavior Pack and Resource Pack stay separate.** BP carries gameplay and `@minecraft/server` scripts; RP carries textures, models, audio. Keep their folders and manifests distinct.
2. **Manifest UUIDs are matched and unique.** Each pack's `manifest.json` needs its own `header.uuid` and `modules[].uuid`. Cross-pack dependencies are declared in `dependencies` with the *other* pack's header UUID and a version range. Duplicate or mismatched UUIDs are the number-one import failure.
3. **Ship one `.mcaddon`.** A single zip containing both packs, importable in one click on Windows, Android, iOS, and console. A loose folder or two separate packs costs imports.

**Also verify `min_engine_version`.** The guide targets current Bedrock; the batch flags 1.21+ as the check. A too-high minimum silently blocks older clients.

**First step:** add a `manifest.json` validator to `scripts/package.sh` — assert two packs, no duplicate UUIDs, every `dependencies` UUID resolves to a pack in the same `.mcaddon`. Fail the build if not. That is cheap and it protects the whole distribution path.

### 2. The `universal-modder` asset pipeline (Basgiath + CCC)

`rehan-remade/universal-modder` scored `basgiath overlap 0.75`. K281 already took the **layout** (one canonical `skills/` tree with symlinked entry points, a single `AGENTS.md`, a `knowledge/INDEX.md` field-notes base). This wave adds the **fal MCP asset pipeline**: generative textures, sound design, and promo-clip production driven from Claude Code.

**Decision (2026-10-05): do not adopt the pipeline.** Its asset generation routes through a **paid third-party service** (fal). We will not pay for it, so we do not use it. No paid API, no new spend line.

**Extract only the free parts.** The *shape* of asset iteration — make a texture or sound variant, show it in-game, keep or discard — costs nothing with Blockbench and the existing world.

### 3. What was rejected, and why

The batch's most instructive Pass is **`brainage04/FabricModdingConventions`**. It does a thing we want — **headless GameTest regression CI for Minecraft entities and block states** — but it is **Java Fabric**. Java Fabric cannot compile to the Bedrock runtime. **Goal match, stack mismatch.**

The Bedrock equivalent needs `@minecraft/server` scripting and Bedrock's own test path. Hold the *goal*; the repo does not transfer. This pairs with the K281 test bench: the bench proves the world loads and the pack is error-free; a Bedrock GameTest layer would prove the *behaviour* (dragon flight, spawn, entity sync) without a human.

### Boundary

Free, non-monetized fan project. **Never Minecraft Marketplace.** No official art, no book text, no series name in the title. A clear "fan-made" label on every listing and every generated clip. No client-modification code — the batch's hacked-client rows were Pass and nothing from them is recorded.

## Sources

- [Source: @osint-wiki/sources/eval-project-stack-revenue-2026-10-05.md]
- [Source: @osint-wiki/concepts/k282-level-editors-wave.md]
- [Source: @osint-wiki/concepts/k281-basgiath-wave.md]
