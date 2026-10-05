# Fifth audit — deep pass at a6ed964

**Mode:** code-debug · **Pack:** `reports/audit/pack-free-basgiath-fifth` · **Out:** `reports/audit/free-basgiath-fifth`

**Auditor:** `anthropic/claude-opus-5.5` (1M context), plus a free deepseek-flash leg. **Cost: $0.247.**

The Opus reply carries a harness flag `degraded-empty-or-tool-stub`. That flag only means it did not open with the required heading — it thought out loud and was cut off at the end. The reasoning is intact and the findings are real. Two of the biggest were verified by the orchestrator.

## Verdict: FAIL

Not for correctness of the build — for **playability**. The world can be bypassed, and it ships in the wrong game mode.

## Confirmed by the orchestrator

### 1. The world ships as Creative and never forces Adventure

```
scripts/build_world.py:52   "GameType": 1,             # creative
scripts/build_world.py:84   "ForceGameType": Byte(0),  # do not force on join
scripts/build_map.py:349    "gamemode adventure @a",   # only players present now
```

The build switches everyone **currently connected** to adventure. `ForceGameType` is off, so a friend who joins afterwards — by LAN, by invite, or on a Realm — spawns in **Creative**. They can fly, break the college, and skip the Parapet by air.

### 2. The whole story is walkable around

Tested by replaying the emitted commands into a block map and walking from `START`:

```
reach the SPAN         : True
reach the QUAD (court) : True
reach the VALLEY       : True
walk to VALLEY staying at ground level (y<=1): True
walk to QUAD   staying at ground level (y<=1): True
```

The chasm has a **stone floor at ground level** (`parapet.py` `_chasm` fills `y=-1` with stone). It is a walled corridor, not a drop. So a player walks under the span instead of across it.

Worse: the valley is reachable the same way, and the bond fires **purely on position**. Nothing checks that the Parapet was crossed, that the College was attended, that the Gauntlet was run, or that Presentation happened. **A player can skip six of the seven beats in about a minute.**

This is the map's signature moment — the clip the project is built around — and it is optional.

## Reported by Opus, not yet independently verified

| Severity | Finding |
|----------|---------|
| High | The Gauntlet score is tracked on a **single global fake player**, no timer starts or stops it, and nothing reads it. The "timekeeper" armor stand does nothing. `rope_told` is added and never cleared, so the rope penalty message fires **once, ever** |
| High | The Gauntlet summit may have **no way down** except a 26-block fall, which exceeds the 23-block kill line |
| Medium | The bond box overlaps the trial pad, so the "flew" flag can be satisfied by proximity. The flight trial is effectively decorative |
| Medium | The valley's live line says **"say only the colour"**, while the Roll-keeper form asks for the **full name**, and `docs/CANON.md` says the roll-keeper receives the full name. The keeper build contradicted the existing text |
| Medium | Lightning can ignite the valley's oak trees and planks — `doFireTick` is on |
| Low | Stale welcome text: "touch the stone in the Quad" (the lodestone moved to the valley) and "the dragon waits on the gold pad" (the pad is moss now) |
| Low | The bond already summons a dragon; `summon_dragon` spawns a second one |
| Low | `NetworkVersion: 827` against `lastOpenedWithVersion: [1, 21, 90, …]` — worth checking whether a 1.21.90 client rejects it |

## What this proves about method

Four cheaper models produced a solid but shallow audit. The strong model, pointed at **one file** and told where the others had already been, produced the two biggest findings in the project's history.

The lesson is not "spend more". It is: **scope the strong model away from what you already know, and aim it at the seam.** The cheapest model in round 4 found `beta_apis` for the same reason — nobody else had opened that file.

## Cumulative spend

| Round | Cost |
|-------|------|
| 4 | $0.093 |
| 5 | $0.247 |
| **Total** | **$0.340 of $1.00** |
