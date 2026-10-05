"""Gauntlet. The stone cliff, five switchbacks, and six obstacles.

Stage range 31-40 is reserved. This module does not write stage files.
The integrator calls build(ctx) once and appends live_lines() to the tick.

The strip east of the dorms is a stepped cliff. Each terrace is one
switchback leg, and every leg sits one turn higher than the one before it.
The six obstacles sit on the legs in canon order. Chain ropes hang off the
open north edge.

Scoring is real now. The `#clock map_state` counter in live_lines() is the
stopwatch and it runs every tick. A cadet who steps onto the base of the
cliff earns the `gate_run` tag, `gate_start` holds the clock at that tick, and
`gate_time` is recomputed every tick as `clock - gate_start + gate_pen`. A
cadet who reaches the summit banks the run in `gate_best`. Each fresh rope
grab adds 600 ticks (30 seconds) to that cadet's own `gate_pen`, so the
penalty follows the player instead of a fake player. `scoreboard objectives
setdisplay sidebar gate_time` shows the live number. The "Gauntlet timekeeper"
armor stand is still scenery; the scoreboard is the stopwatch, and a function
cannot write a time into an entity nametag.

Canon: docs/CANON.md section 4. Interface: scripts/zones/README.md.
"""

STAGE_START = 31
STAGE_END = 40

# Every live line hangs from the anchor that build_map.py summons.
ANCHOR = 'execute as @e[type=armor_stand,name="build_anchor",c=1] at @s '

# The cliff fence. x=146 to 168, z=80 to 140, east of the dorms.
X0 = 146
X1 = 168

# (z0, z1, floor). floor is the y of the top solid block of that terrace.
# Index 0 is the approach, 1 to 6 are the legs, 7 is the summit.
BANDS = (
    (80, 81, 0),  # approach from the college
    (82, 84, 1),  # leg one, heads east
    (85, 88, 5),  # leg two, heads west
    (89, 92, 9),  # leg three, heads east
    (93, 96, 13),  # leg four, heads west
    (97, 100, 17),  # leg five, heads east
    (101, 104, 21),  # leg six, heads west
    (105, 140, 25),  # summit
)

LEG_FIRST = 1
LEG_LAST = 6
SUMMIT = 7

# A rope every six blocks along each leg.
ROPE_XS = (148, 154, 160)
# A rope starts three above the lower floor and ends three above the upper
# floor, so a walker passes under it and only a faller grabs it.
ROPE_LIFT = 3

# The two scoring zones. Both are read straight off BANDS, so a change to the
# cliff moves the zones with it and no coordinate is written by hand twice.
# A band carries the y of its top solid block, so a body standing on that
# terrace has its feet one above the floor.
START_BAND = 0
SUMMIT_BAND = SUMMIT


def start_box() -> tuple[int, int, int, int, int, int]:
    """The full-width base of the cliff, at body height. BANDS[0]."""
    z0, z1, floor = BANDS[START_BAND]
    return (X0, floor + 1, z0, X1, floor + 1, z1)


def summit_box() -> tuple[int, int, int, int, int, int]:
    """The full-width top band, at body height. BANDS[SUMMIT]."""
    z0, z1, floor = BANDS[SUMMIT_BAND]
    return (X0, floor + 1, z0, X1, floor + 1, z1)


def cliff_footprint() -> set[tuple[int, int]]:
    """Every (x, z) cell the cliff terraces stand on.

    The scoring zones must sit inside this. The bench proves it and proves a
    mutation that slides a zone off the cliff fails.
    """
    return {
        (x, z)
        for z0, z1, _ in BANDS
        for z in range(z0, z1 + 1)
        for x in range(X0, X1 + 1)
    }


def _box_selector(box: tuple[int, int, int, int, int, int]) -> str:
    x0, y0, z0, x1, y1, z1 = box
    return (
        f"x=~{x0},y=~{y0},z=~{z0},"
        f"dx={x1 - x0 + 1},dy={y1 - y0 + 1},dz={z1 - z0 + 1}"
    )


