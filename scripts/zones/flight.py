"""Presentation. The flight field in the box canyon south of the dorms.

Stage range 41-48 is reserved. This module does not write stage files.

Canon (`docs/CANON.md` section 5) puts Presentation on the flight field. The
squads walk a footpath through the meadow. The dragons form up a few feet back
and watch. The walk lets the dragons look, and it is not the choosing.

The canyon box runs x=100..145, z=124..148, south of the dorms. The ground is
the college floor at y=-1, so every wall rises from that level. The north side
stays open to the path from the dorms; the west, east and south sides are
stone with a stone brick cap and a stone brick course at the foot. The rim is
cut at `ctx.DECK_Y`, the same height as the span deck, so the seasonal fall
drops the full face of the south wall.

Nothing in this zone summons a dragon and nothing here offers a choice. The
six wool posts are a line for the eye. The player walks; the dragons look.
"""

STAGE_START = 41
STAGE_END = 48

# The canyon box. Nothing is placed outside it.
X_MIN, X_MAX = 100, 145
Z_MIN, Z_MAX = 124, 148

WALL = 2                            # wall thickness
FLOOR_Y = -1                        # the college ground
WALL_BLOCK = "stone"
BRICK = "stone_bricks"
DAIS_BLOCK = "smooth_stone"
WALK_BLOCK = "dirt_path"
GLASS = "light_blue_stained_glass"

# The footpath. It runs the middle of the field for ctx.SPAN_Z blocks.
WALK_X0, WALK_X1 = 121, 123
WALK_Z0 = Z_MIN + 1                 # 125; the mouth at z=124 stays clear

# The gate at the mouth: two hollow posts and one beam over the path.
GATE_Z0, GATE_Z1 = 124, 126
GATE_WEST = (117, 119)
GATE_EAST = (125, 127)
GATE_TOP = 3                        # post crown
GATE_BEAM_Y = GATE_TOP + 1
THRESHOLD_X0, THRESHOLD_X1 = 118, 126

# The dais at the south end of the walk.
DAIS_X0, DAIS_X1 = 114, 130
DAIS_Z0, DAIS_Z1 = 145, 146

# The bleachers along the west wall, four rows, facing the walk.
BLEACH_X0 = X_MIN + WALL            # 102
BLEACH_TOP = 3
BLEACH_ROWS = 4
BLEACH_Z0, BLEACH_Z1 = 126, 144

# The dragon line: six wool posts along the east wall. Colours only, no name.
POST_X = X_MAX - WALL - 2           # 141
POST_Z = (126, 130, 134, 138, 142, 146)
POST_TOP = 2
POST_WOOL = (
    "white_wool",
    "orange_wool",
    "yellow_wool",
    "lime_wool",
    "light_blue_wool",
    "purple_wool",
)

# The seasonal fall on the south wall, near the Vale corner.
FALL_X0, FALL_X1 = 105, 107
FALL_Z = Z_MAX - WALL + 1           # 147, the inner face of the south wall
SPLASH_Z0, SPLASH_Z1 = 145, 146

FLOWERS = (
    "dandelion",
    "poppy",
    "cornflower",
    "oxeye_daisy",
    "azure_bluet",
    "allium",
)


def build(ctx) -> list[str]:
    """Return the Presentation commands. Vanilla blocks only."""
    rim_y = ctx.DECK_Y
    walk_z1 = WALK_Z0 + ctx.SPAN_Z - 1
    seed = ctx.START[0] * 31 + ctx.START[2] * 17

    _walls(ctx, rim_y)
    _gate(ctx)
    _threshold(ctx)
    _walk(ctx, walk_z1)
    _bleachers(ctx)
    _dais(ctx)
    _dragon_line(ctx)
    _fall(ctx, rim_y)
    _meadow(ctx, seed, walk_z1)
    ctx.add(_walk_line())
    return ctx.take()


def _walls(ctx, rim_y: int) -> None:
    """Stone on the west, east and south sides. The north side stays open."""
    west0, west1 = X_MIN, X_MIN + WALL - 1
    east0, east1 = X_MAX - WALL + 1, X_MAX
    south0 = Z_MAX - WALL + 1
    ctx.fill(west0, FLOOR_Y, Z_MIN, west1, rim_y - 1, Z_MAX, WALL_BLOCK)
    ctx.fill(east0, FLOOR_Y, Z_MIN, east1, rim_y - 1, Z_MAX, WALL_BLOCK)
    ctx.fill(X_MIN, FLOOR_Y, south0, X_MAX, rim_y - 1, Z_MAX, WALL_BLOCK)
    # A stone brick cap, so the rim reads as a cut edge and not loose rock.
    ctx.fill(west0, rim_y, Z_MIN, west1, rim_y, Z_MAX, BRICK)
    ctx.fill(east0, rim_y, Z_MIN, east1, rim_y, Z_MAX, BRICK)
    ctx.fill(X_MIN, rim_y, south0, X_MAX, rim_y, south0, BRICK)
    # A brick course at the foot of each inner face.
    ctx.fill(west1, FLOOR_Y, Z_MIN, west1, FLOOR_Y + 1, Z_MAX, BRICK)
    ctx.fill(east0, FLOOR_Y, Z_MIN, east0, FLOOR_Y + 1, Z_MAX, BRICK)
    ctx.fill(X_MIN, FLOOR_Y, south0, X_MAX, FLOOR_Y + 1, south0, BRICK)


