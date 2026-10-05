# Playability and correctness fixes — audits 4 and 5

## WorkDir

`/Users/claudiobarone/Projects/dragon-rider-map`

## Read first

`reports/audit/free-basgiath-fourth/SYNTHESIS.md` and `reports/audit/free-basgiath-fifth/SYNTHESIS.md`.

**Implement in the order below.** Part A changes how the map plays. If you run out of room, finish a whole numbered item and stop at a clean boundary, then report exactly what you completed.

## HARD BOUNDARY

Write only inside `/Users/claudiobarone/Projects/dragon-rider-map`. Never touch `~/.pyenv`, `~/.local`, `~/.cemini`, or any home-directory dotfile.

---

# Part A — the map can be skipped

## A1. Turn the experiments off

`scripts/build_world.py` writes `level.dat` with:

```python
"experiments": {
    "experiments_ever_loaded": Byte(1),
    "beta_apis": Byte(1),
    "gametest": Byte(1),
},
```

`DESIGN.md` and `README.md` both forbid Beta APIs. Set `beta_apis` and `gametest` to `Byte(0)`. Keep `experiments_ever_loaded`.

Add a check to `scripts/test_release.py` that reads the emitted world and fails if either is non-zero. Checking the manifest's dependency versions is not enough — that is how this survived four audits.

## A2. Force the game mode on join

```
scripts/build_world.py:52   "GameType": 1,             # creative
scripts/build_world.py:84   "ForceGameType": Byte(0),  # off
scripts/build_map.py:349    "gamemode adventure @a",   # only players present
```

The build switches everyone connected at that moment to adventure. `ForceGameType` is off, so anyone who joins later — by LAN, invite, or Realm — spawns in **Creative** and can fly, break the college, and skip the Parapet by air.

Set `GameType` to `2` (adventure) and `ForceGameType` to `Byte(1)`. Keep the `gamemode adventure @a` lines; they are harmless. The player must still be able to interact with lodestones and lecterns, which adventure allows.

## A3. Close the ground route under the span

The chasm has a **stone floor at ground level**. `scripts/zones/parapet.py` `_chasm()`:

```python
ctx.fill(15, -1, 12, 77, -1, 28, "stone")
ctx.fill(15, 0, 12, 77, ctx.DECK_Y - 1, 28, "air")
```

It reads as a ravine but it is a walkable corridor. Replaying the emitted commands confirms it: from `START` a player at ground level reaches the Quad and the Valley without ever climbing.

Make the chasm impassable at foot height while keeping a fall from the span fatal. One shape that works: solid from the ground to `y=1`, air above —

```python
ctx.fill(15, -1, 12, 77, 1, 28, "stone_bricks")
ctx.fill(15, 2, 12, 77, ctx.DECK_Y - 1, 28, "air")
```

That blocks walking and still leaves about 29 blocks of fall, which is past the 23-block kill line. Any shape with those two properties is acceptable. Say which you chose and why.

## A4. Gate the bond on the crossing

Even with A3, nothing proves the player crossed the span rather than finding another way in. The bond in `scripts/zones/valley.py` `live_lines()` fires purely on position:

```python
in_center = "as @a[x=~38,y=~-2,z=~112,dx=12,dy=4,dz=12,tag=!bonded] "
```

Add a `crossed` tag:

- Set it from the live pass when a player is **on the span or the roof**, at `y >= DECK_Y + 1` and within the span's x range. That is the only place the tag can be earned, so it proves the crossing.
- Require it in `in_center`: `tag=crossed,tag=!bonded`.

A player who walks around now reaches the dell and **nothing happens**. Say so in a message or not, your choice — but the bond must not fire.

## A5. Assert all of it

Extend the checks so these cannot silently return:

- `assert_walk()` in `scripts/build_map.py`: it currently asserts the player can walk from `START` to the span. Add the inverse — a walk from `START` to the Quad **must fail** at or below `y <= 1`. The orchestrator's probe for this is in the transcript; write your own.
- `scripts/test_release.py`: assert the world's experiments are off, and that the emitted live pass carries the `crossed` requirement in the bond selector.

---

# Part B — correctness, in value order

## B1. The story contradicts itself about the dragon's name

The valley says `"Say the colour, nothing more. The full name stays with you and the roll-keeper."` The Roll-keeper's form asks for the **full name**, and `docs/CANON.md` says the rider gives the roll-keeper the full name.

**Canon is right.** Fix the valley line so it and the keeper agree.

## B2. The Gauntlet does not score

In `scripts/zones/gauntlet.py`: the score is tracked on one global fake player, no timer starts or stops it, nothing reads it, and the rope penalty message fires once ever because `rope_told` is added and never cleared. Report what is true and make the rope penalty repeat correctly — clear `rope_told` when `rope_touch` clears.

Do not invent a scoring UI. Make the existing pieces honest, or remove what does nothing.

## B3. Stale text in the welcome

`welcome_lines()` still tells the player to touch the stone **in the Quad** — the lodestone moved to the valley — and the dragon line still names the **gold pad**, which is moss now. Reconcile both with what the map actually does.

## B4. Two dragons

The bond already summons one. `summon_dragon` can produce a second. Confirm and make it idempotent.

## B5. Audit-4 items

1. Cross-validate `KEEPERS[].block` in `main.js` against the lectern `setblock`s in the emitted functions. Read each side independently; do not feed the table back to itself.
2. Wrap `runKeeperForm` in error handling. `form.show` can reject on a disconnect or a busy player, and `system.run(...)` discards the promise.
3. Cancel a pending roll-call timeout when a new name is written, so two quick writes cannot leave two live callbacks.
4. Make `solid_blocks()` fail loudly on an unrecognised positional command instead of skipping it.
5. Send a line instead of returning silently when `buildOrigin()` finds no anchor.

## B6. The remaining Lows

`event.cancel` on the no-anchor lectern path; the docs name scan in `test_release.py`; `rememberOnWing` keyed on `player.id` rather than `player.name`.

---

## Success criteria

1. `python3 scripts/build_map.py` exits 0.
2. All gates pass, including `bench_static.py`.
3. The world's `beta_apis` and `gametest` are 0, and `GameType`/`ForceGameType` are adventure and on.
4. A ground-level walk from `START` to the Quad fails, and a fall from the span is still fatal.
5. The bond cannot fire without `crossed`.
6. The valley line and the Roll-keeper agree on what the dragon's name is for.

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

- Do not write outside the repo.
- Do not change `addon/behavior_pack/manifest.json`'s dependency versions. No Beta APIs.
- Do not raise the 80,000 air gate.
- Do not weaken `assert_walk` to make the new inverse pass.
- Do not put player input into a command string.
- Do not ship a person name, a dragon name, or book text. The `docs/CANON.md` denylist stays.
- Do not print, write, or commit a key.
- Do not commit or push.
