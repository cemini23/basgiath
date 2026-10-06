# Functions

`/function basgiath/build` raises the college around an armor stand named `build_anchor`.

The stand is the origin. Every later command is relative to it. The build stays at your feet. The screen says "Building" at once. It places one stone under the stand, then gives that stand invisibility and resistance. The stone keeps the stand from falling. The same command places every stage. About 15 seconds later the game moves you onto the plaza for a few seconds, places the stairs, then returns you to the start. Close chat. Do not walk until the screen says "Welcome, candidate".

`/function basgiath/summon_dragon` summons `dragon_rider:dragon` on the valley pad.

The script runs `basgiath/tick` every tick. After the build, that tick runs `basgiath/live` for wind, checkpoints, and the storm. A fall from the span is fatal. You respawn on the ground path until you reach the east tower.

The Gauntlet is scored. Step onto the base of the cliff to start the clock; the sidebar shows `gate_time` in ticks. Every fresh rope grab adds 600 ticks (30 seconds) to that cadet's own penalty. Reaching the summit stops the clock, announces the finish, and keeps the best run in `gate_best`. The armor stand on the summit is scenery; the scoreboard is the stopwatch.

`/function basgiath/run_start` starts a timed run, and `/function basgiath/run_stop` ends it.

A run puts the tag `timed_run` on you, zeroes `run_tick` and `run_sec`, and puts the seconds on your action bar every tick. Build the college first: `run_start` writes scores the build creates, so the clock needs the build to have run. The flight readout stands down while the tag is set, because both write the action bar.

Do not run the old placeholder functions. They are gone. Coordinates live in `scripts/build_map.py`.