def _gate(ctx) -> None:
    """Two hollow posts and one beam at the mouth. The path runs under it."""
    for x0, x1 in (GATE_WEST, GATE_EAST):
        ctx.shell(x0, FLOOR_Y, GATE_Z0, x1, GATE_TOP, GATE_Z1, BRICK)
    ctx.fill(
        GATE_WEST[0],
        GATE_BEAM_Y,
        GATE_Z0,
        GATE_EAST[1],
        GATE_BEAM_Y,
        GATE_Z1,
        BRICK,
    )


def _threshold(ctx) -> None:
    """A stone lip under the gate. The mouth itself stays open."""
    ctx.fill(THRESHOLD_X0, FLOOR_Y, Z_MIN, THRESHOLD_X1, FLOOR_Y, Z_MIN, BRICK)


def _walk(ctx, walk_z1: int) -> None:
    """The walk down the middle. The squads pass; the dragons look on."""
    ctx.fill(WALK_X0, FLOOR_Y, WALK_Z0, WALK_X1, FLOOR_Y, walk_z1, WALK_BLOCK)


def _bleachers(ctx) -> None:
    """Stone brick steps along the west wall, four rows, facing the walk."""
    for row in range(BLEACH_ROWS):
        x = BLEACH_X0 + row
        ctx.fill(x, FLOOR_Y, BLEACH_Z0, x, BLEACH_TOP - row, BLEACH_Z1, BRICK)


def _dais(ctx) -> None:
    """One smooth stone dais, a single step up, a lantern at each back corner."""
    ctx.fill(DAIS_X0, 0, DAIS_Z0, DAIS_X1, 0, DAIS_Z1, DAIS_BLOCK)
    for x in (DAIS_X0, DAIS_X1):
        ctx.setblock(x, 1, DAIS_Z1, BRICK)
        ctx.setblock(x, 2, DAIS_Z1, "lantern")


def _dragon_line(ctx) -> None:
    """Six wool posts. A line for the eye, not a menu and not a summon."""
    for z, wool in zip(POST_Z, POST_WOOL):
        ctx.setblock(POST_X, FLOOR_Y, z, BRICK)
        ctx.fill(POST_X, 0, z, POST_X, POST_TOP, z, wool)


def _fall(ctx, rim_y: int) -> None:
    """The seasonal fall. Stained glass only; no water block is placed."""
    ctx.fill(FALL_X0, 0, FALL_Z, FALL_X1, rim_y - 1, FALL_Z, GLASS)
    ctx.fill(FALL_X0, rim_y, FALL_Z, FALL_X1, rim_y, FALL_Z, GLASS)
    ctx.fill(FALL_X0, FLOOR_Y, SPLASH_Z0, FALL_X1, FLOOR_Y, SPLASH_Z1, GLASS)


def _blocked(x: int, z: int, walk_z1: int) -> bool:
    """True where a structure already owns the block above the floor."""
    if WALK_X0 <= x <= WALK_X1 and WALK_Z0 <= z <= walk_z1:
        return True
    if BLEACH_X0 <= x < BLEACH_X0 + BLEACH_ROWS and BLEACH_Z0 <= z <= BLEACH_Z1:
        return True
    if DAIS_X0 <= x <= DAIS_X1 and DAIS_Z0 <= z <= DAIS_Z1:
        return True
    if GATE_WEST[0] <= x <= GATE_EAST[1] and GATE_Z0 <= z <= GATE_Z1:
        return True
    if FALL_X0 <= x <= FALL_X1 and (z == FALL_Z or SPLASH_Z0 <= z <= SPLASH_Z1):
        return True
    return abs(x - POST_X) <= 1 and any(abs(z - pz) <= 1 for pz in POST_Z)


def _meadow(ctx, seed: int, walk_z1: int) -> None:
    """Short grass and a few flowers. A fixed pattern, not random."""
    for x in range(X_MIN + WALL, X_MAX - WALL + 1):
        for z in range(Z_MIN + 1, Z_MAX - WALL + 1):
            if _blocked(x, z, walk_z1):
                continue
            roll = (x * 31 + z * 17 + seed) % 97
            if roll < 9:
                ctx.setblock(x, 0, z, "short_grass")
            elif roll == 96:
                ctx.setblock(x, 0, z, FLOWERS[(x + z) % len(FLOWERS)])


def _walk_line() -> str:
    """The one line for the walk. Original text, no book line and no name."""
    text = (
        "Keep to the middle path. The dragons watch. "
        "This walk is for them to look, and it is not the choosing."
    )
    return f'tellraw @a {{"rawtext":[{{"text":"{text}"}}]}}'
