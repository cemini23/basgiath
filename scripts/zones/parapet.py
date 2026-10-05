"""Parapet. The span, the two towers, and the two climbs.

Stage range 01-12 is reserved. This module does not write stage files.
"""

STAGE_START = 1
STAGE_END = 12


def build(ctx) -> list[str]:
    """Return the Parapet commands. The world blocks stay as they are today."""
    _ground(ctx)
    _chasm(ctx)
    _tower(ctx, 2, 12, 14, 28)
    _west_climb(ctx)
    _tower(ctx, 78, 12, 90, 28)
    _east_climb(ctx)
    _span(ctx)
    return ctx.take()


def _ground(ctx) -> None:
    ctx.fill(0, -2, 0, 170, -2, 150, "stone")
    ctx.fill(0, -1, 0, 170, -1, 150, "grass_block")


def _chasm(ctx) -> None:
    """A stone ravine under the span, solid from the ground to y=1.

    The old floor was one stone layer at y=-1, so the "chasm" read as a walled
    corridor and a player walked under the span instead of across it. The
    fill now rises to y=1: a two-block step from the grass at y=-1, which a
    walker cannot climb. The deck stays at y=32, so a fall onto this floor is
    31 blocks, past the 23-block kill line.

    The open air above y=1 is not written. The shipped world is flat, so the
    space above the ground is already air, and re-emitting it was the 34,272
    fill no-op this module already removed once. The 80,000 air gate is a hard
    limit; writing it back would put the build over.
    """
    ctx.fill(15, -1, 12, 77, 1, 28, "stone_bricks")


def _tower(ctx, x0: int, z0: int, x1: int, z1: int) -> None:
    ctx.fill(x0, -1, z0, x1, ctx.DECK_Y, z1, "stone_bricks")
    ctx.fill(x0 + 1, 0, z0 + 1, x1 - 1, ctx.DECK_Y - 1, z1 - 1, "air")


def _stair(ctx, x0: int, x1: int, y: int, z: int) -> None:
    """One glowing step. x0 and x1 are the walk blocks. Curbs sit one block outside."""
    for x in range(x0, x1 + 1):
        ctx.setblock(x, y, z, "sea_lantern")
        ctx.setblock(x, y + 1, z, "air")
        ctx.setblock(x, y + 2, z, "air")
    for x in (x0 - 1, x1 + 1):
        ctx.setblock(x, y, z, "stone_bricks")
        ctx.setblock(x, y + 1, z, "sea_lantern")


def _west_climb(ctx) -> None:
    """Glowing stairs on the ground, south of the west tower, then a lit roof path."""
    for step in range(ctx.DECK_Y + 1):
        _stair(ctx, 7, 8, step, 61 - step)
    ctx.fill(6, -1, 62, 9, -1, 68, "sea_lantern")
    for z in range(ctx.SPAN_Z, 29):
        ctx.setblock(7, ctx.DECK_Y, z, "sea_lantern")
        ctx.setblock(8, ctx.DECK_Y, z, "sea_lantern")
    for x in range(7, 15):
        ctx.setblock(x, ctx.DECK_Y, ctx.SPAN_Z, "sea_lantern")
    for z in range(12, 29):
        if z == ctx.SPAN_Z:
            continue
        ctx.setblock(14, ctx.DECK_Y + 1, z, "stone_brick_wall")
        ctx.setblock(14, ctx.DECK_Y + 2, z, "stone_brick_wall")


def _stair_east(ctx, z0: int, z1: int, y: int, x: int) -> None:
    """One glowing step. z0 and z1 are the walk blocks. The stair moves east."""
    for z in range(z0, z1 + 1):
        ctx.setblock(x, y, z, "sea_lantern")
        ctx.setblock(x, y + 1, z, "air")
        ctx.setblock(x, y + 2, z, "air")
    for z in (z0 - 1, z1 + 1):
        ctx.setblock(x, y, z, "stone_bricks")
        ctx.setblock(x, y + 1, z, "sea_lantern")


def _gate(ctx, x: int) -> None:
    """A lit stone frame above the roof, with a walk-through on the span."""
    for z in (18, 23):
        ctx.fill(x, ctx.DECK_Y + 1, z, x, ctx.DECK_Y + 5, z, "stone_bricks")
        ctx.setblock(x, ctx.DECK_Y + 2, z, "sea_lantern")
    ctx.fill(x, ctx.DECK_Y + 5, 18, x, ctx.DECK_Y + 5, 23, "stone_bricks")
    ctx.setblock(x, ctx.DECK_Y + 4, 19, "sea_lantern")
    ctx.setblock(x, ctx.DECK_Y + 4, 22, "sea_lantern")


def _east_climb(ctx) -> None:
    """A gate at the end of the span, then glowing stairs east down to the quad."""
    for x in range(78, 91):
        ctx.setblock(x, ctx.DECK_Y, ctx.SPAN_Z, "sea_lantern")
        ctx.setblock(x, ctx.DECK_Y, ctx.SPAN_Z + 1, "sea_lantern")
    _gate(ctx, 78)
    _gate(ctx, 90)
    for step in range(ctx.DECK_Y + 1):
        _stair_east(ctx, ctx.SPAN_Z, ctx.SPAN_Z + 1, ctx.DECK_Y - step, 91 + step)


def _span(ctx) -> None:
    for x in range(15, 78):
        if x in (45, 46):
            continue
        if x <= 18:
            block = "sea_lantern"
        elif x in (44, 47):
            block = "polished_blackstone"
        elif (x - 15) % 4 == 0:
            block = "chiseled_stone_bricks"
        else:
            block = "stone_bricks"
        ctx.setblock(x, ctx.DECK_Y, ctx.SPAN_Z, block)
