<!-- model=inclusionai/ling-3.0-flash-sante:free channel=openrouter-free ts=20261004T1702Z -->
<!-- finalize-from-reasoning -->

### Verdict: WARN — bench reads stale stage files, so a deleted Parapet in `build_map.py` can pass if `stage_*.mcfunction` aren't regenerated first.

### Findings

| # | Finding | Severity |
|---|---------|----------|
| 1 | `bench_static.py` reads `stage_*.mcfunction` but never runs `build_map.py`; stale outputs produce false negatives | High |
| 2 | Parapet is in `build_map.py`, not `build_world.py` — the question's premise targets the wrong file | Medium |
| 3 | `prove()` only mutates a copy of commands; it doesn't verify stage files match current `build_map.py` | Medium |
| 4 | CI regenerates stages via `test_release.py` before the bench, masking the local gap | Low |

### Root cause
The bench asserts against generated artifact files, not the build script itself. Deleting `parapet()` from `build_map.py` without regenerating `stage_*.mcfunction` leaves the old Parapet blocks on disk, so `assert_parapet` passes.

### Confidence
High — the code path `stage_lines()` → `assert_parapet` is purely read-only with no rebuild step.

### Unique angle
The bench is not decoration, but it's an artifact-level check, not a pipeline-level one. The real guard is CI ordering (`test_release.py` first); the bench alone cannot detect a deleted Parapet if stage files are stale.
