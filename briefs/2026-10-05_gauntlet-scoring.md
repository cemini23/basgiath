# Real Gauntlet scoring

## WorkDir

`/Users/claudiobarone/Projects/dragon-rider-map`

## The problem

`scripts/zones/gauntlet.py` `live_lines()` adds a flat 30 to **one global fake player** on every rope grab:

```python
ANCHOR + f"as @a[{box},tag=!rope_cool] run scoreboard players add #gauntlet map_state 30"
```

Nothing starts a clock, nothing stops it, and **no command reads `#gauntlet`**. The module docstring now admits the "Gauntlet timekeeper" armor stand is scenery. The course is the one beat the story makes you earn, and it does not score.

Build it for real.

## Design

### The clock

Add a tick counter on the existing `map_state` objective in `live_lines()`:

```
scoreboard players add #clock map_state 1
```

### Objectives

Create them once, at build time, in `scripts/build_map.py` `build_text()` beside the existing `scoreboard objectives add map_state dummy`:

- `gate_time` — the cadet's elapsed ticks, live
- `gate_start` — the tick the run began
- `gate_pen` — accumulated rope penalty, in ticks
- `gate_best` — the cadet's best run, in ticks

Tags, not objectives: `gate_run` (on the course now) and `gate_done` (has finished at least once).

### Down the course

Two zones derived from the existing geometry so they cannot drift — do not write new numbers by hand:

- **Start** — `BANDS[0]`, the base of the cliff, at the full `X0..X1` width.
- **Summit** — `BANDS[SUMMIT]`, the top band.

Start, when a player enters the base and is not already running:

```
as @a[<start box>,tag=!gate_run] run tag @s add gate_run
as @a[<start box>,tag=!gate_run] run tag @s remove gate_done
as @a[<start box>] run scoreboard players operation @s gate_start = #clock map_state
as @a[<start box>] run scoreboard players set @s gate_pen 0
```

Each tick, for a cadet on the course:

```
as @a[tag=gate_run] run scoreboard players operation @s gate_time = #clock map_state
as @a[tag=gate_run] run scoreboard players operation @s gate_time -= @s gate_start
as @a[tag=gate_run] run scoreboard players operation @s gate_time += @s gate_pen
```

Finish, on entering the summit with `gate_run`:

- remove `gate_run`, add `gate_done`
- if `gate_best` is 0, or `gate_time` is less than `gate_best`, copy `gate_time` into `gate_best`
- announce the time

Three operations per running cadet per tick. There is normally one. It is affordable.

### The rope penalty, per cadet

Replace the global add:

```
as @a[<rope box>,tag=!rope_cool] run scoreboard players add @s gate_pen 600
```

600 ticks is 30 seconds, matching the line the player already sees. Keep the `rope_cool`/`rope_touch`/`rope_told` behaviour exactly as it is — it was just fixed so the warning repeats.

### Showing it

- `scoreboard objectives setdisplay sidebar gate_time` once at build time. A sidebar is the one way Bedrock shows a live number without a client mod.
- For the finish line, use the score component in `titleraw`:

```
titleraw @a {"rawtext":[{"selector":"@s"},{"text":" finished the Gauntlet in "},{"score":{"name":"@s","objective":"gate_time"}},{"text":" ticks."}]}
```

**Verify that first.** If Bedrock rejects the `score` component, the command logs an error. Fall back to a plain line — the sidebar still carries the number. Do not ship a command you have not seen accepted.

### The timekeeper

Update the module docstring: the armor stand is still scenery, the scoreboard is the stopwatch. Do not try to write a time into an entity's nametag from a function.

### Delete what is dead

`#gauntlet` on `map_state` is no longer read by anything once this lands. Remove it rather than leaving a second, contradictory counter.

## Verification that actually tests it

`scripts/bench_bds.sh` never runs the live pass, which is why the tick path has never been proven. Add a real probe:

1. After the stage functions run, call the live function several times, for example
   `send "function basgiath/live"` three times with a pause.
2. Fail the run if the log gains any command error from those calls. A malformed scoreboard or `titraw` line surfaces there and nowhere else.

This is the only check in the project that would catch a bad command inside the live pass. It is worth having.

## Tests

`scripts/test_release.py`, against the emitted live function:

- every objective above is created
- the rope penalty is 600 and applies to `@s`, not a fake player
- `#gauntlet` is gone
- the start and summit boxes are derived, not hand-written numbers
- the score component appears, or the documented fallback does

`scripts/bench_static.py`: prove the start and summit boxes lie inside the cliff footprint, with a mutation that moves one outside and asserts a failure.

## Success criteria

1. `python3 scripts/build_map.py` exits 0.
2. All gates pass.
3. A cadet who climbs the cliff gets a recorded time; a cadet who grabs a rope is 30 seconds slower.
4. The live pass runs clean on the Bedrock server, with no command error in the log.
5. `#gauntlet` no longer exists.

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

- Do not write outside `/Users/claudiobarone/Projects/dragon-rider-map`. Never touch `~/.pyenv`, `~/.local`, `~/.cemini`, or any home dotfile.
- Do not invent a client-side UI. Functions and the sidebar only.
- Do not change the rope detection behaviour that was just fixed.
- Do not ship a `titleraw` component you have not seen accepted in a server log.
- Do not change `addon/behavior_pack/manifest.json`. No Beta APIs.
- Do not make `solid_blocks()` raise on a `scoreboard`, `tag`, `execute`, or `titleraw` line — it raises on unparsed **positional** commands only. A non-positional line must still be skipped.
- Do not print, write, or commit a key.
- Do not commit or push.
