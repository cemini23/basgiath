# K283 — Basgiath: Bedrock add-on extracts (currency, UI, lore, migration)

**Date:** 2026-10-06 · **Batch:** K283 · **Home:** `Projects/dragon-rider-map/briefs/`, `../Game Dev wiki/briefs/`
**Source:** `GitHub Revenue Opportunity Evaluation.docx` (20 rows) — OSINT K283

## Target

Basgiath. `Projects/dragon-rider-map/`. Also Game Dev wiki.

## Summary

FILE. The Bedrock batch routes **13 of 20 rows to Basgiath**. Five clean Extract techniques: in-game currency, JSON UI easing, readable lore items, schema migration, HUD timer. **Free, non-monetized fan project. In-game roleplay tokens only. No Minecraft Marketplace. No official novel text.**

## Body

### 1. In-game roleplay currency — `Flower7C3/simple-money` (overlap 0.80)

A turnkey currency framework: multiple coin tiers, paper bills, crafting conversion recipes, and an **ATM block**, packaged as `.mcaddon`. MIT (stated). This gives the academy world a cadet trading loop — dorm supplies, dragon-flight gear, a trading post.

**Gate:** the currency must stay **100% in-game roleplay tokens**. No real-money transactions, no paid server perks, no Marketplace. That constraint is what makes this safe to use.

### 2. UI easing — `tfgh6/bedrock-ui-animations` (overlap 0.85, highest of the batch)

JSON UI easing curves, smooth progress-bar interpolation, transition keyframes. Use for the **dragon-flight speedometer, altitude display, and stamina bar**. This is the largest visual-quality jump for the least code. Note: the docx lists this repo twice (URL 13 and URL 20) — it is one repo.

### 3. Readable lore items — `Flower7C3/books-minecraft-bedrock-addon` (overlap 0.75)

Custom readable items and paginated content, beyond the vanilla book-and-quill limit. Use for academy archives, dragon codices, flight manuals.

**Gate:** all text must be **original fan-written**. No official novel excerpts, no copyrighted passages. Label everything fan-made.

### 4. Schema migration — `kongbai9288/mc-mod-migrator` (overlap 0.70)

Automated refactor of deprecated entity components and JSON UI tags across Mojang updates. The pack will face monthly breakage; the migration *pipeline* is the reusable part. **Verify it targets Bedrock schema** — the row's stack claims Java, and K282 already showed a Java tool that does not transfer.

### 5. HUD timer — `Flower7C3/just-clock` (overlap 0.60)

An on-screen clock via mcfunction hooks, no experimental flags. Use for timed cadet obstacle courses and curfew challenges.

### Rejected

- **`void-community/Void`** — a modern .NET-10 proxy for **Java-Edition** modded servers (real repo `caunt/Void`, MIT). Bedrock has no equivalent proxy here. **Goal match, stack mismatch**, same as K282's `FabricModdingConventions`. Do not wire.
- **Texture packs, launchers, backup scripts, CS16MC** — Context only.
- **`roma234567/AUTOCLICKER`** — Pass. Unattended click automation violates the manual-operator gate.

### Boundary

Free fan project. **Never Minecraft Marketplace.** No official art, no book text, no series name in the title. A clear "fan-made" label on every listing and clip. No client-modification code — those rows were Pass and nothing from them is recorded.

## Sources

- [Source: @osint-wiki/sources/eval-bedrock-ecosystem-2026-10-06.md]
- [Source: @osint-wiki/concepts/k283-eval-wave.md]
- [Source: @osint-wiki/entities/tools/simple-money-minecraft-bedrock-addon.md]
- [Source: @osint-wiki/entities/tools/bedrock-ui-animations.md]
- [Source: @osint-wiki/entities/tools/mc-mod-migrator.md]
