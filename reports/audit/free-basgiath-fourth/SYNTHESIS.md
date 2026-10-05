# Fourth audit — Basgiath at a6ed964

**Mode:** code-debug · **Pack:** `reports/audit/pack-free-basgiath-fourth` · **Out:** `reports/audit/free-basgiath-fourth`

**Target:** commit `a6ed964`, whole project.
**Auditors:** deepseek-flash (`claude-ds`) · `xiaomi/mimo-v2.6-pro` · `openai/gpt-5.6-luna-pro` · `x-ai/grok-4.20-multi-agent`

**Cost:** **$0.093** of the $1.00 budget. The remaining budget was not spent, because the gap was verification rather than another opinion.

| Slot | Model | Verdict |
|------|-------|---------|
| 1 | deepseek-flash | WARN |
| 2 | xiaomi/mimo-v2.6-pro | WARN |
| 3 | openai/gpt-5.6-luna-pro | WARN |
| 4 | x-ai/grok-4.20-multi-agent | PASS |

**Overall: WARN.** One confirmed High finding, and a recurring root cause now named three times.

## Confirmed High — the shipped world turns on beta APIs

`scripts/build_world.py` writes the world's `level.dat`:

```python
"experiments": {
    "experiments_ever_loaded": Byte(1),
    "beta_apis": Byte(1),
    "gametest": Byte(1),
},
```

The orchestrator verified this directly. It contradicts every other statement in the project:

- `DESIGN.md`: "The script uses stable `@minecraft/server` 2.0.0 ... Do not enable Beta APIs."
- `README.md`: "Those modules are stable. Do not enable Beta APIs. Do not bump the dependency versions."
- Every build brief's NEVER list.

The manifest is correct, which is why nothing caught it. **Checking dependency versions is not the same as checking the world's experiments.** The Bedrock bench loads the pack with `pack_error=none` either way, so a green smoke test cannot see this.

Fix: set `beta_apis` and `gametest` to `Byte(0)`, rebuild, and re-run the release checks and the BDS bench.

## The recurring root cause, now named three times

Each audit has found the same shape, one level up:

1. The far retry and the parser shared a filter, so air and then summons vanished.
2. The generator and the benches share `_box`, so a command class is invisible to both.
3. **The keeper table lives in `main.js` and the lectern lives in the zone, and no check proves they agree.** `bench_static.py` reads the table out of `main.js` and feeds it back to the harness. If the table drifted from `zone-quad.py` and `zone-valley.py`, every check would pass and the keeper would silently never open.

MiMo's phrasing is the one to keep: *"the third instance of 'generator and checker share one source of truth, so a divergence is invisible to both.'"*

## Other findings, ranked

| Severity | Finding | Source |
|----------|---------|--------|
| High | **`beta_apis` / `gametest` enabled in the world.** Verified. | gpt-5.6-luna |
| Medium | No check cross-validates `KEEPERS[].block` against the emitted lectern `setblock`s | mimo |
| Medium | `runKeeperForm` has no error handling. `form.show` can reject on a disconnect or a busy player, and the promise is discarded by `system.run(...)` | mimo |
| Medium | Roll call can schedule two pending reads if a player writes a name twice inside the 60-tick beat. The tag hides it, but the timeout is never cancelled | mimo, gpt-5.6-luna |
| Medium | Only the keeper path has an off-origin proof. The rest of the geometry is replayed at the origin | gpt-5.6-luna |
| Low | `solid_blocks()` silently skips any command it does not parse, so a future `clone` or `structure` would be invisible to the walk and parapet checks | mimo |
| Low | A lectern interact with no anchor returns before `event.cancel = true`, so the book UI opens | grok-4.20 |
| Low | `check_names()` scans only `addon/` and `scripts/`. A docs regression — book text pasted into `README.md` — ships undetected | grok-4.20 |
| Low | `buildOrigin()` returning `null` gives the player no feedback | mimo, deepseek |
| Low | `rememberOnWing` keys the roster on `player.name`, which is not guaranteed stable | mimo |
| Info | `bench_bds.sh` records `TICK_SPAN=false` but can still report `blocks_ok=true`, so the tick loop is never actually proven | mimo |

## One finding rejected

deepseek-flash rated the valley bond trigger High: it read `as @a[x=~38,y=~-2,z=~112,dx=12,dy=4,dz=12]` as a mismatch.

It is not. The selector runs under `execute as @e[type=armor_stand,name="build_anchor",c=1] at @s`, so `~` is the anchor. The dell is built at relative `x=16..70, z=94..140`, and the box resolves to relative `38..50, 112..124` — inside it. **Both are anchor-relative, so they agree.** The auditor compared a relative box against an absolute footprint.

mimo and grok both read it correctly. Rejected.

The useful part survives: nothing cross-validates that the live-line box actually matches the dell's relative coordinates. That is a real, smaller gap.

## Recommended fix order

1. **Turn off `beta_apis` and `gametest`**, rebuild, and re-run the release checks and the BDS bench.
2. Cross-validate the keeper table against the emitted lecterns.
3. Wrap `runKeeperForm` in error handling, and cancel a pending roll-call timeout on a new write.
4. Make `solid_blocks()` fail loudly on an unrecognised positional command rather than skipping it.
5. Add a non-origin replay for representative geometry, not just the keepers.
6. The remaining Lows: `event.cancel` on the no-anchor path, the docs name scan, `player.id` for the roster, and the no-feedback case.

## Verdict rollup

**Overall: WARN.** The origin class is genuinely closed — mimo traced every anchor-relative command and found no remaining mismatch, and grok agreed. What is not closed is the meta-problem: the checks keep sharing a source of truth with the thing they check.
