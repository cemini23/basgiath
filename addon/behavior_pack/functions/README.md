# Functions

`/function basgiath/build` raises the college around an armor stand named `build_anchor`.

The stand is the origin. Every later command is relative to it. The build runs one stage per tick.

`/function basgiath/summon_dragon` summons `dragon_rider:dragon` on the valley pad.

`functions/tick.json` runs `basgiath/tick`. After the build, that tick runs `basgiath/live` for wind, checkpoints, chasm rescue, and the storm.

Do not run the old placeholder functions. They are gone. Coordinates live in `scripts/build_map.py`.
