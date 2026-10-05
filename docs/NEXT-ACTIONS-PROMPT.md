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

## Routing and audit — use these

**Route the work to free models first. Do not burn a premium session on bulk edits.**

This federation has a `/route` skill that sorts a task into **easy / mid / hard** and outsources it. Use it. The cheap chain is **OpenRouter free (chat) → OpenCode Zen free (tools) → claude-ds Flash (paid fallback)**.

- **Free OpenCode models for easy and mid coding work.** `opencode` is installed. Run the **OpenCode Zen free** sidecar with the prompt in a file (never `$` interpolation in argv):
  ```bash
  cd /Users/claudiobarone/Projects/dragon-rider-map
  opencode run --auto --dir "$PWD" --model free "$(cat /tmp/task.md)"
  ```
  `--model free` (or empty) = the **live strongest listed-free coding pick**; do not lock one id. `-f` / `--file` **attaches** files (pass the affected source files that way). The unified wrapper, which picks the lane and walks the fallback chain, is:
  ```bash
  route-task -Profile claudio "mid: <the task>"
  ```
- **Premium only for the plan and the audit.** For a hard task, write the plan in the premium session, then let Grok CLI / the cheap lanes implement. Hard-lane implement falls to **Flash, then OpenCode** when Grok usage is out.
- **Never send secrets or protected IP text to a free OpenRouter or OpenCode model.** They may log or train. Keep keys out of every free-lane prompt.

**Audit every large change set. This is required, not optional.**

If a change touches **many files**, or any of the high-risk surfaces — the world generator (`scripts/zones/*`, `build_map.py`), the dragon geometry (`build_dragon_model.py`), the script (`main.js`), the world writer (`build_world.py`), or the pack manifests — run an **independent audit** before you call it done. The auditor must not be the writer.

- **Default:** the `cursor-audit` / `super-audit` lane (V4.1 Flash).
- **For a high-risk or hard-to-reverse change, audit on the strongest available model.** Use the session premium model (Opus / Sonnet 5.5), **or** a model reached with the API keys in the OSINT `.env` (`OPENROUTER_API_KEY`, `DEEPSEEK_API_KEY` at `/Users/claudiobarone/Projects/OSINT WORKSPACE/.env`). A cheap audit on a change that reshapes the map is false economy.
- The audit checks the change against the task's **success criteria** and the constraints below — not style. Report findings, fix them, then re-run the gate chain.
- **Never** route a change that would touch secrets or `.env` through a free lane.

## Smoke test — run it on RunPod after any pack or world change

`scripts/bench_bds.sh` boots the **official Bedrock dedicated server** and asks it about the built world. It observes the pack; it does not change the add-on. It is **Linux-only** — on macOS it exits 2 with "needs the Linux Bedrock server". Run it on a clean Linux pod.

**When to run it:** any change to the pack manifests, the script (`main.js`), the world writer (`build_world.py`), the generators (`scripts/zones/*`, `build_map.py`), the dragon model (`build_dragon_model.py`), or `bench_bds.sh` itself. **A green `bench_static.py` is not a substitute** — it checks the shape of the code, not whether Bedrock accepts the packed add-on.

**How:** spin a clean x86_64 CPU container, then from the repo root:

- **Preferred: the `runpod` MCP.** It is configured in `~/.cursor/mcp.json` (Cursor / Grok Build) and it has also run from **Claude Code in this workspace** — use whichever is at hand.
- **Fallback: the RunPod REST API.** If no runpod MCP is present, drive the API directly with **`RUNPOD_API_KEY`** from the OSINT `.env` (`/Users/claudiobarone/Projects/OSINT WORKSPACE/.env`). Do not print the key.

```bash
bash scripts/package.sh
bash scripts/bench_bds.sh
```

`bench_bds.sh` installs its own tooling (`unzip`, `curl`, `python3-pil`, `zip`). Then read `result.txt` and **require**:

```
server_started=yes
pack_error=none
blocks_ok=true
BENCH_EXIT=0
```

- **`pack_error=none` is the line that matters** — the behavior pack loaded with no manifest, script, or command error.
- **`TICK_SPAN=false` is expected on a pod.** There is no player, so the tick-driven build falls back to calling every stage function directly.
- Expect log lines like `ERROR ... is out of range. / Execute subcommand unless block test failed.` A lectern probe outside the bench ticking area prints a warning then succeeds. **Do not read the warning as a failure.**

**Cost and cleanup.** One CPU pod is enough — about 90 seconds at ~$0.14/hr. **Terminate the pod when the run ends** and confirm the pod list is empty. Do not leave a pod running.

**Precedent — follow it, do not reinvent it.** This repo has run the pod bench before. `briefs/2026-10-05_smoke-green.md` records a full green run (commit `0152ae4`): the pod cloned `cemini23/basgiath` over HTTPS, ran `package.sh`, then the bench. `reports/audit/*-bench/` holds the bench prompts. Use the same flow.

**A green pod run is the proof the add-on still ships.** It is the one check CI cannot do.

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

These run locally. `bench_bds.sh` cannot run on a Mac — run it on a **RunPod pod** (see **Smoke test** above) whenever a change touches the pack, the script, the world writer, the generators, the dragon model, or the bench.

## Out of scope for this prompt

- **The Java port.** That is a separate prompt. Do not start it here. (`addon/behavior_pack/scripts/main.js` → NeoForge, the generator → a Java function emitter, and the dragon model are the three moving parts — and a port started today is easier than ever, because Mojang dropped obfuscation after 1.21.11, so **use official Mojang mappings, never Yarn**.) The open question that decides the dragon-model effort: **does the Java port ship publicly, or is it a capability experiment?**
- **The fal MCP generative asset pipeline from `universal-modder` — do not adopt it.** Operator decision (2026-10-05): **we will not pay for it, so we do not use it.** Its asset generation routes through a **paid third-party service** (fal). No paid API, no new spend line. **Extract only the free parts** — the skill-tree layout K281 already took, and the asset-iteration *loop*: make a texture or sound variant with free tools, show it in-game, keep or discard.
