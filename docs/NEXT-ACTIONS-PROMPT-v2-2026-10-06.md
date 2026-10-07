# Basgiath — next actions prompt (v2, 2026-10-06)

**Paste this whole file into a fresh session in this repo** (`/Users/claudiobarone/Projects/dragon-rider-map`, GitHub `cemini23/basgiath`). It is written for a Claude Code or Grok Build session that can shell out.

This v2 replaces the 2026-10-05 prompt. The 2026-10-05 tasks 1 and 2 were started; this file reflects where the repo actually stands and adds a **bug fix that comes first**.

---

## Where the project stands (2026-10-06)

- **The build is green.** `scripts/bench_bds.sh` passed against `bedrock-server-1.26.52.3`: `pack_error=none`, the `.mcworld` loads, span / both gaps / column correct, both keeper lecterns present.
- **Task 1 (packaging) is done.** `scripts/validate_manifests.py` now exists. `scripts/package.sh`, `scripts/validate.sh`, and `scripts/test_release.py` were changed to call it.
- **Task 2 (GameTest) is partly built.** `tests/gametest/behavior_pack/`, `scripts/bench_gametest.sh`, `scripts/build_gametest_world.py`, and `scripts/build_gametest_structure.py` exist. The GameTest run **surfaced a real bug in the shipped map** (below). This is the most important finding since the last prompt.
- **Task 3 (bench: container + NBT) is not started.** `scripts/nbt_le.py` exists as the NBT foundation.
- **Uncommitted work — do not lose it:** modified `addon/behavior_pack/manifest.json`, `scripts/package.sh`, `scripts/test_release.py`, `scripts/validate.sh`; untracked `tests/`, `scripts/bench_gametest.sh`, `scripts/build_gametest_*.py`, `scripts/validate_manifests.py`.

## Read first

1. `docs/IP-RULES.md` — **non-negotiable. This file wins on any conflict.**
2. `README.md`, `DESIGN.md`
3. `DISTRIBUTION.md` and `docs/LISTING.md`
4. `BUILD_CHECKLIST.md`
5. `scripts/package.sh`, `scripts/validate.sh`, `scripts/test_release.py`, `scripts/bench_bds.sh`, `scripts/bench_gametest.sh`
6. `briefs/2026-10-06_gametest-handoff.md` — the task-2 spec
7. `briefs/2026-10-06_k283-basgiath-bedrock-extracts.md` — today's research (the polishes)

## Task order

Do these in order. Finish a whole numbered task before starting the next. If you run out of room, stop at a clean boundary and report exactly what you completed.

### 0. Fix the shipped-map function syntax bug (do this FIRST)

A pre-existing bug surfaced when the GameTest bench ran with content logging on. The shipped map's functions log syntax errors on the Bedrock dedicated server:

```
ladder [facing_direction=2]
lectern [facing_direction=...]
dirt_path
#-prefixed scoreboard names in basgiath/tick
```

**Why the old bench never saw it.** `scripts/bench_bds.sh` sets `content-log-console-output-enabled=false` (line 76). That suppresses content-log errors. `scripts/bench_gametest.sh` sets it `true` (line 88). The errors were always there; the standard bench was blind to them.

**Why it matters.** A syntax error in a `setblock` or `fill` command means **that block does not place**. Some stage blocks are silently missing from the shipped world. This is not cosmetic — the map is incomplete. Fix it before any clip or release.

**The emitters — fix HERE, then regenerate.** The `.mcfunction` files are generated, so editing them directly is lost on the next build.

| Broken form | Emitter (fix this) |
|-------------|--------------------|
| `"ladder [facing_direction=2]"` | `scripts/zones/dorms.py:222-223` |
| `f"lectern [facing_direction={facing}]"` | `scripts/zones/dorms.py:270` |
| `WALK_BLOCK = "dirt_path"` | `scripts/zones/flight.py:32` |
| `#now` / `#stage` / `#done` / `#pass` / `#twenty` / `#wind` / `#storm` scoreboard names | `scripts/build_map.py` — tick text (lines 210-222), ONCE/LIVE/build text (339-388), LIVE + FAR text (406-422, 601) |

**Candidate corrections — VERIFY against the content log; do not guess.**

- **Bedrock block states attach to the id with quoted keys and no space:** `minecraft:ladder["facing_direction"=2]`. The current unquoted, space-separated form (`ladder [facing_direction=2]`) is the likely syntax error for **both** ladder and lectern.
- **The lectern's state is `direction`, not `facing_direction`.** Use `lectern["direction"=N]`. Confirm the value range (0-3).
- **ladder:** confirm the state name and value range against this Bedrock version (`facing_direction`, likely 2-5).
- **`dirt_path`:** confirm the id the server accepts. The 1.21.90 target may want `minecraft:dirt_path`, or the older `grass_path`. If the log says *unknown block*, switch to the accepted id. The zone note in `reports/zones/z5-flight.md` flagged this as unconfirmed.
- **scoreboard `#`-names:** if the log rejects `#`, rename to a valid token (for example `basgiath_now`) **consistently** across `build_map.py` and every consumer. Check `scripts/test_release.py` and `scripts/bench_static.py` first — they read these names.

