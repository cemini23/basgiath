# z4 Gauntlet report

Zone: Gauntlet, stages 31-40. File: `scripts/zones/gauntlet.py` (new).

## What I built

A stepped stone cliff in `x=146..168`, `z=80..140`, east of the dorms. The
cliff is eight flat terraces. Each terrace is one leg of the course and each
leg is four blocks higher than the one before it.

| Band | z | floor y | Leg |
| --- | --- | --- | --- |
| 0 | 80-81 | 0 | approach from the college |
| 1 | 82-84 | 1 | leg one, heads east |
| 2 | 85-88 | 5 | leg two, heads west |
| 3 | 89-92 | 9 | leg three, heads east |
| 4 | 93-96 | 13 | leg four, heads west |
| 5 | 97-100 | 17 | leg five, heads east |
| 6 | 101-104 | 21 | leg six, heads west |
| 7 | 105-140 | 25 | summit |

The path is a three-wide `stone_bricks` strip on the north side of each
terrace. The south side of every leg is the next riser, so the ledge has a
wall uphill and a drop downhill. Each exposed riser is `cobblestone` against
the `stone` mass, so the cliff face reads as rough rock.

### Five switchbacks

- Turn one, east end, `stone_bricks` stairs at `x=161..164`, `z=82..84`, y=1 to 5.
- Turn two, west end, `x=151..148`, `z=85..88`, y=5 to 9.
- Turn three, east end, `x=161..164`, `z=89..92`, y=9 to 13.
- Turn four, west end, `x=151..148`, `z=93..96`, y=13 to 17.
- Turn five, east end, is the chimney (obstacle five), y=17 to 21.

Every turn reverses the run (180 degrees) and ends four blocks higher. A
`stone_bricks` wall between legs means the turn is the only route up.

### Six obstacles, in order

1. Horizontal oak log: `oak_wood` bar at `x=152`, y=2, `z=82..84`, across leg one.
2. Rising stone pillars: `granite` walls at `x=159,157,155,153` on leg two, heights 1, 2, 3, 4.
3. Stone ring with one air gap: a square `stone_bricks` ring at `x=157`, y=10..14, `z=89..92`, with the top-centre block at `(157,14,91)` set to air.
4. Cobblestone clusters: `cobblestone` patches at `x=160-161` (1 high), `x=157-158` (2 high), `x=154-155` (1 high), plus singles at `x=162` and `x=152`, all on leg four.
5. One-block chimney with ladders: a `stone_bricks` block at `x=161..164`, y=18..21, `z=97..100`, with a 1x1 air shaft at `(162,18..21,98)`, a two-block entry at `(161,18..19,98)`, and a `ladder` column at `(162,18..21,98)`. The climb is also turn five.
6. Oak stair ramp: `oak_stairs` on `oak_planks` at `x=151,150,149,148`, y=22..25, `z=101..104`, from leg six up to the summit.

### Ropes

`chain` columns beside each leg at `x=148,154,160` (one every six blocks).
Each rope starts three above the lower floor and ends three above the upper
floor, so a walker passes under it and only a faller grabs it. 18 ropes.

### Summit

A low `stone_bricks` parapet on the south and east edges, and a small
`ctx.shell` lookout at `x=163..167`, y=26..30, `z=108..112`, with a door, a
`lantern`, and one `armor_stand` named "Gauntlet timekeeper" (a role, not a
person). It stands in for the wingleader who records the times.

### live_lines()

`live_lines()` is not wired yet. The integrator appends it. Every line carries
the `build_anchor` execute wrapper. It does:

- Clears `rope_touch` on every player each tick.
- For each of the 18 rope boxes: if a player is inside and lacks `rope_cool`,
  adds 30 to `#gauntlet map_state`; then tags the player `rope_touch`.
- Players still touching keep `rope_cool`; players who left lose it. So the
  score is added once per grab, not once per tick. `rope_told` fires one
  actionbar line the first time a player grabs a rope.
- A `#spinline` counter with a two-frame `basic_smoke_particle` puff at each
  end of the log bar, as a stand-in for a spin.

`build()` also sets `#gauntlet map_state` to 0. It relies on the `map_state`
objective that `build.mcfunction` creates before the stages run.

## Files touched

- `scripts/zones/gauntlet.py` (created).
- `reports/zones/z4-gauntlet.md` (created).

Nothing else. `git status` shows only the pre-existing dirty tree plus these
two new files. No commit, no push, no key printed, no external model called.

## Commands I ran

Only reads, `py_compile`, and two throwaway checkers in `/tmp` (nothing
written inside the repo except this report and the module):

- `python3 -m py_compile scripts/zones/gauntlet.py`
- `python3 /tmp/z4_check.py` (imports the zone, rebuilds commands with a copy
  of the driver's fill splitter, checks the stage range, the region, fill
  volumes, the water/name bans, and the live-line anchor)
- `python3 /tmp/z4_walk.py` (replays the commands into a block map and walks
  the course with a BFS that models one-block steps, drops, and ladder
  climbs)

I did not run `scripts/build_map.py`, `scripts/package.sh`, or
`scripts/test_release.py`. I did not run git checkout, restore, reset, or
clean.

Results:

- `build()` returns 96 commands (budget: under 400).
- One fill is at most 21,528 blocks (limit 32,768).
- Every fill and setblock is inside `x=146..168`, `z=80..140`.
- No `water`, no person name, no series title, no book line.
- `live_lines()` returns 45 lines, 18 of them score adds (`#gauntlet`), every
  line carries the anchor.
- The walk replay reaches the approach, all six legs, and the summit when the
  parkour-only pieces are removed. The full course needs real 2-block jumps
  at the pillars and the cobbles, which the one-block BFS cannot model.

## What I could not do

- **A true spinning log.** A `oak_log`/`oak_wood` bar is symmetric around its
  long axis, so a real spin is invisible with vanilla blocks and would need
  an entity or a per-tick clone rig. I used a horizontal `oak_wood` bar (bark
  on all sides) and a two-frame smoke puff at the ends instead.
- **Block states.** The repo has no block-state commands, so I did not risk
  state syntax. The log is `oak_wood`, and the `oak_stairs` and `ladder`
  blocks use Bedrock default facing. If the ladder or stair facing looks
  wrong in game, a later pass can set `facing_direction`/`weirdo_direction`.
- **The steep staircase beside the switchbacks to the flight field.** Canon
  mentions it (used after Presentation, not during the Gauntlet). I left it
  out because it would be a ground-to-summit bypass of the course and the
  flight-field agent owns that connection.
- **Wiring.** I did not edit `scripts/build_map.py`, the stage writer, or the
  tick, so the zone is not yet called and `live_lines()` is not yet in
  `basgiath/live`. The integrator must add the import, the call order between
  College and Presentation, and the live lines.
- **In-game testing.** I could not launch Minecraft, so collision, ladder
  climb, and stair facing are reasoned and simulated, not observed.
- **Rope coverage.** The penalty only fires at the 18 rope columns. A fall
  between two ropes adds nothing. That matches "safety ropes every six feet",
  but it does mean a careful faller can miss every rope.
- The score is a fake-player total. Nothing shows the running time to the
  player yet except the one-time actionbar line.
