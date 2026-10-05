<!-- model=openai/gpt-5.6-luna-pro channel=openrouter-free ts=20261005T0240Z -->

### Verdict
WARN — the generated build is coherent, but the shipped world enables beta APIs and the keeper flow lacks disconnect/error handling; verification also does not exercise most geometry at a non-origin anchor.

### Findings
| Severity | Finding | Evidence (file:line or quote) | Fix |
|----------|---------|--------------------------------|-----|
| High | The world enables beta APIs despite the stated stable-API requirement. | `build_world.py`: `"experiments": { ... "beta_apis": Byte(1), ... }`; `manifest.json`: dependencies are `@minecraft/server` `2.0.0` and `@minecraft/server-ui` `2.0.0`. | Set `beta_apis` to `Byte(0)` or remove it, then rebuild and rerun the release/BDS checks. |
| Medium | A disconnect or invalid player during the naming form’s delayed roll call can cause an unhandled script error or silently lose the call. | `main.js`: `system.runTimeout(() => readRollCall(player), 60);` and `readRollCall` immediately calls `player.getDynamicProperty(...)`. There is no validity/disconnect guard or exception handling around the timeout. | Check that the player is still valid/online before reading, and wrap delayed callbacks and form handling in error handling. Decide explicitly whether a disconnected player should receive a catch-up roll call. |
| Medium | The static and BDS benches share an origin blind spot for nearly all generated geometry. They use origin-relative commands as absolute coordinates, and the BDS probe summons the anchor at `(0, 80, 0)`. A mistakenly absolute stage coordinate can therefore pass. | `bench_static.py`: `rel_coord()` converts `~N` to `N` and replays those values directly; `bench_bds.sh`: `summon armor_stand "build_anchor" 0 80 0`. Only the keeper harness moves the anchor off-origin. | Add a non-origin geometry replay/probe, or generate a second build with an anchor such as `(12,70,-5)` and verify representative blocks, entities, checkpoints, and live containment zones after adding the origin. |
| Low | The roll-call behavior is intentionally repeatable after a rename, but the implementation permits multiple pending delayed reads if the player submits several names quickly. The tag prevents duplicate messages for the same current state, but there is no timeout cancellation or generation check. | `main.js`: every scroll submission calls `player.removeTag(ROLLCALL_TAG)` followed by `system.runTimeout(..., 60)`. | Track a per-player naming generation or pending timeout and ignore stale callbacks. |

### Root cause (if debugging)
The remaining risk is inconsistent treatment of world-relative state: generation correctly wraps stage and live commands at the anchor, while most verification replays relative coordinates as though the anchor were zero. The keeper path explicitly resolves and floors the anchor, but the rest of the geometry has no equivalent non-origin proof. Separately, world packaging contradicts the stable API configuration by writing `beta_apis: 1`.

### Confidence
medium — the coordinate audit shows no additional definite relative/absolute mismatch in the supplied generator and zone artifacts. Confidence would become high after inspecting/running `scripts/validate.sh` and exercising the generated pack with a non-origin anchor plus a disconnect during the form timeout.

### Unique angle
The world-level `beta_apis` flag is still enabled in `build_world.py`; checking only manifest dependency versions can incorrectly report that beta APIs are off.
