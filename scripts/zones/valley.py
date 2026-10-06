"""Valley. The Threshing dell southwest of the Quad.

Stage range 49-60 is reserved. This module does not write stage files.

The land is a shallow bowl: the floor sits at y=-2 so the dell reads one block
below the college ground. Squat oaks ring the rim, wildflowers and short grass
run across the slopes, and the middle stays open. A 3 by 3 moss pad sits at
x=42..44, z=116..118. The Roll-keeper stands at x=50, y=-1, z=124, with the
roll lectern at x=50, y=-1, z=123. The rider gives the dragon's full name at
that lectern; the script writes it on the rider, never in a command.

`live_lines()` holds the Threshing event. The integrator appends those lines to
`basgiath/live.mcfunction`. They are not called from here.
"""

STAGE_START = 49
STAGE_END = 60

# The dell footprint.
X0, X1 = 16, 70
Z0, Z1 = 94, 140

# Open ground in the middle. No tree and no ground cover goes here.
OPEN_X0, OPEN_X1 = 36, 54
OPEN_Z0, OPEN_Z1 = 110, 126

# The clear landing pad. The old summon still aims at 43, -1, 117.
PAD_X0, PAD_X1 = 42, 44
PAD_Z0, PAD_Z1 = 116, 118

# The courtyard agent drops a lodestone here. Keep it free of trees.
LODESTONE_X0, LODESTONE_X1 = 48, 52
LODESTONE_Z0, LODESTONE_Z1 = 128, 132

# The Roll-keeper post.
KEEPER = (50, -1, 124)

# The Parapet span, anchor-relative. The crossing tag is earned on the span
# or the tower roof: feet at DECK_Y + 1, inside the span's x range. That is the
# only place it can be earned, so holding it proves the crossing.
CROSSED_X0, CROSSED_X1 = 15, 77
CROSSED_Y = 33
CROSSED_Z0, CROSSED_Z1 = 12, 28
CROSSED_BOX = (
    f"x=~{CROSSED_X0},y=~{CROSSED_Y},z=~{CROSSED_Z0},"
    f"dx={CROSSED_X1 - CROSSED_X0},dy=8,dz={CROSSED_Z1 - CROSSED_Z0}"
)

ANCHOR = 'execute as @e[type=armor_stand,name="build_anchor",c=1] at @s '

# Squat oaks. Bands ring the rim and run south; the middle stays open.
TREES = (
    # North rim, two rows.
    (19, 97), (26, 99), (33, 97), (40, 99), (47, 97), (54, 99), (61, 97), (68, 99),
    (22, 105), (36, 105), (50, 105), (64, 105),
    # West flank.
    (18, 114), (20, 122), (18, 130), (21, 138),
    # East flank.
    (68, 112), (66, 120), (69, 129), (67, 137),
    # Greenery running south.
    (24, 133), (31, 136), (38, 134), (45, 137), (58, 133), (65, 137),
    (28, 139), (42, 139), (56, 139),
)

GROUND = (
    "short_grass",
    "short_grass",
    "short_grass",
    "dandelion",
    "poppy",
    "cornflower",
    "oxeye_daisy",
    "azure_bluet",
    "allium",
    "lily_of_the_valley",
)


def build(ctx) -> list[str]:
    """Return the Threshing dell commands. Vanilla blocks only."""
    _floor(ctx)
    _trees(ctx)
    _ground_cover(ctx)
    _keeper(ctx)
    return ctx.take()


def _floor(ctx) -> None:
    """One bowl floor at y=-2. Clearing y=-1 opens the dell one step down."""
    ctx.fill(X0, -2, Z0, X1, -2, Z1, "grass_block")
    ctx.fill(X0, -1, Z0, X1, -1, Z1, "air")
    # The landing pad is moss, not gold. A cadet stands on it.
    ctx.fill(PAD_X0, -2, PAD_Z0, PAD_X1, -2, PAD_Z1, "moss_block")


def _tree(ctx, x: int, z: int) -> None:
    """One squat oak. Trunk is three tall, then a flat canopy and a top cross."""
    ctx.fill(x, -1, z, x, 1, z, "oak_log")
    ctx.fill(x - 1, 2, z - 1, x + 1, 2, z + 1, "oak_leaves")
    ctx.fill(x - 1, 3, z, x + 1, 3, z, "oak_leaves")
    ctx.fill(x, 3, z - 1, x, 3, z + 1, "oak_leaves")