**Method — follow it in this order:**

1. **See the real errors.** Run the gametest bench on a pod with content logging on (line 88 is already `true`). Capture the content-log lines. Each error names the exact command and reason. Fix per the log, not per this list.
2. **Fix the emitter(s).** Then regenerate: `python3 scripts/build_map.py`. Confirm the `.mcfunction` now carry the corrected syntax.
3. **Re-run the local gate chain** (see Verify).
4. **Re-run the pod bench with content logging ON, and require ZERO content-log errors** — not just `pack_error=none`.
5. **Close the blind spot.** Make the standard bench see content errors too: set `content-log-console-output-enabled=true` in `scripts/bench_bds.sh` (and parse for content errors). This is fixing the check, not the result. Do not leave the check off.

**This touches high-risk surfaces** (`scripts/zones/*`, `build_map.py`). Run the **required independent audit** (see *Routing and audit*). The auditor must not be the writer.

**Success:** the shipped functions produce no content-log errors on the pod, and every stage/far block places.

### 1. Finish task 2 — the GameTest behaviour layer

Use the spec in `briefs/2026-10-06_gametest-handoff.md`. Summary of the success criteria:

- A dev test behavior pack at `tests/gametest/behavior_pack/` — **not** under `addon/`, **not** in `dist/`.
- Exactly one GameTest, `basgiath:dragon_rides`: summon `dragon_rider:dragon`, assert it exists, is rideable (`minecraft:rideable`), and is flyable (`minecraft:input_air_controlled`), then succeed. No other tests.
- `scripts/bench_gametest.sh` boots the official Linux BDS against `dist/gametest.mcworld`, runs `gametest run basgiath:dragon_rides` on the console, writes `gametest_ok=true|false`. Exit 2 on macOS.
- **Do not enable Beta APIs in the shipped packs.** The test world is the only place `beta_apis`/`gametest` experiments are allowed.
- The exact GameTest pass string is unknown. Dump the last 60 gametest lines on the first pod run, then tighten the parser.

**One honest test beats four that pass trivially.** Finish this before adding more.

### 2. Task 3 — extend the bench: the container + NBT pair (on RunPod)

There is **no room on the local machine for more programs** (operator note, 2026-10-06). This task runs on a **RunPod server**. Plan for that: the pod is the target environment, and the local chain must stay green.

Add the pair that removes most manual clicking:

- **`itzg/docker-minecraft-server`** — headless container lifecycle for world-gen and pack-load validation.
- **Bedrock LevelDB NBT reader/writer** — `scripts/nbt_le.py` already exists. Extend it to set an inventory or player state **offline**, then boot the world and assert the state.

Start with those two. **Do not** wire the full client-automation layer (`mcpelauncher-agent`) until the container pair proves itself. It is a stepping stone, not the goal.

Document the exact pod setup and the run steps in `briefs/`, so the next session reuses it.

### 3. Polish, then wire today's research (before any clip)

**Do not take the clips yet.** Take them only after: the bug is fixed (task 0), the GameTest passes (task 1), the bench is green (task 2), and the polishes below are in.

Work these in order. Each is an **Extract technique from the K283 eval** — re-implement an original version. **No copy-paste; no vendored tree.** Full detail in `briefs/2026-10-06_k283-basgiath-bedrock-extracts.md`.

