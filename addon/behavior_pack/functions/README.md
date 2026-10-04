# Functions

`/function basgiath/build` raises the college around an armor stand named `build_anchor`.

The stand is the origin. Every later command is relative to it. The build places one stone under the stand, then gives that stand invisibility and resistance. The stone keeps the stand from falling. The build runs one stage per tick.

`/function basgiath/summon_dragon` summons `dragon_rider:dragon` on the valley pad.

`functions/tick.json` runs `basgiath/tick`. After the build, that tick runs `basgiath/live` for wind, checkpoints, and the storm. A fall from the span is fatal. You respawn on the ground path until you reach the east tower.

Do not run the old placeholder functions. They are gone. Coordinates live in `scripts/build_map.py`.