def _trees(ctx) -> None:
    for x, z in TREES:
        _tree(ctx, x, z)


def _blocked(x: int, z: int) -> bool:
    """True where a tree trunk or a reserved box forbids ground cover."""
    if any(tx == x and tz == z for tx, tz in TREES):
        return True
    if OPEN_X0 - 1 <= x <= OPEN_X1 + 1 and OPEN_Z0 - 1 <= z <= OPEN_Z1 + 1:
        return True
    if LODESTONE_X0 <= x <= LODESTONE_X1 and LODESTONE_Z0 <= z <= LODESTONE_Z1:
        return True
    kx, _, kz = KEEPER
    if kx - 1 <= x <= kx + 1 and kz - 1 <= z <= kz + 1:
        return True
    return False


def _ground_cover(ctx) -> None:
    """Short grass and wildflowers on the slopes. A fixed pattern, not random."""
    for x in range(X0 + 1, X1):
        for z in range(Z0 + 1, Z1):
            if _blocked(x, z):
                continue
            if (x * 31 + z * 17) % 29 != 0:
                continue
            ctx.setblock(x, -1, z, GROUND[(x + z) % len(GROUND)])


def _keeper(ctx) -> None:
    """The roll-keeper waits on a stone at the south edge of the open ground.

    One lectern stands one block north of the stand, on the open dell floor.
    The keep of the roll is here: the rider gives the dragon's full name and it
    is written on the rider alone. The armor stand does not move.
    """
    kx, ky, kz = KEEPER
    ctx.setblock(kx, -2, kz, "stone_bricks")
    ctx.add(f'summon armor_stand "Roll-keeper" ~{kx} ~{ky} ~{kz}')
    ctx.setblock(kx, ky, kz - 1, "lectern")


def _say(text: str) -> str:
    return f'tellraw @s {{"rawtext":[{{"text":"{text}"}}]}}'


def live_lines() -> list[str]:
    """Commands that run every tick. Each line already includes execute-at-anchor."""
    # The bond is gated on the crossing. A player who walks to the dell without
    # crossing the span never earns the tag, so the bond below cannot fire.
    in_center = (
        "as @a[x=~38,y=~-2,z=~112,dx=12,dy=4,dz=12,tag=crossed,tag=!bonded] "
    )
    fresh = "as @a[tag=bonded,tag=!bondcall] "
    on_pad = (
        "as @a[x=~42,y=~-2,z=~116,dx=2,dy=3,dz=2,tag=trial,tag=!flew] "
    )
    at_keeper = (
        "as @a[x=~48,y=~-2,z=~122,dx=4,dy=3,dz=4,tag=flew,tag=!named] "
    )
    lines = [
        # 0. The crossing. Earned on the span or the roof, never on the ground.
        ANCHOR + f"as @a[{CROSSED_BOX}] run tag @s add crossed",
        # 1. A dragon chooses the player. The player does not choose the dragon.
        ANCHOR + in_center + "run tag @s add bonded",
        ANCHOR + fresh + "at @s run summon dragon_rider:dragon ~1 ~ ~",
        ANCHOR + fresh + "run scoreboard players set bg_bond map_state 1",
        ANCHOR
        + fresh
        + "run "
        + _say(
            "A dragon has chosen you. You did not choose it. Stand still and let it look."
        ),
        ANCHOR + fresh + "run tag @s add bondcall",
        # 2. The relic.
        ANCHOR
        + "as @a[tag=bondcall,tag=!relic] run "
        + _say("A relic mark burns onto your arm, shaped like the one that chose you."),
        ANCHOR + "as @a[tag=bondcall,tag=!relic] run tag @s add relic",
        # 3. The flight trial.
        ANCHOR
        + "as @a[tag=relic,tag=!trial] run "
        + _say("Hold your seat. The dragon will fly and turn. Do not let go."),
        ANCHOR + "as @a[tag=relic,tag=!trial] run tag @s add trial",
        # 4. The landing pad.
        ANCHOR
        + on_pad
        + "run "
        + _say("You held. Walk south to the roll-keeper and give the full name."),
        ANCHOR + on_pad + "run tag @s add flew",
        # 5. The roll-keeper. The rider gives the dragon's full name, and the
        # keeper is the only one who hears it. docs/CANON.md says the same.
        ANCHOR
        + at_keeper
        + "run "
        + _say(
            "Give the keeper the full name, nothing held back. Only you and the keeper will know it."
        ),
        ANCHOR + at_keeper + "run tag @s add named",
    ]
    return lines
