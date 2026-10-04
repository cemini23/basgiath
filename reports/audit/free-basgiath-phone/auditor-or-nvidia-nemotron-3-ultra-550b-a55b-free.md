<!-- model=nvidia/nemotron-3-ultra-550b-a55b:free channel=openrouter-free ts=20261004T1946Z -->

### Verdict
FAIL — The Parapet places (near), but east stairs and plaza do not place before "Welcome, candidate". Far blocks run in the first pass and fail silently; the welcome title is gated by a 300-tick delay that chat pauses, not by far-chunk readiness.

### Findings
| Severity | Finding | Evidence | Fix |
|----------|---------|----------|-----|
| CRITICAL | Stage functions contain far commands that fail in first pass | `build_map.py:288` writes ALL commands to `stage_XX`; `build.mcfunction:38-57` runs all 20 stages inline. Far blocks (east stairs x≥91, plaza x≥96) exceed phone sim distance (79 blocks). | In `build_map.py`, split `commands` into `near` and `far` before `write_named_stages("stage", near)`. Regenerate pack. |
| CRITICAL | `fill_far` has no welcome/teleport; welcome only in `raise` at 300 ticks | `fill_far.mcfunction` only calls `far_01`–`far_11`. `raise.mcfunction:14-19` shows welcome after 300 ticks unconditionally. Chat pauses ticks → welcome delayed arbitrarily. | In `fill_far.mcfunction`, append the welcome/teleport lines from `raise.mcfunction` (with `#done` guard). In `raise.mcfunction`, add `execute unless score #far_done map_state matches 1 run ...` and set `#far_done` in `fill_far`. |
| HIGH | Welcome title targets `@p` at world spawn, not anchor | `raise.mcfunction:15-16` uses `titleraw @p title` inside a `schedule delay` (runs at world spawn). Player at anchor may not be nearest to spawn. | Change to `execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run titleraw @p title ...` (same pattern as teleport line 19). |
| HIGH | `on_area_loaded` may not fire if area loads before schedule registers | `build.mcfunction:35` adds ticking areas, line 36 schedules `on_area_loaded`. Bedrock may load chunks before schedule is processed. | Keep 300-tick `raise` as fallback, but gate it behind `#far_done` (see above). |
| MEDIUM | First-pass far commands waste tick budget and log spam | 984 commands include far `setblock`/`fill` that error "Cannot place block in unloaded chunk". | Fix #1 (split near/far) eliminates this. |
| LOW | `tick.json` empty but `main.js` runs `basgiath/tick` every tick | `tick.json:2` empty; `main.js:87-91` runs interval. `#stage=0` makes tick run `live` only — harmless but confusing. | Document or remove `tick.json`; keep `main.js` interval for wind/checkpoints. |

### Root cause
The generator (`build_map.py`) writes every command into the 20 `stage_XX` functions, including far blocks (x>79 or z>79). The first `build` pass runs all stages at once while the player stands on the anchor; far `setblock`/`fill` silently fail. The retry path (`fill_far` on `college_d` load, `raise` at 300t) re-runs far commands but the welcome title is bound to the 300-tick timer, not to successful far placement. Chat pauses ticks, so the welcome can appear long before or after far chunks load. The title also targets `@p` at world spawn, not the player at the anchor.

### Confidence
high — The geometry, sim distance, and command flow are all in the inlined files. The fix is mechanical: split near/far at generation time, make `fill_far` the primary welcome path, gate `raise` with a scoreboard flag.

### Unique angle
Other models may focus on ticking-area radius or `schedule` syntax. The real blocker is that the **generator does not partition commands by distance** — it duplicates far commands into both `stage_XX` (run immediately, fail) and `far_XX` (run later, succeed). The phone only proves the inline `build` body; everything scheduled is best-effort. The smallest fix is a one-line change in `build_map.py` to filter `is_far` before writing `stage_XX`, then append the welcome logic to `fill_far.mcfunction`.