def build(ctx) -> list[str]:
    """Return the Gauntlet commands. The cliff rises one terrace at a time."""
    _check(ctx)
    _cliff(ctx)
    _walkways(ctx)
    _turns(ctx)
    _log(ctx)
    _pillars(ctx)
    _ring(ctx)
    _cobbles(ctx)
    _chimney(ctx)
    _ramp(ctx)
    _ropes(ctx)
    _summit(ctx)
    return ctx.take()


def live_lines() -> list[str]:
    """Tick commands. Each line includes execute-at-anchor. The integrator appends them later.

    The `#clock map_state` line is the stopwatch. It runs first, so a tick of
    the live function advances it by exactly one. Every gate_* line below reads
    that clock. None of them places a block, so `solid_blocks()` never sees
    them.
    """
    lines = [ANCHOR + "run scoreboard players add #clock map_state 1"]
    # The start. A cadet who steps onto the base of the cliff and is not
    # already on the course starts the clock: gate_start is the clock now, the
    # rope penalty is wiped, and gate_done is cleared so a second run can beat
    # the first. The tag line must come first so the box that follows can see
    # gate_run on a cadet who just earned it in this same tick.
    start = _box_selector(start_box())
    lines.append(ANCHOR + f"as @a[{start},tag=!gate_run] run tag @s add gate_run")
    lines.append(ANCHOR + f"as @a[{start},tag=!gate_run] run tag @s remove gate_done")
    lines.append(
        ANCHOR
        + f"as @a[{start}] run scoreboard players operation @s gate_start = #clock map_state"
    )
    lines.append(
        ANCHOR + f"as @a[{start}] run scoreboard players set @s gate_pen 0"
    )
    # The run. Three operations per cadet on the course, then the rope penalty
    # for a fresh grab. There is normally one cadet.
    lines.append(
        ANCHOR
        + "as @a[tag=gate_run] run scoreboard players operation @s gate_time = #clock map_state"
    )
    lines.append(
        ANCHOR
        + "as @a[tag=gate_run] run scoreboard players operation @s gate_time -= @s gate_start"
    )
    lines.append(
        ANCHOR
        + "as @a[tag=gate_run] run scoreboard players operation @s gate_time += @s gate_pen"
    )
    # Seconds, for anyone reading a screen. The clock stays in ticks so the
    # rope penalty keeps its resolution; this is only the display unit.
    lines.append(
        ANCHOR
        + "as @a[tag=gate_run] run scoreboard players operation @s gate_sec = @s gate_time"
    )
    lines.append(
        ANCHOR
        + "as @a[tag=gate_run] run scoreboard players operation @s gate_sec /= #twenty map_state"
    )
    # The finish. Entering the top band while on the course stops the clock.
    # gate_best is a running personal best. The first sentence forces an
    # unset or zero gate_best down so the compare has a real number, then
    # `operation ... <` keeps the smaller of the two. gate_pen was folded
    # into gate_time on the lines above, so the banked run carries its rope
    # penalty. Every guard is an `if score`/`unless score`, never a nested
    # execute, so one bad line cannot take the whole tick down.
    summit = _box_selector(summit_box())
    finish = f"as @a[{summit},tag=gate_run]"
    lines.append(ANCHOR + f"{finish} run tag @s remove gate_run")
    lines.append(ANCHOR + f"{finish} run tag @s add gate_done")
    # A missing score is 0 to `operation` and to an `if score`, but not to a
    # selector `matches 0..`, so normalise first.
    lines.append(
        ANCHOR
        + f"{finish} unless score @s gate_best matches 0.. run scoreboard players set @s gate_best 0"
    )
    lines.append(
        ANCHOR
        + f"{finish} if score @s gate_best matches 0 run scoreboard players operation @s gate_best = @s gate_time"
    )
    lines.append(
        ANCHOR
        + f"{finish} if score @s gate_best matches 1.. run scoreboard players operation @s gate_best < @s gate_time"
    )
    # The time, inline. The `titleraw` score component used to be withheld
    # because no server had accepted it; the bench's component probe now runs
    # this exact shape against the anchor stand on every run, so it ships.
    lines.append(
        ANCHOR
        + f"{finish} run titleraw @s "
        + '{"rawtext":[{"text":"Gauntlet complete. Your time: "},'
        + '{"score":{"name":"@s","objective":"gate_sec"}},'
        + '{"text":" seconds."}]}'
    )
    for x, y, z, height in _rope_specs():
        box = f"x=~{x},y=~{y},z=~{z},dx=1,dy={height},dz=1"
        # The penalty lands on the cadet who grabbed the rope, not on a fake
        # player: 600 ticks is the 30 seconds the warning line already says.
        lines.append(
            ANCHOR
            + f"as @a[{box},tag=!rope_cool] run scoreboard players add @s gate_pen 600"
        )
        lines.append(ANCHOR + f"run tag @a[{box}] add rope_touch")
    lines.append(ANCHOR + "run tag @a[tag=rope_touch] add rope_cool")
    lines.append(ANCHOR + "run tag @a[tag=!rope_touch] remove rope_cool")
    # rope_told used to be added and never cleared, so the warning fired once
    # ever and never again. Clear it with rope_touch so a fresh grab warns
    # again; a player who holds the same rope stays quiet.
    lines.append(ANCHOR + "run tag @a[tag=!rope_touch] remove rope_told")
    lines.append(
        ANCHOR
        + "as @a[tag=rope_touch,tag=!rope_told] run titleraw @s actionbar "
        + '{"rawtext":[{"text":"You grabbed a rope. The run adds 30 seconds."}]}'
    )
    lines.append(ANCHOR + "run tag @a[tag=rope_touch] add rope_told")
    # The log at ~152 is static because a real spin needs an entity. A two
    # frame puff at each end of the bar suggests the roll instead.
    lines.append(ANCHOR + "run scoreboard players add #spinline map_state 1")
    lines.append(
        ANCHOR
        + "if score #spinline map_state matches 10.. run scoreboard players set #spinline map_state 0"
    )
    lines.append(
        ANCHOR + "run particle minecraft:basic_smoke_particle ~152 ~3 ~83"
    )
    lines.append(
        ANCHOR
        + "if score #spinline map_state matches 5 run particle minecraft:basic_smoke_particle ~152 ~3 ~82"
    )
    return lines


