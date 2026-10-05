# Third-audit fixes

## WorkDir

`/Users/claudiobarone/Projects/dragon-rider-map`

## Context

The third audit ran on `e2acf93` and returned FAIL. Full read: `reports/audit/free-basgiath-third/SYNTHESIS.md`.

Three items. Two are small. Do not touch anything else.

## Plan

### 1. HIGH — the dorm summon is in absolute coordinates

`scripts/zones/dorms.py` builds the rider stand as a raw string and never passes it through `rel()`:

```python
ctx.add(
    'summon armor_stand "A rider kneels and the dragon decides." '
    f"{x0 + 4} 0 {(z0 + z1) // 2}"
)
```

Emitted today: `summon armor_stand "A rider kneels and the dragon decides." 130 0 105`.

Every other placement in the project is anchor-relative, for example `summon armor_stand "wing1_flame_squad1" ~124 ~1 ~36`. The build places the college at the player's feet, so the anchor is the player. An absolute stand is right only when the player stands at the origin. Anywhere else it is roughly 45 blocks out.

**Zones must not import `build_map`,** so do not reach for `rel()`. Write the tildes directly:

```python
f"~{x0 + 4} ~ ~{(z0 + z1) // 2}"
```

Check every other zone for the same mistake. `grep -n 'ctx.add' scripts/zones/*.py` and confirm each positional `ctx.add` line begins with `~`. Report anything else you find.

### 2. HIGH — the IP rule contradicts the IP doc

`docs/IP-RULES.md` rule 3 says character names are banned **"everywhere"**. `docs/CANON.md` line 220 lists fifteen of them as a denylist. `scripts/test_release.py` scans only `addon/` and `scripts/`, so the docs are not enforced.

The list is correct. The word "everywhere" is wrong.

**Reword rule 3** so the character-name ban names its scope: the map, the pack, and every shipped string. State that a policy doc may keep a denylist, and that `docs/CANON.md` holds it.

Do **not** delete the names from `docs/CANON.md`. A policy that cannot name what it bans is useless.

Do **not** extend the name scan to the docs. That would fail on the denylist.

### 3. INFO — the parser has a known edge

`_box()` in `scripts/build_map.py` understands three plain forms: `setblock`, `fill`, `summon`. A wrapped positional command such as `execute as @e[…] run setblock ~200 ~1 ~200 stone` returns `None`, so `is_far()` cannot see it. No such line is emitted today, and the guarded retry lines are safe because `bench_static.py` compares written files as strings.

Two changes, both small:

1. Teach `_box()` to strip a leading `execute … run ` and parse the tail. Use the **last** ` run ` in the line.
2. Add a check that a synthetic wrapped command is classified. Put a `execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run setblock ~200 ~1 ~200 stone` through the parser and assert it comes back far. Follow the shape of the existing `prove()` mutations in `bench_static.py`.

## Success criteria

1. `python3 scripts/build_map.py` exits 0.
2. All gates pass.
3. `grep 'summon armor_stand "A rider kneels' addon/behavior_pack/functions/basgiath/stage_*.mcfunction` shows `~130 ~ ~105`, not `130 0 105`.
4. No zone emits a positional `ctx.add` line without a leading `~`.
5. The wrapped-command fixture fails if the parser regresses.
6. `docs/IP-RULES.md` rule 3 no longer says "everywhere".

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

- Do not delete the denylist from `docs/CANON.md`.
- Do not extend `test_release.py`'s name scan to `docs/`.
- Do not change `addon/behavior_pack/manifest.json`. Keep the two 2.0.0 deps. No Beta APIs.
- Do not use a person name, a dragon name, or book text in any new string.
- Do not print, write, or commit a key.
- Do not commit or push.
