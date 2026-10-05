# Basgiath at a6ed964 — fifth audit, deep pass (readonly)

You are the strongest auditor on this project so far. **Target commit: `a6ed964`.**

**Mode:** `code-debug` · **Readonly** — a markdown report only. No edits. No tool calls.

---

## Output rules

- **Start your reply with the line `### Verdict`. Nothing before it.**
- **Under 1500 words.**
- Cite `file` plus a quoted line.
- `insufficient evidence` beats speculation.

---

## Why you are here

Four cheaper models have already audited this. One of them found the single biggest defect by reading one file nobody else opened: the world's `level.dat` configuration. That was not a strength difference. It was scope.

**Go where the others did not.** Do not re-report what is listed as known below.

---

## Known and confirmed — do NOT re-report these

1. `scripts/build_world.py` writes `"beta_apis": Byte(1)` and `"gametest": Byte(1)` into `level.dat`. Confirmed by the orchestrator. It contradicts `DESIGN.md` and `README.md`.
2. Nothing cross-validates the `KEEPERS` table in `main.js` against the lectern `setblock`s in the zones.
3. `runKeeperForm` has no error handling; `form.show` can reject.
4. The roll call can schedule two pending reads if a name is written twice inside the 60-tick beat.
5. `solid_blocks()` silently skips a positional command it does not parse.
6. Only the keeper path has an off-origin proof; the rest of the geometry is replayed at the origin.
7. Minor: `event.cancel` skipped on the no-anchor lectern path; `check_names()` scans only `addon/` and `scripts/`; `rememberOnWing` keys on `player.name`; no feedback when no anchor exists.

---

## Mission

**Find what four audits missed.** In priority order:

### 1. The whole world configuration, not just the experiments

One file, `scripts/build_world.py`, produced the largest finding of the project so far. Read **every field** it writes into `level.dat`, and the world's `world_behavior_packs.json`, `world_resource_packs.json`, and `levelname.txt`. Compare each against what `README.md`, `DESIGN.md`, and `docs/IP-RULES.md` claim.

The others read the experiments and stopped. Look at `baseGameVersion`, `NetworkVersion`, `LimitedWorldOriginX/Y/Z`, `spawnMobs`, `texturePacksRequired`, `hasBeenLoadedInCreative`, `ForceGameType`, `MultiplayerGame`, `commandblocksenabled`, `sendcommandfeedback`, and anything else there. Which of these contradicts a stated intent, or changes gameplay in a way the design does not want?

### 2. The seven beats, as a player experiences them

Walk the story order — Parapet, Formation, College, Gauntlet, Presentation, Threshing, Signet — through the code. Is each beat actually reachable and actually gated in the right order? Can a player skip one, get stuck, or arrive at the wrong one? Pay attention to what the world rules in `scripts/build_map.py`'s `finish()` and `build_text()` do to the player: adventure mode, night, a locked storm, `keepinventory`, `doimmediaterespawn`, and a spawn point they can never change.

### 3. The tick and live layer

`basgiath/live.mcfunction` is joined from `LIVE` in `build_map.py` plus `gauntlet.live_lines()` and `valley.live_lines()`. It runs every tick, forever, from a script interval. Is that correct and affordable? Does anything in it fight the world rules, or fire for a player who is not there?

### 4. Anything else the four missed

You have the whole pack. Use it.

---

## Context

A Minecraft Bedrock fan map. Python generates `.mcfunction` files; a behaviour pack holds a script. The world is flat.

Four audits found, in order: dropped air fills in the far retry; dropped `summon` commands (the command parser read only `setblock` and `fill`); one absolute-coordinate summon; and the beta API flag. Two of those shared one root cause — **the generator and its checkers share a source of truth, so a divergence is invisible to both.**

Measured: 32 stages, 1596 build commands, 39 summons, air volume 34,328 against an 80,000 gate, a lectern at both keeper spots. The official Bedrock dedicated server `1.26.52.3` loads the pack with `pack_error=none` and passes every block probe.

---

## Already ruled out

- Do not ask for a Bedrock client. Report what the code and commands prove.
- `tickingarea add circle` takes its radius in **chunks**. Do not raise it.
- The canon facts in `docs/CANON.md` were verified separately.

---

## Required output format

### Verdict
PASS | WARN | FAIL — one line why

### Findings
| Severity | Finding | Evidence (file:line or quote) | Fix |
|----------|---------|----------------------------------|-----|

### Root cause
One paragraph, or "insufficient evidence" plus what to inspect.

### Confidence
high | medium | low.

### Unique angle
The one thing you found that no other auditor would.

---

## Data pack

```
{pack_index}
```