def _rope_specs() -> list[tuple[int, int, int, int]]:
    """(x, y0, z, height) for each rope column, top to bottom beside the path."""
    specs = []
    for index in range(LEG_FIRST, LEG_LAST + 1):
        z0, _, floor = BANDS[index]
        lower = BANDS[index - 1][2]
        y0 = lower + ROPE_LIFT
        height = floor + ROPE_LIFT - y0 + 1
        for x in ROPE_XS:
            specs.append((x, y0, z0 - 1, height))
    return specs


def _check(ctx) -> None:
    """Read the driver constants and keep the cliff in its own corner."""
    sx, _, _ = ctx.START
    if X0 <= sx:
        raise ValueError("the Gauntlet must sit east of the build origin")
    if BANDS[0][0] <= ctx.SPAN_Z:
        raise ValueError("the Gauntlet must start south of the Parapet span")
    if BANDS[SUMMIT][2] >= ctx.DECK_Y:
        raise ValueError("the Gauntlet summit must stay below the Parapet deck")


def _cliff(ctx) -> None:
    """A stepped stone cliff. Each band is a terrace that rises to the south."""
    base = ctx.START[1]
    for z0, z1, floor in BANDS:
        ctx.fill(X0, base, z0, X1, floor, z1, "stone")
    # Rough the exposed riser face of every leg with cobblestone.
    for index in range(LEG_FIRST, SUMMIT + 1):
        z0, _, floor = BANDS[index]
        lower = BANDS[index - 1][2]
        ctx.fill(X0, lower + 1, z0, X1, floor, z0, "cobblestone")


def _walkways(ctx) -> None:
    """A stone-brick walking strip along the north side of every terrace."""
    for index in range(LEG_FIRST, SUMMIT + 1):
        z0, _, floor = BANDS[index]
        ctx.fill(147, floor, z0, 166, floor, z0 + 2, "stone_bricks")
    ctx.fill(X0, 0, 80, X1, 0, 81, "stone_bricks")
    ctx.fill(X0, 25, 105, 150, 25, 140, "stone_bricks")


