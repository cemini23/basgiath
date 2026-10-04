# z5 — Flight-field / Presentation agent report

Task file: `/tmp/basgiath-swarm/z5.md`.
Module: `scripts/zones/flight.py` (new, stage range 41–48).
Canon read first: `docs/CANON.md` section 5 (Presentation) and
`scripts/zones/README.md` (interface, budgets, stage table, text rules).

Scope: one new zone module and this report. No other file touched.

## What I built

The flight field is a box canyon in `x=100..145, z=124..148`, south of the
dorms (the dorms fence ends at `z=122`). The floor is the college ground at
`y=-1`, so the field shares the Quad and Citadel level. Every emitted command
stays inside the box.

### Walls — three sides, north open

- West `x=100..101`, east `x=144..145`, south `z=147..148`: `stone` from
  `y=-1` to `y=31`.
- A `stone_bricks` cap at `y=32` (`ctx.DECK_Y`), so the rim is cut level with
  the old span deck. The wall reads as a built cliff edge, not loose rock.
- A `stone_bricks` course at the foot of each inner face (`y=-1..0`).
- The north side (`z=124`) is left open across the full 46-block width, toward
  the path from the dorms. Nothing is placed north of `z=124`.

### Gate at the mouth

- Two hollow `stone_bricks` posts, `x=117..119` and `x=125..127`,
  `z=124..126`, `y=-1..3`, built with `ctx.shell`. Each 3×3×5 post keeps a
  hidden 1×1×3 core (3 air blocks each, 6 for both).
- One beam over the posts at `y=4`, spanning `x=117..127` at `z=124..126`.
- A `stone_bricks` threshold at `z=124`, `x=118..126` on the floor.
- Clearance under the beam is four blocks (`y=0..3`).

### The walk

- `dirt_path` down the middle: `x=121..123`, `z=125..144`. The length is
  `ctx.SPAN_Z` (20) blocks, starting at `z=125` so the mouth stays clear.
- The path is three wide and centered on the field. It is the only line the
  player follows. No control, form, or pick UI exists anywhere in the zone.

### Dais, bleachers, dragon line

- **Dais**: `smooth_stone`, `x=114..130`, `z=145..146` at `y=0` — one step up
  from the walk, at the south end. Each back corner carries a `stone_bricks`
  post (`y=1`) and a `lantern` (`y=2`).
- **Bleachers**: four `stone_bricks` rows along the west wall, `z=126..144`,
  facing the walk. Tops step down from the wall: `x=102` top `y=3`, `x=103`
  top `y=2`, `x=104` top `y=1`, `x=105` top `y=0`.
- **Dragon line**: six wool posts in a row on the east side at `x=141`,
  `z=126, 130, 134, 138, 142, 146`. Each is a `stone_bricks` base at `y=-1`
  and three wool blocks at `y=0..2`. Colours, in order: `white_wool`,
  `orange_wool`, `yellow_wool`, `lime_wool`, `light_blue_wool`,
  `purple_wool`. Colour only. No summon, no entity, no name.

### Seasonal fall

- `light_blue_stained_glass` on the inner face of the south wall:
  `x=105..107`, `z=147`, from `y=0` to `y=31`, with the lip at `y=32` in the
  brick cap. The column runs the full wall height so it reads as melt off the
  rim in season.
- A small glass apron at `y=-1`, `x=105..107`, `z=145..146`.
- No water block and no bucket is placed. The **string** `" water"` does not
  appear in any emitted command either: the release test greps the whole
  function blob for `" water"`, so a `" waterfall"` tellraw line would trip
  it. The fall is therefore described without that word.

### Meadow

- `short_grass` (65 blocks) and six flower kinds (`dandelion`, `poppy`,
  `cornflower`, `oxeye_daisy`, `azure_bluet`, `allium`) scattered on `y=0`
  with a fixed formula seeded from `ctx.START`. Nothing lands on the walk,
  the dais, the bleachers, the gate, the posts, or the fall apron.

### The one tellraw

```
tellraw @a {"rawtext":[{"text":"Keep to the middle path. The dragons watch. This walk is for them to look, and it is not the choosing."}]}
```

Original text, no book line, no person name, no series title. It tells the
player the walk is for the dragons to look and is not the choosing. It is the
only tellraw in the module and it is added inside `build()`.

## Interface and context

- `STAGE_START = 41`, `STAGE_END = 48`; `build(ctx) -> list[str]` ends with
  `return ctx.take()`.
- Uses `ctx.fill`, `ctx.setblock`, `ctx.shell` (the gate posts), `ctx.add`.
- Reads `ctx.DECK_Y` (rim and fall height), `ctx.SPAN_Z` (walk length),
  `ctx.START` (meadow seed). No `build_map` import.
- Vanilla blocks only. Block ids used: `stone`, `stone_bricks`,
  `smooth_stone`, `dirt_path`, `light_blue_stained_glass`, `short_grass`,
  `dandelion`, `poppy`, `cornflower`, `oxeye_daisy`, `azure_bluet`, `allium`,
  the six wools, `lantern`, `air` (gate cores only).

## Measured numbers

