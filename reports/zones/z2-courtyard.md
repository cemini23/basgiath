# z2 — Courtyard and Formation agent report

Scope: keep the stone court, ring it with the canon courtyard wall, and add the
Formation roll-call beat, per `docs/CANON.md` section 2 and
`scripts/zones/README.md`. Two files touched: `scripts/zones/quad.py` (edited)
and this report. Nothing else in the tree was edited.

## What I built

### The wall ring — `scripts/zones/quad.py`

A solid `stone_bricks` ring over the rim of `x=96..168`, `z=4..78`.

- 10 blocks thick: west `x=96..105`, east `x=159..168`, north `z=4..13`,
  south `z=69..78`.
- 8 blocks tall: `y=0..7`, standing on the existing floor at `y=-1`.
- One opening, west face, full 10-block depth: `x=96..105`, `y=0..7`,
  `z=18..26`. The gate is derived from `ctx.SPAN_Z` (`SPAN_Z - 2` to
  `SPAN_Z + 6`), so it stays lined up with the Parapet path.
- The opening is written as an explicit `air` fill too, so it can never be
  sealed by a later edit.
- The inner footprint left for the court is `x=106..158`, `z=14..68`.

The wall closes the ring, so the courtyard has exactly one way through: the
west gate. This is canon (section 2: "There is one opening. That opening is
the Parapet.").

### What was kept

| Item | Action |
| --- | --- |
| Stone floor `x=96..168, z=4..78, y=-1` | kept unchanged |
| Bleachers | kept, moved inboard to `z=14..17` and `z=65..68` so the 10-thick wall does not bury them. Four rows per side, tallest against the wall, `x=108..156` |
| Wool poles (`122/134`, `z=34/46`) | kept exactly where they were |
| Bell tower | kept, moved inboard to `x=144..150, z=20..26`, same 7×7 shell, `bell` at `147,15,23`, `sea_lantern` on top |
| Lantern posts | kept, moved from `x=104` to `x=110` because `x=104` fell inside the new west wall |

### The plaza marker

`128, 0, 40` is now `chiseled_stone_bricks`. No summoning stone or lodestone is
placed or named by this file. The signet stone belongs to the valley, per the
`signet.py` handoff in `reports/zones/z6-signet.md`.

### The roll-call beat

- A square of 36 `armor_stand` markers on the plaza platform: 4 rows (the
  wings) at `z=36, 38, 40, 42`, and 9 columns (three sections of three squads)
  at `x=124..132`, all at `y=1`. Names are `wing<1-4>_<flame|claw|tail>_squad<1-3>`.
- A roll desk at the head of the square: `chiseled_stone_bricks` at
  `128, 0, 34` and a `lectern` at `128, 1, 34`.
- Six `tellraw @a` lines, emitted once from `build()`:

  1. `Roll call. Four wings answer in this courtyard. Find your row.`
  2. `Each wing carries three sections: Flame, Claw, and Tail.`
  3. `Each section holds three squads. Nine marks stand in three groups of three.`
  4. `First-years hold the back two rows of the square until a name is read.`
  5. `Wingleaders and section leaders are third years. A rare second year may lead a squad.`
  6. `The scribes read the death roll. We answer for the cadets who did not live to stand here.`

  These teach 4 wings, the 3 named sections, 3 squads per section, and a death
  roll line. Line 6 names no person. All lines are original. No book text, no
  person name, and no series title appears in the file.

### Budget and hard limits

Measured on the emitted command list (stub context that copies the driver's
`_segments` / `_split_box` exactly):

- 104 commands for the whole zone (fill 25, setblock 37, summon 36, tellraw 6).
  Limit is 400.
- Largest single `fill` is 5,840 blocks (the south wall). Limit is 32,768.
- Every block sits inside `x=96..168`, `z=4..78`; no command leaves the box.
- Vanilla blocks only: `stone_bricks`, `chiseled_stone_bricks`, `sea_lantern`,
  `lantern`, `air`, `bell`, `lectern`, four wool colours. No water.

## Files touched

| File | Action |
| --- | --- |
| `scripts/zones/quad.py` | edited (full rewrite of the body; same `build(ctx)` interface, same stage range 13-20) |
| `reports/zones/z2-courtyard.md` | created (this report) |

No other file was edited. No `git checkout`, `git restore`, `git reset`, or
`git clean` was run. No commit, no push, no key printed.

## Commands I ran

All read-only or in-memory. No repo file other than the two above was written.

1. `read` on the task file, `docs/CANON.md`, `scripts/zones/README.md`,
   `scripts/zones/quad.py`, `scripts/zones/parapet.py`,
   `scripts/zones/valley.py`, `scripts/zones/dorms.py` (extents),
   `scripts/build_map.py` (driver, ctx, `assert_walk`),
   `reports/zones/z6-signet.md`.
2. `python3 -m py_compile scripts/zones/quad.py` → passed.
3. `/tmp/z2_check.py` — a stub context that copies the driver's `_segments`,
   `_split_box`, `rel`, and `ZoneCtx` surface, then imports `zones.quad` and
   runs `build(ctx)`. It reported: 104 commands, largest fill 5,840, no fill
   over 32,768, no block outside `x=96..168 / z=4..78`, no non-air block inside
   the gate box, 36 summons, 6 tellraw, and zero occurrences of the word
   lodestone in the output.
4. `/tmp/z2_walk.py` — a harness that imports the four zone modules, replays
   the driver's `paths()` and `finish()` in memory, then copies the driver's
   `solid_blocks`, `_can_stand`, and `_reachable` to re-run `assert_walk`'s two
   goals. Both still pass: `start → span` true, `east roof → quad` true. It also
   confirmed `(128,0,40)` is `chiseled_stone_bricks` and that the emitted
   geometry now contains no lodestone at all.
5. A case-insensitive grep of `scripts/zones/quad.py` for the forbidden person
   names, the series and book titles, and `lodestone` → no hits.
6. `git status --short`, `git diff --stat`, `git check-ignore` to record the
   edit set.

I did **not** run `scripts/build_map.py`, `scripts/package.sh`, or
`scripts/test_release.py`. I did not call Claude or OpenAI.

## What I could not do

- **No in-game check.** There is no Bedrock client or server here, so I could
  not stand in the gate, walk the ring, or read the roll-call lines in chat.
  Everything above is verified from the emitted command list only.
- **The driver will now fail its own lodestone assert.** `scripts/build_map.py`
  line 466 raises `far retry missed the lodestone` when no command outside the
  loaded box names a lodestone. My file does not place one, and `signet.py`
  (lodestone at `50, -1, 130`, far) is **not wired into `geometry()`**. So
  `python3 scripts/build_map.py` will exit until the integrator either wires
  `zones.signet` after `valley.py` or replaces that assert. This is the
  expected shape of "the signet stone moves to the valley".
- **`test_release.py` has the same dependency.** Its release blob must contain
  the string `lodestone`. Wiring `signet.py` supplies the valley stone and
  satisfies it. I could not run the test, by rule.
- **`bench_static.py` will need a one-line update.** It pins
  `LODESTONE = (128, 0, 40)` and fails unless that block is `lodestone`; it is
  now `chiseled_stone_bricks`. The integrator should repoint it at the valley
  stone or expect chiseled stone there. I was told not to edit any other file,
  so I left it.
- **The south wall closes the old overland route.** The driver's path
  `108,-1,79 → 112,-1,89` and the dorms' north approach now sit outside the
  ring. Walkers must leave by the west gate and go around. That is canon for
  the courtyard (one opening), but it is a routing change the integrator may
  want to record in the README or a path.
- **The "keep" clause needed relocation.** The bleachers and the bell tower did
  not fit inside a 10-thick wall where they stood, so I kept them by moving
  them inboard rather than deleting them. If the intent was to leave them
  exactly in place, the wall would have overwritten them.
- **No block-built sign text.** Bedrock `oak_sign` set by `setblock` carries no
  text without NBT, so literal signage would be blank. The task allows armor
  stands, and I used those for the wing square; the teaching text is carried by
  the six tellraw lines.
- **`armor_stand` nametag syntax.** I used the same name-first form the driver
  and `dorms.py` already use (`summon armor_stand "name" ~x ~y ~z`). It matches
  the existing code, but I could not confirm it against a live Bedrock server.

## Open item for the integrator

Wire `zones.signet` into `scripts/build_map.py` after `valley.py` in the canon
order (it is the valley stone the task refers to), then drop or rewrite the
`far retry missed the lodestone` assert and, if desired, move
`bench_static.py`'s `LODESTONE` marker to `(50, -1, 130)`. Until then the
generator stops on the lodestone check even though `quad.py` itself is inside
its budget and its box.
