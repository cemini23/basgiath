# Free audit — Basgiath zone integration

**Mode:** code-debug · **Pack:** `reports/audit/pack-free-basgiath-zones` · **Out:** `reports/audit/free-basgiath-zones`

**Auditors:** claude-ds (deepseek-flash) · nvidia/nemotron-3-ultra-550b-a55b:free · nvidia/nemotron-3.5-lightning:free

Grok is out of credits, so the orchestrator wrote this rollup from the three auditor reports. The auditors are independent. The rollup is not.

Channel failures, not product votes: `thinkingmachines/inkling-small:free` (HTTP 403), `google/gemma-4-26b-a4b-it:free` (HTTP 429). The Lightning slot ran as the Gemma fallback.

| Slot | Channel | Model | Verdict |
|------|---------|-------|---------|
| 1 | claude-ds | deepseek-flash | **FAIL** |
| 2 | openrouter-free | nemotron-3-ultra-550b | **FAIL** |
| 3 | openrouter-free | nemotron-3.5-lightning | PASS |

**Overall: FAIL.** Two of three auditors fail the change.

## The question

The far retry in `scripts/build_map.py` now drops every air fill:

```python
far = [line for line in far if not line.endswith(" air")]
```

Is that safe for a phone?

## Consensus (2 of 3 agree)

**The dropped far air is load-bearing, not decorative.** The far pass exists because pass 1 cannot place blocks in chunks the phone has not loaded. So for a far chunk, the retry is the *only* place those commands ever run. Dropping air there means the air never lands.

The dropped air includes:

- `fill ~49 ~ ~12 ~77 ~31 ~28 air` — the far half of the chasm.
- `fill ~79 ~ ~13 ~89 ~31 ~27 air` — the east tower interior.
- The valley floor fills.
- About 130 `setblock ~NN ~N ~20 air` lines — the staircase clearance.
- `fill ~101 ~ ~89 ~119 ~6 ~107 air` — a citadel interior.

**The failure mode is worst for hollow buildings.** Every zone that uses a solid-then-air shell places both the solid and the air in the far set. The retry re-places the solid but not the air. The result is a building with no inside.

**The comment is false.** It claims the load pass already places every air fill. It does not, for any box past 48 blocks.

## The dissent

The Lightning auditor says PASS, on the argument that the player never reaches those chunks during normal play. That argument assumes the first pass works, which is the exact thing the far pass exists to fix. The dissent does not survive the premise.

## Single-auditor findings worth action

| Source | Finding | Fix |
|--------|---------|-----|
| claude-ds | `bench_static.py` replays only `stage_*.mcfunction`. It never reads `far_*.mcfunction`. So the static bench cannot catch this class of bug — it stays green while the phone path breaks. | Replay the far files too |
| claude-ds | `main()` asserts the far set holds the east stairs and a lodestone, but never asserts that far air survived. | Add a far-air assertion |
| nemotron-ultra | Distinguish **redundant** air (clearing world space that is already empty) from **structural** air (hollowing a solid fill the retry re-places). Only structural air must be retried. | Use this rule in the fix |

## Conflict resolved

The two fails disagree on the chasm. claude-ds calls it load-bearing. nemotron-ultra calls it redundant.

The orchestrator tested it. Nothing else places a non-air block inside the chasm box. The world is flat, and the box sits above the surface. So the two chasm carves — 34,272 blocks — are a **no-op**. nemotron-ultra is right on that one item.

That matters, because it is also the budget fix.

## Recommended fix order

1. **Remove the redundant chasm carves** (`~15..77`, `z12..28`, `y0..31`). 34,272 air blocks, no visual change in a flat world.
2. **Restore the far air retry.** Delete the filter and the false comment.
3. New air volume: 84,376 − 34,272 = **50,104**, under the 80,000 gate. The retry stays whole.
4. **Make `bench_static.py` replay `far_*.mcfunction`** as well as `stage_*.mcfunction`, so the phone path is actually simulated.
5. **Add a generator assert** that the far set still holds its structural air.
6. Correct the comment on the filter.

Note on step 1: removing the carve also drops robustness for a **non-flat** world. The shipped world is flat. Record the choice.

## Verdict rollup

**Overall: FAIL.** The integration order and the `bonded` signal are correct and both fails confirm that. The far-air filter is not. Fix it before ship.