| Check | Value | Limit |
| --- | --- | --- |
| Emitted commands | 113 | under 400 (8 stages × 50) |
| Largest single `fill` | 3036 blocks (south wall) | 32768 |
| Air fills added by this zone | 6 blocks (two gate cores) | — |
| Air across all four current zones + this one | 53,812 | 80000 |
| Out-of-box commands | 0 | — |

Block census of the zone: `stone` 5791, `stone_bricks` 720,
`light_blue_stained_glass` 105, `short_grass` 65, `dirt_path` 60,
`smooth_stone` 34, `air` 6, wool 3 each (18), `lantern` 2, flowers 7.

Because every coordinate is outside the driver's ±48 loaded box, 112 of the
113 commands are classed `far` by `is_far()` and are copied into the
`far_NN` retry pass. The `college_d` ticking area is centered at `(120,110)`
with radius 4, which covers `z=124..148`; the integrator must keep that area
loaded or the field will not place in the second pass.

The zone alone fits in 3 stage files (50 commands each). The integrator's
call order decides which numbered stages the block actually lands in.

## Files touched

| File | Action |
| --- | --- |
| `scripts/zones/flight.py` | created |
| `reports/zones/z5-flight.md` | created (this report) |

No other file was edited. I did not run `git checkout`, `git restore`,
`git reset`, or `git clean`. The repo already had uncommitted changes to other
files (`README.md`, the generated functions, `manifest.json`, `main.js`,
`build_map.py`, `test_release.py`) when I started; I left all of them alone.
`__pycache__/` is gitignored and the stub harness lives in `/tmp`, not in the
repo.

## Commands I ran

Read-only and local checks only:

1. `python3 -m py_compile scripts/zones/flight.py` → passed.
2. `python3 /tmp/z5_check.py` — a stub `ctx` that mirrors the driver's
   `rel()`, `_segments()`, `_split_box()`, and `shell()`. It imported
   `zones.flight` (not `build_map`) and asserted: stage range 41/48; 113
   commands; every `fill` ≤ 32768; every setblock/fill inside `x=100..145,
   z=124..148`; no `" water"` substring; no `summon`; no `dragon_rider`; no
   `lodestone`; exactly one `tellraw`; the walk cells are exactly
   `x=121..123, z=125..144`; the source uses `ctx.DECK_Y`, `ctx.SPAN_Z`,
   `ctx.START`, `ctx.fill`, `ctx.setblock`, `ctx.shell`, `ctx.add`; no
   `build_map` import; no forbidden name. Result: **PROBLEMS: none**.
3. `python3 /tmp/z5_air.py` — summed `air` fill volume for `parapet` (44,832),
   `quad` (1,120), `dorms` (5,269), `valley` (2,585) and `flight` (6) with the
   same stub: **53,812 of 80,000**, headroom 26,188. This is why the three
   walls are explicit `fill`s: a full-canyon `ctx.shell` would have added
   ~32,000 air blocks and broken the release-test budget.
4. `python3 /tmp/z5_map.py` — applied the emitted commands to a grid and
   printed top-down maps at `y=-1` and `y=0`, a side section down the walk
   (`x=122`), and a south-wall section at `z=147`; confirmed the north side
   is open, the gate reads as a gate, the walk runs unbroken to the dais, and
   the glass column is flush in the south wall.
5. A final Python one-liner printed the max fill (3036), the far count
   (112/113), and the tellraw line.
6. `git status --short` — read-only, to confirm the edit set.

I did not run `scripts/build_map.py`, `scripts/package.sh`, or
`scripts/test_release.py`. I did not commit or push. No key was printed. No
Claude or OpenAI call was made.

## What I could not do

- **No in-game check.** There is no Bedrock client here, so the wall height,
  the four-block gate clearance, the one-block step onto the dais, the
  bleacher climb, and the look of the glass fall are unverified in the game.
  They are verified as coordinates and command text only.
- **Release test not run.** `scripts/test_release.py` was off limits for this
  task. I checked its relevant rules by hand instead: no `" water"` substring
  in any command; no forbidden name in the file; every `fill` ≤ 32768; air
  volume counted (6 here, 53,812 total).
- **`dirt_path` vs `grass_path`.** The task allowed either. I used
  `dirt_path` (the Bedrock rename of the old `grass_path`; the target is
  1.21.90). I could not confirm the id in a client.
- **The module is not wired in.** The zone list and call order live in
  `scripts/build_map.py`, which I was told not to edit. Until the integrator
  adds `zones.flight` in canon order — after the Gauntlet, before Threshing —
  the field does not appear in a built world. The stage table reserves 41–48
  for exactly this module.
- **No dragon, no choice control, by design.** There is no entity, no form,
  and no block that opens one (in particular no lodestone, which would open
  the signet gate). The dragons are six wool markers; the watching is implied
  by the tellraw. I could not test how that reads on a phone.
- **Canon tension I did not act on.** Canon section 5 puts the Vale's
  entrance at the narrowest part of the field by the seasonal fall. Here the
  fall sits on the south wall near the west corner (the side closest to the
  valley at `x=16..70`), but no opening is cut through the wall, because the
  task requires three closed sides with the only opening to the north.

## Open item for the integrator

Add `zones.flight` to `scripts/build_map.py` in the canon play order after the
Gauntlet and before `zones.valley`, keep the 41–48 stage window, and keep the
`college_d` ticking area over `z≈124..148` so the far retry pass places the
field.
