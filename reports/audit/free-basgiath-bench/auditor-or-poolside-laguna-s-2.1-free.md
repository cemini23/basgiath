<!-- model=poolside/laguna-s-2.1:free channel=openrouter-free ts=20261004T1702Z -->
<!-- retry-after-empty-or-stub -->

### Verdict
FAIL — The static bench does not actually assert the Parapet contract against the shipped world; it only re-simulates the stage functions in memory, so deleting `parapet()` from `build_map.py` would still pass CI.

### Findings
| Severity | Finding | Evidence (file:line or quote) | Fix |
|----------|---------|----------------------------------|-----|
| Critical | `bench_static.py` never reads the Parapet from the shipped `.mcworld`; it replays `stage_*.mcfunction` text in memory. | `bench_static.py:stage_lines()` globs `addon/behavior_pack/functions/basgiath/stage_*.mcfunction` and `solid_blocks()` parses those lines; `assert_world()` only checks `level.dat` header and prints `leveldb files in the zip: 0`. | Have the bench extract and replay the actual function files from inside `dist/basgiath.mcworld`, or assert that the zip contains the expected stage files. |
| Critical | The "proof" mutations append to the in-memory command list, not to the shipped artifacts, so they only prove the checker logic, not the shipped world. | `bench_static.py:prove()` calls `expect_fail(lines + [...])` where `lines` come from `stage_lines()`; the real `dist/basgiath.mcworld` is untouched. | Run the mutation proofs against the extracted zip contents, not the source tree. |
| High | `assert_world()` explicitly notes it cannot count placed blocks and does not try. | `bench_static.py:assert_world()` comment: "Placed college blocks are not in this zip. Counting them here would pass after the Parapet was deleted." | Add a check that the zip contains the expected `stage_*.mcfunction` files with non-zero size, or parse them from the bundle. |
| Medium | `test_release.py` checks for `setblock ~45 ~32 ~20 air` and `setblock ~46 ~32 ~20 air` as text, but does not verify the Parapet blocks exist. | `test_release.py:check_map()` needle list includes the gap air commands but no positive assertion of `parapet()` output. | Add a positive assertion that the span blocks are present in the generated functions. |
| Low | `bench_bds.sh` is Linux-only and was not executed; CI does not run it. | `ci.yml` only runs `python3 scripts/bench_static.py`; `bench_bds.sh` exits 2 on non-Linux. | Either gate `bench_bds.sh` behind a Linux runner or remove it from the critical path. |

### Root cause
The static bench treats the stage function files as the source of truth and replays them in a Python dict, but it never inspects the actual `dist/basgiath.mcworld` bundle for those functions. Because `build_map.py` regenerates the stage files from `parapet()` on every run, and CI runs `build_map.py` before `bench_static.py`, the bench is effectively testing the generator's current output rather than the shipped artifact. Deleting `parapet()` from `build_map.py` would remove the span from the generated functions, but `bench_static.py` would still pass because it only checks that the (now span-less) functions are internally consistent — and the `prove()` mutations would still fail correctly because they mutate the same span-less list. The bench therefore cannot detect a deleted Parapet in the shipped world.

### Confidence
high — The code path is explicit: `stage_lines()` reads from the source tree, `solid_blocks()` parses those lines, and `assert_world()` only validates the `level.dat` header. No code path reads the college blocks from the `.mcworld` zip.

### Unique angle
Other models may focus on the `prove()` mutation tests and assume they validate the shipped world, but those proofs only mutate an in-memory copy of the source-tree functions. The real gap is that the bench never opens the `.mcworld` to confirm the stage functions inside the bundle match what the source tree generated — so a stale or span-less bundle would sail through CI.
