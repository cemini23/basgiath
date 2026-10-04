### Verdict
WARN — the static bench fails if the span blocks are gone, and it does not fail if the Parapet is deleted from `build_world.py`, because that file never contains the Parapet.

### Findings
| Severity | Finding | Evidence (file:line or quote) | Fix |
|----------|---------|----------------------------------|-----|
| warn | Deleting the Parapet from `scripts/build_world.py` does not fail any automated check. That file writes a flat `level.dat` and copies the packs. It has no span blocks to delete. | `build_world.py` `_level_root()` and `main()` write `level.dat`, `levelname.txt`, pack JSON, and the two pack trees. `bench_static.py` `assert_world()` only checks `LevelName`, `Generator`, and `commandsEnabled`. | Keep the geometry check on the stage functions. Do not describe the world zip as a Parapet check. |
| info | The static bench is not decoration for the span that the release actually ships. Removing the deck blocks, filling the gap, or adding a floor at y=20 makes `assert_parapet` or `assert_walk` raise. A local run printed `proof ok` for all three mutations, then `static bench ok: 61 Parapet blocks`. | `bench_static.py` `assert_parapet()` requires a solid at y=32, z=20 for x=15..77 except 45 and 46, air in the gap, one-block width from x=19..77, and no solid above y=9 under the span. `prove()` appends those three mutations to a copy of the stage lines. | None for this claim. |
| warn | `scripts/bench_bds.sh` does not protect a release. CI does not run it. It was not executed. A green static bench does not mean a Bedrock server loaded the pack or placed the span. | `.github/workflows/ci.yml` runs `python3 scripts/bench_static.py` only. The server script exits 2 on a non-Linux host. | Leave it out of the "automated" list until a Linux run shows `SPAN_OK`, `GAP45_OK`, `GAP46_OK`, and `COLUMN_OK` in the server log. |
| info | Deleting `chasm()` still leaves a fatal fall, so the bench stays green. The fall check fails when a solid appears above y=9, which is a safety floor, not the absence of the air fill. | `bench_static.py` `MAX_SAFE_FLOOR_Y = 9`. Unplaced cells are treated as air. | State that in the bench output if a reader expects the chasm fill itself to be required. |
| info | `expect_fail` treats every `SystemExit` as proof the checker worked. A crash inside `solid_blocks` on a bad mutation would also count as proof. The three mutations used today are valid `fill` and `setblock` lines, so this did not happen on the run above. | `bench_static.py` `expect_fail()` | Catch only the checker messages, or require the error text to name the span, the gap, or the floor. |

### Root cause (if debugging)
The Parapet is a list of relative `setblock` commands emitted by `build_map.py` `parapet()` into `stage_*.mcfunction`. `build_world.py` never sees those coordinates. A check that opens the `.mcworld` and counts blocks will stay green after the span is removed from the generator, because the zip has no LevelDB (`leveldb files in the zip: 0`). The new bench avoids that hole by replaying the stage commands. It does not close the differently worded hole in the mission question, because there is nothing named Parapet in `build_world.py`.

### Confidence
high — the three proof lines were printed by `python3 scripts/bench_static.py` in this session, and `build_world.py` has no span coordinates. A Linux run of `bench_bds.sh` that prints the four `*_OK` markers would raise confidence in the server script. It would not change the `build_world.py` answer.

### Unique angle
CI regenerates the stages with `build_map.py` before the bench runs. `build_map.py` `assert_walk()` already exits if the start cannot reach the span. The new bench still adds checks that `assert_walk()` does not do: the two-block gap, the one-block width, and a floor that would make the fall survivable. Those are the checks that make the bench more than a second copy of the walk.
