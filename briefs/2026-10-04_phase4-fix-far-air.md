# Phase 4 — fix the far-air regression

## WorkDir

`/Users/claudiobarone/Projects/dragon-rider-map`

## Context

A free audit failed the Phase 2 integration. Two of three auditors agree on one defect.

`scripts/build_map.py` drops every air fill from the far retry:

```python
far = [line for line in far if not line.endswith(" air")]
```

The far pass exists because pass 1 cannot place blocks in chunks a phone has not loaded. So for a far chunk, the retry is the only place those commands ever run. Dropping air there means the air never lands. Buildings hollowed by a solid-then-air pair keep their solid shell and lose their inside.

The filter was added to keep the air-volume gate under 80,000. Keeping the far air counts 84,376 and fails; dropping it counts 54,117 and passes. That is the wrong trade.

Full read: `reports/audit/free-basgiath-zones/SYNTHESIS.md`.

## Plan

### 1. Cut the redundant chasm carve

`scripts/zones/parapet.py`, `_chasm()`. Today:

```python
ctx.fill(15, -1, 12, 77, -1, 28, "stone")
ctx.fill(15, 0, 12, 77, ctx.DECK_Y - 1, 28, "air")
```

The second line carves `y=0..31` over `x=15..77`, `z=12..28`. **Nothing places a non-air block in that box.** The world is flat and the box sits above the surface, so the carve is a no-op that costs 34,272 air blocks on every phone.

**Delete the second line.** Keep the first line. It changes the floor from grass to stone, which is real work.

Update the docstring to say the floor stays at ground level and the air above it is already open.

Note the trade: this removes robustness for a **non-flat** world. The shipped world is flat. Record the choice in the commit.

### 2. Restore the far air retry

`scripts/build_map.py`. Delete the filter line and the comment above it. Restore `far` to the full far set.

### 3. Add a guard so this cannot come back

In `main()`, next to the east-stairs and lodestone checks, add an assert that the far set still holds air fills. Fail the build when it does not. The count is large; assert that it is at least 100 air lines.

### 4. Teach the static bench the phone path

`scripts/bench_static.py` replays only `stage_*.mcfunction`. It never reads `far_*.mcfunction`, so it stayed green while the phone path broke. Make it replay the stage files **and** the far files together.

Keep its existing checks and its three negative proofs working.

### 5. Confirm the budget

After steps 1 and 2, the counted air volume must be under 80,000 **with the retry included**. Expected: about 34,328.

## Success criteria

1. `python3 scripts/build_map.py` exits 0.
2. All gates pass.
3. The air volume counted by `test_release.py` is under 80,000 **and** the far set contains air.
4. `bench_static.py` reads the far files. Prove it by deleting one far file in a scratch copy and watching the bench fail.
5. `grep -c 'endswith(" air")' scripts/build_map.py` returns 0.

## Verify

```
python3 scripts/build_map.py
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh
python3 scripts/test_release.py
python3 scripts/bench_static.py
```

All six must pass.

## NEVER

- Do not change `addon/behavior_pack/manifest.json`. Keep the two 2.0.0 deps. No Beta APIs.
- Do not touch the other zone modules.
- Do not use a person name or paste book text.
- Do not raise the 80,000 air gate. Fix the volume, not the gate.
- Do not print, write, or commit a key.
- Do not commit or push.