def _stairs(ctx, xs, z0, z1, base) -> None:
    """Four one-block steps that climb from base to base+4 along xs."""
    for step, x in enumerate(xs):
        ctx.fill(x, base + 1, z0, x, base + 1 + step, z1, "stone_bricks")


def _turns(ctx) -> None:
    """Turns one to four. Each one reverses the run and adds four blocks."""
    _stairs(ctx, (161, 162, 163, 164), 82, 84, 1)
    _stairs(ctx, (151, 150, 149, 148), 85, 88, 5)
    _stairs(ctx, (161, 162, 163, 164), 89, 92, 9)
    _stairs(ctx, (151, 150, 149, 148), 93, 96, 13)


def _log(ctx) -> None:
    """Obstacle one. A horizontal oak log across the first leg. Jump it."""
    ctx.fill(152, 2, 82, 152, 2, 84, "oak_wood")


def _pillars(ctx) -> None:
    """Obstacle two. Granite pillars of rising height on the second leg."""
    for x, height in ((159, 1), (157, 2), (155, 3), (153, 4)):
        ctx.fill(x, 6, 85, x, 5 + height, 88, "granite")


def _ring(ctx) -> None:
    """Obstacle three. A stone ring with one air gap on the third leg."""
    x = 157
    ctx.fill(x, 10, 89, x, 10, 92, "stone_bricks")  # step onto this bar
    ctx.fill(x, 14, 89, x, 14, 92, "stone_bricks")  # top of the ring
    ctx.fill(x, 11, 89, x, 13, 89, "stone_bricks")  # west side
    ctx.fill(x, 11, 92, x, 13, 92, "stone_bricks")  # east side
    ctx.setblock(x, 14, 91, "air")  # the one air gap


def _cobbles(ctx) -> None:
    """Obstacle four. Cobblestone clusters to jump on, fourth leg."""
    ctx.fill(160, 14, 93, 161, 14, 96, "cobblestone")
    ctx.fill(157, 14, 93, 158, 15, 96, "cobblestone")
    ctx.fill(154, 14, 93, 155, 14, 96, "cobblestone")
    ctx.setblock(162, 14, 94, "cobblestone")
    ctx.setblock(152, 14, 95, "cobblestone")


def _chimney(ctx) -> None:
    """Obstacle five and turn five. A 1-block chimney with ladders.

    The player walks into the base, climbs the ladder, and steps off the
    top onto the sixth leg. The climb reverses the run, so it is the turn.
    """
    ctx.fill(161, 18, 97, 164, 21, 100, "stone_bricks")
    ctx.fill(162, 18, 98, 162, 21, 98, "air")
    ctx.fill(161, 18, 98, 161, 19, 98, "air")
    for y in range(18, 22):
        ctx.setblock(162, y, 98, "ladder")


def _ramp(ctx) -> None:
    """Obstacle six. An oak stair ramp from the sixth leg to the summit."""
    for step, x in enumerate((151, 150, 149, 148)):
        top = 22 + step
        if top - 1 >= 22:
            ctx.fill(x, 22, 101, x, top - 1, 104, "oak_planks")
        ctx.fill(x, top, 101, x, top, 104, "oak_stairs")


def _ropes(ctx) -> None:
    """A chain rope every six blocks beside each leg."""
    for x, y0, z, height in _rope_specs():
        ctx.fill(x, y0, z, x, y0 + height - 1, z, "chain")


def _summit(ctx) -> None:
    """The top landing, a low parapet, and the timekeeper post.

    The stand is a marker for the eye. It holds no timer and reads no score:
    the stopwatch is the `#clock`/`gate_*` scoreboard in live_lines(). A
    function cannot write a time into an entity's nametag.
    """
    ctx.fill(X0, 26, 140, X1, 26, 140, "stone_bricks")
    ctx.fill(X1, 26, 105, X1, 26, 140, "stone_bricks")
    ctx.shell(163, 26, 108, 167, 30, 112, "stone_bricks")
    ctx.setblock(163, 27, 110, "air")
    ctx.setblock(163, 28, 110, "air")
    ctx.setblock(165, 31, 110, "lantern")
    ctx.add('summon armor_stand "Gauntlet timekeeper" ~165 ~27 ~110')
