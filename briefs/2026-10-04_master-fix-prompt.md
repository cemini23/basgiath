# Master fix prompt — both audits

## WorkDir

`/Users/claudiobarone/Projects/dragon-rider-map`

## What this covers

Every open item from two free audits.

**Audit 1** (`reports/audit/free-basgiath-zones/SYNTHESIS.md`): **fully closed.** The far air retry is restored, the redundant chasm carve is gone, the far-air assert exists, and `bench_static.py` replays the far files. **Do not redo any of it.**

**Audit 2** (`reports/audit/free-basgiath-full/SYNTHESIS.md`): seven open items below. Item 1 is the one that changes the world.

## Plan

### 1. HIGH — the far retry drops every `summon`

`scripts/build_map.py`, `_box()`. It parses only `setblock` and `fill`. `is_far()` returns `False` for everything else, so no entity spawn can enter the far set.

Measured: 39 summon commands, 0 in the retry. All sit at `x >= 50`, outside `LOADED = 48`. They include the 36 roll-call armor stands (`x=124..132`), the Gauntlet timekeeper, the Threshing Roll-keeper, and a rider stand in the college.

On a phone these spawn against unloaded chunks and are never retried.

**Do this:**

1. Extend `_box()` to read a `summon` line. **The name tag is quoted and can contain spaces and commas**, so the coordinates are the **last three tokens** of the line, not fixed positions. Reuse the existing `_rel()` helper.

2. **Make the retry idempotent.** A `fill` can run twice safely. A `summon` cannot — the stage pass may already have spawned the entity, and the retry would add a second one. In the retry only, wrap each summon:

```
execute unless entity @e[type=armor_stand,name="<name>"] run summon armor_stand "<name>" <x> <y> <z>
```

Leave the stage pass summoning normally.

3. The rider stand's name contains a comma: `"A rider kneels, and the dragon decides."`. A comma inside a quoted selector argument is not safe. **Rename that stand** to a comma-free line of the same meaning, in `scripts/zones/dorms.py`.

4. `main()` already asserts the far set holds the east stairs and a lodestone. Add the same shape of assert for summons: fail the build when the far set holds no `summon`.

### 2. MEDIUM — the checker shares the generator's blind spot

`scripts/bench_static.py`, `phone_lines()`. Its `covered == retry` check compares two lists that both come from the same `is_far` filter, so it is tautological. It cannot catch a command class the filter ignores — which is exactly how item 1 survived.

Assert instead that **every positional command** whose target sits outside `LOADED` appears in the retry, for all command types the filter now understands.

Then prove it: in a scratch copy, drop one summon from a far file and confirm the bench exits non-zero. The proof is the point of this item.

### 3. LOW — the solid model is coarse

`scripts/build_map.py`, `_NON_SOLID`. Handle `ladder` as **climbable** in the reachability check, not as air.

**Do not** add `stone_brick_wall`, `oak_stairs`, or `stone_brick_stairs` to `_NON_SOLID`. They are solid. Adding them would let the walk checker pass through walls.

### 4. LOW — three wait times for one wait

The tellraw and the code both say 15 seconds. `README.md` line 79 says "about 20 seconds". Use **15 seconds** everywhere. Check `DESIGN.md` too.

### 5. LOW — a gate that encodes a number the generator chooses

`scripts/test_release.py` line 114 hard-codes `"function basgiath/stage_20"`. It breaks the moment a zone grows past 32 stages. Derive the last stage number from `build.mcfunction` instead of writing it down.

### 6. LOW — doc/code drift

`scripts/zones/quad.py` docstring says the one opening is the only way through the courtyard ring. The east descent flies over the wall at `y=18..27` and lands inside. Either route the descent through the gate, or reword the docstring to say the ring is a silhouette and the gate is the ground route. Prefer the reword.

### 7. INFO — document the air-gate count

`scripts/test_release.py` counts air over all `*.mcfunction`, so far air is counted in both the stage pass and the retry. The phone does run both, so the count is conservative, not wrong. Add a comment that says so, so a later reader does not read it as a bug.

## Success criteria

1. `python3 scripts/build_map.py` exits 0.
2. All gates pass.
3. The far set contains summons, and every far summon is wrapped in `unless entity`.
4. The bench fails when a summon is dropped from a far file in a scratch copy.
5. No comma remains inside any selector name.
6. All six gates plus `bench_static.py` pass.

## Verify

```
python3 scripts/build_map.py
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh
python3 scripts/test_release.py
python3 scripts/bench_static.py
```

## NEVER

- Do not re-do audit 1's work. The far air is fixed.
- Do not change `addon/behavior_pack/manifest.json`. Keep the two 2.0.0 deps. No Beta APIs.
- Do not add `stone_brick_wall`, stairs, or `lectern` to `_NON_SOLID`.
- Do not raise the 80,000 air gate.
- Do not use a person name, a dragon name, or book text.
- Do not print, write, or commit a key.
- Do not commit or push.
