# Zone 3 report — Citadel (College)

Agent: Citadel. Task file: `/tmp/basgiath-swarm/z3.md`.
Module: `scripts/zones/dorms.py` (stage range 21–30, replaced in place).

## What I built

The three spruce huts are gone. One college group now stands in x=96..145,
z=80..122, all on one stone court at ground level y=-1 (the same level as the
Quad floor), so the player walks in from the north and the west with no step.

### 1. Rotunda (three stories, four door gaps, glass dome)

- Centre (110, 98), radius 10. A solid stone-brick cylinder from y=-1 to y=7,
  hollowed inside with air. The ground floor is `polished_andesite` set into
  the `smooth_stone` court; the two upper story floors are `polished_andesite`
  at y=2 and y=5, with a small open shaft at the centre.
- Four door gaps, each cut clean through the curved wall:
  - north (z≈88) — opens on the Quad, the north entry;
  - west (x≈100) — opens on the path down to the valley, the west entry;
  - south (z≈108) — opens on the college court;
  - east (x≈120) — opens toward the dorm court.
  A `smooth_stone` floor is re-laid under each opening so every threshold is
  walkable, and a passage is opened south to the court through the old wall
  line at z=112.
- Glass dome stepped over the stone cap (radius 9, 7, 5, 3, 2, 1) with a glass
  keystone. Lanterns light the ground floor.
- Four wool pillars between the doors: orange and black, as the canon calls
  for between the academic wing doors. They sit inside the wall line so they
  do not seal the side doors.

### 2. Keep (one arched door, one armor stand)

- Footprint x=126..140, z=100..110, top y=8, stone-brick shell, polished stone
  floor at y=-1.
- One arched door on the west face at z=104..105: a 1x2 opening under
  `stone_brick_stairs` springers and a stone lintel, with stone jambs at both
  sides. This is the only way in.
- One armor stand at (130, 0, 105), inside, facing the door. Its display name
  is an original line: **"A rider kneels, and the dragon decides."** It is not
  a book line and contains no person name.

### 3. Dorm block (three stories, four rows of beds, one private room)

- Footprint x=126..140, z=84..92, shell to y=9. Ground floor, then stone floor
  slabs at y=2 and y=5, giving three stories.
- Four rows of `red_wool` beds at z=86, 88, 90, 92 (five beds a row, kept clear
  of the ladder well).
- A ladder shaft at (127, 85) joins all three stories: ladders at y=-1, 1 and
  4, with the slabs opened at y=2 and y=5.
- Door gap on the north face at x=132..133, under a stone-brick stair lintel.
- One private room at x=142..144, z=87..93: a small hollow with a door gap on
  its west face (z=90) into the dorm, plus its own one-block door on the outer
  west face. One bed and one lantern inside.

### 4. Classroom (shell with lecterns)

- Footprint x=102..122, z=112..120, shell to y=5, polished stone floor, hollow
  inside.
- One arched door on the west face at z=116..117, opening onto the west path.
- Eight `lectern` blocks with varied `facing_direction`, plus two lanterns.

## Entry gaps (both required, both verified)

- **North (the quad):** the rotunda's north door at z≈88 lines up with the
  quad edge at z=80. I confirmed a continuous walk from (110, 0, 80) to the
  rotunda centre.
- **West (the valley path):** the rotunda's west door leads to a paved court
  at x=96..101 that meets the existing valley path along z=116..120. I
  confirmed a walk from the valley path at (98, 0, 118) into the rotunda, and
  out of the rotunda west door to the zone edge at x=96.

## Verification I ran

I wrote throwaway Python checks in the shell (no test file added to the repo).
I imported the real `ZoneCtx` and `assert_walk` from `scripts/build_map.py` and
re-simulated the full block map from the emitted commands (`~`-relative, in
anchor space).

- **Command budget: 237 commands**, under the 400 limit.
- **Every fill is at most 3969 blocks**, far under the 32768 cap.
- **Total air carved: 5269 blocks**, well under the 80000 air budget. The
  largest single air fill is the rotunda interior (18 x 6 x 18); the hint was
  about 20 x 12 x 20, so the box is small.
- **Bounds:** every fill and setblock lies inside x=96..145, z=80..122, with no
  block below y=-1. Nothing is west of x=96, so the valley is untouched.
- **Walkability:** a BFS over the full four-zone block map passes for all nine
  routes: quad→rotunda, valley→rotunda, rotunda→west/east/south exits,
  quad→dorm, dorm→private room, through the keep arch, and through the
  classroom west door.
- **Driver assertion:** `assert_walk()` from `scripts/build_map.py`, run over
  all four zones in order, passes.
- **Blocks used:** `stone_bricks`, `smooth_stone`, `polished_andesite`, `glass`,
  `lantern`, `sea_lantern`, `stone_brick_stairs`, `red_wool`, `orange_wool`,
  `black_wool`, `ladder`, `lectern`, `air`. All vanilla. No water. No custom
  dimension.
- **Text:** no person names and no series or book titles in the file (checked
  against the naming policy in `docs/CANON.md`). The one sentence is original.
- `python3 -c "import ast; ast.parse(...)"` passes on the module.

## Files touched

- `scripts/zones/dorms.py` — rewritten (the only source file I changed).
- `reports/zones/z3-citadel.md` — this report.

No other file was edited. I did not run `scripts/build_map.py`,
`scripts/package.sh`, or `scripts/test_release.py`. I did not run git
checkout, restore, reset, or clean. I did not commit or push. I did not print
a key. I did not call Claude or OpenAI.

## What I could not do

- **The rotunda's upper two stories are not connected by an interior stair.**
  The floors are solid with a small open shaft. A stair would need more
  commands and more air carving; the task asked for a shell and a small air
  box, so I left the shaft open. A player reaches the upper floors only from
  outside (there is no exterior opening above the ground floor).
- **The arch is one block wide, not a wide gate.** The keep face is 11 blocks
  long, so a wider arch is possible, but a 1x2 arched opening reads best at
  this scale and keeps the "one arched door" reading.
- **The dorm beds are `red_wool`**, exactly as the task asked. They are not
  full `bed` blocks, so they do not set a spawn point or sleep.
- **I did not build any terrain.** The zone sits on the existing flat ground
  plane. The Quad's `stone_bricks` fill at y=-1 extends to x=168, so the court
  is continuous with the Quad without a seam.
- **I did not run the game or the Bedrock pack.** I could not verify that the
  `lectern [facing_direction=N]` and `ladder [facing_direction=2]` block states
  are accepted by this Bedrock version, only that the syntax matches vanilla.
  These would be the first things to check in a live world.
- **One step at the zone edge remains.** The plaza is at y=-1 and the Quad
  floor is at y=-1, so there is no step north. The valley path is also at y=-1.
  The only step is the natural one-block lip already present at the old wall
  line, which I opened through the south court passage.
