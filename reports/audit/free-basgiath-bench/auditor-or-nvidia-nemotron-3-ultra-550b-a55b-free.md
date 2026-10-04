<!-- model=nvidia/nemotron-3.5-lightning:free channel=openrouter-free ts=20261004T1659Z -->
<!-- fallback-from-nvidia/nemotron-3-ultra-550b-a55b:free -->

### Verdict
WARN — the static bench does **not** fail when the Parapet is removed from `scripts/build_world.py`; it only validates the stage functions and the world header, which does not include the placed college blocks.

### Findings
| Severity | Finding | Evidence (file:line or quote) | Fix |
|----------|---------|--------------------------------|-----|
| Medium | The `assert_world` routine in `bench_static.py` explicitly states “Placed college blocks are not in this zip. Counting them here would pass after the Parapet was deleted.” The script never extracts or checks the Parapet blocks from the actual `mcworld`; it only replays `setblock`/`fill` from the stage functions. | `bench_static.py` `assert_world` comment and print “world header ok; leveldb files in the zip: 0” | Add a post‑build step that loads the generated `mcworld`, extracts the Parapet block positions, and runs the same `assert_parapet` logic, or run `build_world.py` then `build_map.py` before the check. |
| Medium | The bench’s `prove` mutation tests (deleted span, filled gap, safety floor) correctly reject those mutations **in the stage‑function replay**, but they do not exercise the released world zip. A deletion in `scripts/build_world.py` would leave the stage functions untouched, so the bench would still report “static bench ok”. | `bench_static.py` `prove` → `expect_fail` output “proof ok: the Parapet blocks were deleted” etc., followed by “static bench ok: 61 Parapet blocks…” | Ensure the CI pipeline runs the bench after `build_world.py` + `build_map.py` so the world state reflects the stage functions. |

### Root cause (if debugging)
The static bench was designed to validate the *generated* stage functions, not the *released* `mcworld`. Its `assert_world` routine only inspects the flat‑world header and deliberately skips checking the Parapet blocks that are placed later by `build_map.py`. Consequently, removing the Parapet from `scripts/build_world.py` has no effect on the bench’s outcome; the script still passes because the stage functions (which the bench actually replays) remain unchanged. The bench therefore functions as a contract check on the build‑script pipeline rather than a verification of the final distributed world.

### Confidence
high — the code comment in `assert_world` explicitly acknowledges that counting the placed blocks would “pass after the Parapet was deleted,” making the gap intentional and unambiguous.

### Unique angle
Other models may overlook the `assert_world` comment and assume the bench checks the final `.mcworld`; the explicit statement that the zip does not contain the college blocks and that the check would still pass after Parapet removal is the key insight that reveals the bench’s limited scope.
