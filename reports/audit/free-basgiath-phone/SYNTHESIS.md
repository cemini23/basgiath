# Free audit — Basgiath phone build

**Mode:** code-debug · **Auditors:** Grok + claude-ds (deepseek-v4-flash) + free OR (nvidia/nemotron-3-ultra-550b-a55b:free, nvidia/nemotron-3.5-lightning:free)
**Pack:** `reports/audit/pack-free-basgiath-phone` · **Out:** `reports/audit/free-basgiath-phone`

Keys: DeepSeek from `OSINT WORKSPACE/.env` (same value as the routing env). OpenRouter is not in that file. The routing env at `~/.cemini/llm-routing.env` supplied it. No key text is in this report.

`google/gemma-4-26b-a4b-it:free` returned HTTP 429. `thinkingmachines/inkling-small:free` returned HTTP 403. Those are channel failures, not product votes. The second free vote is Nemotron Lightning, so both free votes are Nvidia.

| Slot | Channel | Model | Verdict |
|------|---------|-------|---------|
| 1 | grok | grok-4.7 | FAIL |
| 2 | claude-ds | deepseek-v4-flash | FAIL |
| 3 | openrouter-free | nvidia/nemotron-3-ultra-550b-a55b:free | FAIL |
| 4 | openrouter-free | nvidia/nemotron-3.5-lightning:free | FAIL |

## Consensus (≥2 auditors agree)

- The Parapet can appear from `/function basgiath/build`. The east stairs (x=91) and the plaza (x=96–168) are outside a phone's 4-chunk simulation distance while the player stands on the anchor. Those `setblock` calls fail. This matches the playtest: gate near x=78, no stairs, no plaza.
- The "Welcome, candidate" title is tied to a timer. A failed `setblock` does not stop the function, so the title can show when the plaza is still missing.
- Do not move block placement back onto `tick.json` or the script tick. That path already placed nothing on this phone.
- The command count is not the bug.

## Unique (single auditor — still investigate)

- [nemotron-lightning] `college_d` is centered near (120, 110). Its radius does not cover the stairs at z=20. `college_b` at (120, 40) does cover the stairs and the plaza. The load hook was waiting on the wrong area.
- [deepseek] `far_01.mcfunction` starts with `fill ~ ~-2 ~ ~170 ~-2 ~150`. That second pass repaves the whole ground, including the start path and the west tower floor.
- [grok] The far cutoff of 79 blocks is the best case. A player on the east edge of a chunk only loads about 64 blocks. The gate at x=78 is then outside the retry.

## Conflicts (Glasswing — resolve before ship)

| Topic | Grok | claude-ds | Nemotron Ultra | Nemotron Lightning | Resolution |
|-------|------|-----------|----------------|--------------------|------------|
| Scheduled far functions use the wrong origin | Wrappers `execute at` the armor stand, so tildes are anchor-relative | Says `/schedule` runs at world spawn, so the far pass is misplaced | Says `@p` in the welcome can be the wrong player | Does not claim the far tildes are wrong | The `execute as @e[name=build_anchor] at @s run function` lines do set the origin. Keep them. Also run the welcome `at` the stand so `@p` is the player. Do not delete the schedule. |
| Four radius-4 ticking areas are over the chunk cap | Each circle is at most 81 chunks. The cap is about 100 per area, and 10 areas. | Treats 4×81 as one 324-chunk area and says the adds fail | Not the main claim | Says the center is wrong, not the size | Keep radius 4. Hook `fill_far` to `college_b` and to `college_d`. |
| Smallest fix is to place far blocks inside the first `build` body and drop `/schedule` | The first body cannot edit unloaded chunks. That is the proven failure. | Drop schedule and place inline | Split near/far in the generator and welcome from `fill_far` | Retarget the ticking area | Keep the inline near pass. Place far blocks again when `college_b` loads, and again after the player has been moved onto the plaza. |

## Recommended fix order

1. Slice fills on the 48-block box so a far retry does not repave the start, and so the near piece of a wide fill can succeed.
2. Retry every command outside that 48-block box, including the gate.
3. Run `fill_far` when `college_b` loads (stairs and plaza) and when `college_d` loads (valley and dorms).
4. After 15 seconds, give the player slow falling, move them to the plaza, wait 4 seconds, place the far blocks, then send them home and show "Welcome, candidate".
5. Bump the behavior pack to `[0, 1, 6]` so the phone does not keep the old pack.

## Verdict rollup

**Overall:** REWORK — all four auditors fail the pre-fix phone build. The Parapet path is sound. The east college is not, until the far blocks are placed in chunks the phone is actually simulating.

## Applied after this rollup

The working tree now follows the fix order above. Pack version is `[0, 1, 6]`. `dist/basgiath.mcworld` is 32643 bytes. `test_release.py` and `bench_static.py` passed. The phone has not run this file yet.
