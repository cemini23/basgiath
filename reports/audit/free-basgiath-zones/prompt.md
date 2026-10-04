# Basgiath zone integration — free audit (readonly)

You are one auditor in a **low-cost multi-model free audit**.

**Mode:** `code-debug` · **Readonly** — markdown report only; no edits; no secrets.

---

## Mission (single sharp question)

Decide this one question, and give a verdict:

**In `scripts/build_map.py`, the far retry now drops every air fill (`far = [line for line in far if not line.endswith(" air")]`). Is that safe for a phone, or does it leave far air unplaced?**

A secondary question, only if the first is answered: does the canon play order in `geometry()` match the zones' own stage ranges and the shared `bonded` signal?

---

## Context

The generator emits Bedrock functions. Two passes:

1. `build.mcfunction` runs `stage_01`..`stage_32` at the build anchor. Those stages hold **all** 1597 commands, near and far.
2. `fill_far.mcfunction` re-runs the far subset when the `college_b` and `college_d` ticking areas load, via `schedule on_area_loaded`.

The far pass exists because a phone at simulation distance 4 cannot place blocks in chunks that are not loaded. Pass 1 fails there. Pass 2 retries.

Numbers measured on the current tree:

- 32 stages, 1597 commands total.
- Air fill volume in the command list: **54,117 blocks**.
- Air commands in the far set: **218**, volume **30,259 blocks**.
- The gate at `scripts/test_release.py:186` fails when air volume exceeds **80,000**. It counts the stage files **and** the far files.

So keeping the far air would count **84,376** and fail the gate. Dropping it counts **54,117** and passes.

Far air that is now never retried includes:

- `fill ~49 ~ ~12 ~77 ~31 ~28 air` — 15,776 blocks. The far half of the chasm between the two towers.
- `fill ~79 ~ ~13 ~89 ~31 ~27 air` — 5,280 blocks. The east tower interior.
- `fill ~16 ~-1 ~94 ~48 ~-1 ~140 air` and `fill ~49 ~-1 ~94 ~70 ~-1 ~140 air` — the Threshing valley floor.
- Roughly 130 `setblock ~NN ~N ~20 air` lines — a diagonal staircase clearance from about x=91 to x=123.
- `fill ~101 ~ ~89 ~119 ~6 ~107 air` — 2,527 blocks. A citadel interior.

Phase 2 wired the zones. `geometry()` now calls parapet, quad, dorms, gauntlet, flight, valley, signet, then `paths()` and `finish()`. All gates pass.

---

## Already ruled out

- The zone modules are inside budget and were **not** edited in Phase 2. Their reports are in `reports/zones/`.
- `manifest.json` keeps `@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0. Beta APIs are off. That is not the question.
- No Bedrock client ran. Do not ask for one.

---

## Data pack files

Grok CLI may open these paths with Read tools. **HTTP auditors** (claude-ds / free OpenRouter) receive the same files **inlined** by `run_non_grok_legs.py` — they must not emit tool calls.

```
{pack_index}
```

---

## Required output format

### Verdict
PASS | WARN | FAIL — one line why

### Findings
| Severity | Finding | Evidence (file:line or quote) | Fix |
|----------|---------|----------------------------------|-----|

### Root cause (if debugging)
One paragraph — or "insufficient evidence" with what to inspect next

### Confidence
high | medium | low — and what would change your mind

### Unique angle
One thing you suspect other models might miss
