<!-- model=xiaomi/mimo-v2.5-pro channel=openrouter-free ts=20261005T0023Z -->

### Verdict
**PASS.** The entity-spawn fix is correct and idempotent; the checker is no longer tautological; no parser blind-spot hides a real defect at this commit; IP compliance is clean.

### Findings

| Severity | Finding | Evidence | Fix |
|----------|---------|----------|-----|
| info | `execute`-guarded far retry lines return `None` from `_box()`, so `is_far()` never sees their position. This is safe because (a) the retry files are checked independently in `assert_far_retry` against the unguarded stage pass, and (b) non-summon commands are idempotent and double-run is harmless. | `build_map.py` `_box()` does not match `execute`; `bench_static.py` `assert_far_retry` lines 140–152 read files from disk and compare exact strings. | None needed. Document the two-layer design so a future parser change doesn't assume `_box()` covers all positional lines. |
| info | `_box()` for `summon` reads the last three whitespace tokens as coordinates. A summon whose Y coordinate is followed by extra optional arguments (Bedrock allows optional `spawnEvent` and `nameTag` after coords) would misparse. | `build_map.py` line: `x = _rel(parts[-3]); z = _rel(parts[-1])`. All 39 summons in this tree use only the three-coordinate form, so no defect fires today. | None needed now. If a summon ever appends a fourth token, the parser will silently shift the box. |

### Root cause

No root-cause issue. Audit 1 fixed air drops, audit 2 fixed summon drops by adding `_box()` recognition for `summon`. At `e2acf93` the far retry correctly guards every summon with `execute unless entity @e[type=…,name="…"] run summon …`, the stage pass sends summons plain, and `bench_static.py`'s `assert_far_retry` compares the on-disk retry against independently computed expected form using `retry_form()`, which is not tautological—it would catch a missing guard or a dropped command.

### Confidence

**High.** The evidence is the source code of `build_map.py`, `bench_static.py`, and the gate scripts. The five gates all pass on this tree. The `_box()` parser covers the three command types actually emitted by the build pipeline (`setblock`, `fill`, `summon`). The `execute` guard is validated by a separate string comparison, not by `_box()`. IP compliance was checked against every `.mcfunction` file, `main.js`, and the pack manifests.

### Unique angle

The `execute`-guarded far retry lines are invisible to `_box()` (return `None`, so `is_far()` sees them as "not far"). A naive auditor would flag this as a checker hole. But `assert_far_retry` in `bench_static.py` bypasses `_box()` entirely—it reads the written retry files, recomputes the expected retry form from stage files using the same `retry_form()` + `is_far()` pipeline, and compares the two sets as strings. The guard is enforced by exact-match comparison, not by coordinate parsing. This two-layer design (parsing for generation, string equality for verification) is the real fix, and it is solid.