1. **JSON UI easing (`tfgh6/bedrock-ui-animations`, overlap 0.85 — highest of the batch).** Easing curves and smooth progress-bar interpolation for the **dragon-flight speedometer, altitude display, and stamina bar**. Largest visual jump for the least code. This is the top polish.
2. **In-game roleplay currency (`Flower7C3/simple-money`, 0.80).** Coin tiers, paper bills, crafting conversion, an ATM block → a cadet trading loop (dorm supplies, flight gear, a trading post). **Gate: in-game roleplay tokens only. No real money, no paid perks, no Marketplace.**
3. **Readable lore items (`Flower7C3/books-minecraft-bedrock-addon`, 0.75).** Custom readable items for academy archives, dragon codices, flight manuals. **Gate: all text original fan-written. No official novel text.**
4. **HUD timer (`Flower7C3/just-clock`, 0.60).** On-screen clock via mcfunction, no experimental flags — for timed cadet courses and curfew challenges.
5. **Schema migration (`kongbai9288/mc-mod-migrator`, 0.70).** The migration *pipeline* for Mojang updates — a maintenance tool, not a gameplay feature. **Verify it targets Bedrock schema** (the row's stack claims Java).

**Optional bench enhancement (from today's Image-gen ingest):** the **voxel-consistency metric** in `briefs/2026-10-06_logo-voxel-consistency-metric.md`. It turns "does the structure still look right as the camera moves?" into a number, which is what an unattended release check needs. Prototype on a known-good flythrough first. Low priority — after the five polishes.

### 4. Distribution: post the clips (LAST)

This is the real distributor, not the map. Follow `DISTRIBUTION.md` and `docs/LISTING.md`. Post the six clips in the listed order. Every download page and every clip carries the credit line from `docs/LISTING.md`. **Never** the Minecraft Marketplace.

## Routing and audit — use these

**Route the work to free models first. Do not burn a premium session on bulk edits.**

The federation `/route` skill sorts a task into easy / mid / hard and outsources it. The cheap chain is **OpenRouter free (chat) → OpenCode Zen free (tools) → claude-ds Flash (paid fallback)**.

- **Free OpenCode models for easy and mid coding work.** `opencode` is installed. Run the **OpenCode Zen free** sidecar with the prompt in a file (never `$` interpolation in argv):

  ```bash
  cd /Users/claudiobarone/Projects/dragon-rider-map
  opencode run --auto --dir "$PWD" --model free "$(cat /tmp/task.md)"
  ```

  `--model free` (or empty) = the live strongest listed-free coding pick; do not lock one id. `-f` / `--file` **attaches** files. The unified wrapper is:

  ```bash
  route-task -Profile claudio "mid: <the task>"
  ```

- **Premium only for the plan and the audit.** For a hard task, write the plan in the premium session, then let Grok CLI / the cheap lanes implement.
- **Never send secrets or protected IP text to a free OpenRouter or OpenCode model.**

**Audit every large change set. This is required, not optional.** The task-0 bug fix touches `scripts/zones/*` and `build_map.py` — high-risk surfaces. Run an **independent audit** before you call it done. The auditor must not be the writer.

## Smoke test — run it on RunPod after any pack or world change

`scripts/bench_bds.sh` boots the official Bedrock dedicated server and observes the pack. It does not change the add-on. It is **Linux-only** — on macOS it exits 2. Run it on a clean Linux pod.

**When:** any change to the pack manifests, `main.js`, `build_world.py`, `scripts/zones/*`, `build_map.py`, `build_dragon_model.py`, or `bench_bds.sh`. A green `bench_static.py` is not a substitute.

**How:** spin a clean x86_64 CPU container, then from the repo root:

```bash
bash scripts/package.sh
bash scripts/bench_bds.sh
```

Read `result.txt` and require:

```
server_started=yes
pack_error=none
blocks_ok=true
BENCH_EXIT=0
```

**After task 0, also require zero content-log errors.** Because task 0 flips `content-log-console-output-enabled` to `true`, the bench now sees them. `TICK_SPAN=false` is expected on a pod (no player).

**Cost and cleanup.** One CPU pod is enough — about 90 seconds at ~$0.14/hr. Use the `runpod` MCP if present; else the RunPod REST API with `RUNPOD_API_KEY` from `/Users/claudiobarone/Projects/OSINT WORKSPACE/.env` (do not print the key). **Terminate the pod when the run ends** and confirm the pod list is empty.

**Precedent — follow it.** `briefs/2026-10-05_smoke-green.md` records a full green run (commit `0152ae4`). `reports/audit/*-bench/` holds the bench prompts. Use the same flow.

## Hard constraints (never break)

- **Platform:** Minecraft **Bedrock**, `@minecraft/server` **2.0.0** and `@minecraft/server-ui` **2.0.0**. Do not bump the versions. Do not enable Beta APIs in shipped packs.
- **Free, fan-made only.** No money, no donation, no Marketplace hook, ever.
- **No official art, no book text, no series name.** The denylist in `docs/CANON.md` and `scripts/test_release.py` stays in force. The place name **Basgiath** is allowed in the title and function folder only.
- **No client-modification code.** No anticheat evasion, no hacked clients, no client mods.
- **Original code.** No copy-paste from another add-on. Re-implement the K283 techniques originally.
- **Original wording** for every entity id, pack string, and generated asset.

## NEVER

- Do not write outside `/Users/claudiobarone/Projects/dragon-rider-map`. Never touch `~/.pyenv`, `~/.local`, `~/.cemini`, or any home-directory dotfile.
- Do not change the pack UUIDs, pack ids, or the geometry id `geometry.dragon_rider`.
- Do not weaken a check to make it pass. Fix the check, not the result. (This is why task 0 must turn content logging **on**, not leave it off.)
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

These run locally. `bench_bds.sh` and `bench_gametest.sh` cannot run on a Mac — run them on a **RunPod pod** whenever a change touches the pack, the script, the world writer, the generators, the dragon model, or the bench.

## Out of scope for this prompt

- **The Java port.** It has its own prompt: `docs/JAVA-PORT-PROMPT.md` (research in `briefs/2026-10-05_java-port-and-tooling.md`). Do not start it here. Run it **after** this prompt, as a parallel track. **Decided 2026-10-06: the port ships publicly, and it lives in this same repo, in a `java/` subfolder — not a new repo** — so the shared generator stays in one place. See that file for the two-stage audit plan.
- **The fal MCP generative asset pipeline from `universal-modder` — do not adopt it.** Operator decision (2026-10-05): we will not pay for it, so we do not use it. **Extract only the free parts** — the skill-tree layout and the free asset-iteration loop (make a variant with free tools, show it in-game, keep or discard).
