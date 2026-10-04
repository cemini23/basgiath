# Free audit — Basgiath static bench

**Mode:** code-debug · **Auditors:** Grok + claude-ds (deepseek-v4-flash) + free OR (nvidia/nemotron-3.5-lightning:free, inclusionai/ling-3.0-flash-sante:free, poolside/laguna-s-2.1:free)
**Pack:** `reports/audit/pack-free-basgiath-bench` · **Out:** `reports/audit/free-basgiath-bench`

`thinkingmachines/inkling-small:free` returned HTTP 403 and an empty report. That slot is a channel failure, not a product vote. `nvidia/nemotron-3-ultra-550b-a55b:free` returned HTTP 503. The script retried with `nvidia/nemotron-3.5-lightning:free`, and that report is the Nvidia vote.

| Slot | Channel | Model | Verdict |
|------|---------|-------|---------|
| 1 | grok | grok-cli | WARN |
| 2 | claude-ds | deepseek-v4-flash | WARN |
| 3 | openrouter-free | nvidia/nemotron-3.5-lightning:free | WARN |
| 4 | openrouter-free | inclusionai/ling-3.0-flash-sante:free | WARN |
| 5 | openrouter-free | poolside/laguna-s-2.1:free | FAIL |

## Consensus (≥2 auditors agree)

- The bench is not decoration for the span that the stage functions place. `assert_parapet` requires the deck blocks, the two-block gap, a one-block width, and no safety floor. A local run printed `proof ok` for a deleted span, a filled gap, and a floor at y=20.
- Deleting the Parapet from `scripts/build_world.py` does not fail a check. That file writes a flat world and the packs. It has no Parapet blocks. `assert_world` only checks the level name, the flat generator, and commands. The zip has no LevelDB.
- `scripts/bench_bds.sh` is not an automated check yet. CI does not run it. It was not executed.

## Unique (single auditor — still investigate)

- [deepseek-v4-flash] The server script's `execute if block 20 112 20` does not use y=32. The static bench uses deck y=32. The server script summons the anchor at `0 80 0`, so relative y=32 is absolute y=112. That offset is intentional. It is still unverified, because the server never started.
- [deepseek-v4-flash] Pressure plates are listed as non-solid. The current walk passes with that rule. The plates in the map sit at foot height on the towers, not as the span floor.
- [grok] Deleting `chasm()` still leaves a fatal fall, because empty space is air. The fall check fails when a solid appears above y=9.

## Conflicts (Glasswing — resolve before ship)

| Topic | Grok | claude-ds | lightning | ling | laguna | Resolution |
|-------|------|-----------|-----------|------|--------|------------|
| Does a deleted span fail the bench? | Yes, on the stage files | Yes, if `parapet()` is removed and the stages are rebuilt | Yes for the stage replay; no for `build_world.py` | No, if the old stage files stay on disk | No, CI would still pass | The stage replay fails when the span lines are absent. CI runs `build_map.py` first, and `assert_walk()` there exits before it writes a span-less map. Laguna's "CI would still pass" claim disagrees with that order and with `assert_parapet`. |
| Is the bench decoration? | No for the shipped stage functions | No, but it is a simulator | No for the functions; yes if you expected the zip to hold the college | No, it is an artifact check | Yes | It is not decoration for the function files. It is decoration for the claim "the `.mcworld` contains the Parapet." |

## Recommended fix order

1. Keep calling the static bench a check of the stage functions. Do not say it watches `build_world.py`.
2. Do not count `bench_bds.sh` as passed until a Linux log shows `SPAN_OK`, `GAP45_OK`, `GAP46_OK`, and `COLUMN_OK`.
3. Optional: make `expect_fail` require the checker message to name the span, the gap, or the floor.

## Verdict rollup

**Overall:** SHIP — the static bench should stay. It fails when the span blocks are removed from the stage functions. It does not fail when someone edits `build_world.py`, because the Parapet is not in that file. The server script is written and unrun.
