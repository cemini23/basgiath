"""College. The Citadel group that replaces the three spruce huts.

Canon (docs/CANON.md section 3): a three-story Dragon Rotunda with a glass dome
and four doors, a keep with one arched door, a three-story dorm block with four
rows of beds and one private room, and classrooms.

Stage range 21-30 is reserved. This module does not write stage files.
Every block sits inside x=96..145 and z=80..122. The valley stays west of x=96.

Ground level in this zone is y=-1, the same as the Quad floor. The whole
group stands on one stone court at that level, so a player walks in from the
north (the quad) and from the west (the valley path) with no step.
"""

from __future__ import annotations

STAGE_START = 21
STAGE_END = 30

# Zone fence. Nothing is placed outside this box.
X_MIN, X_MAX = 96, 145
Z_MIN, Z_MAX = 80, 122

# Rotunda. Polished gray floor, stone walls, glass dome, four door gaps.
ROT_CX, ROT_CZ = 110, 98
ROT_R = 10
ROT_TOP = 7

# Keep. One arched door on the west face.
KEEP_X0, KEEP_Z0, KEEP_X1, KEEP_Z1, KEEP_TOP = 126, 100, 140, 110, 8
KEEP_DOOR_Z = 104

# Dorm block. Three stories, four bed rows, plus one private room.
DORM = (126, 84, 140, 92)
PRIVATE = (142, 87, 144, 93)
PRIVATE_DOOR_Z = 90

# Classroom shell with lecterns.
CLASS = (102, 112, 122, 120)


def build(ctx) -> list[str]:
    """Return the Citadel commands."""
    _plaza(ctx)
    _rotunda(ctx)
    _keep(ctx)
    _dorm(ctx)
    _private_room(ctx)
    _classroom(ctx)
    return ctx.take()


# --------------------------------------------------------------------------
# Rotunda


def _ring(radius: int) -> list[tuple[int, int]]:
    """A one-block-thick ring of offsets for the given radius."""
    ring = []
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            if dx * dx + dz * dz > radius * radius:
                continue
            edge = any(
                abs(dx + ox) > radius
                or abs(dz + oz) > radius
                or (dx + ox) ** 2 + (dz + oz) ** 2 > radius * radius
                for ox, oz in ((1, 0), (-1, 0), (0, 1), (0, -1))
            )
            if edge:
                ring.append((dx, dz))
    return ring


def _ring_with_gaps(radius: int, gaps: tuple[tuple[int, int, int, int], ...]) -> list[tuple[int, int]]:
    """Ring cells with any cell inside a gap rectangle dropped."""
    return [
        (dx, dz)
        for dx, dz in _ring(radius)
        if not any(gx0 <= dx <= gx1 and gz0 <= dz <= gz1 for gx0, gz0, gx1, gz1 in gaps)
    ]


def _plaza(ctx) -> None:
    """One flat stone court at the same level as the Quad floor.

    Ground level in this zone is y=-1, so the player can walk in from the
    north (the quad) and from the west (the valley path) with no step.
    """
    ctx.fill(X_MIN, -1, Z_MIN, X_MAX, -1, Z_MAX, "stone_bricks")


def _rotunda(ctx) -> None:
    """Three-story rotunda: stone walls, polished floor, glass dome, four doors.

    The north and south doors sit on the flat wall runs so a player walks
    straight through. The west door faces the valley path. The east door
    opens toward the dorm court.
    """
    x0, x1 = ROT_CX - ROT_R, ROT_CX + ROT_R
    z0, z1 = ROT_CZ - ROT_R, ROT_CZ + ROT_R

    # Door gaps in offset space. North and south are seven wide, the west
    # and east doors are three wide so the ring stays square around them.
    gaps = (
        (-3, -ROT_R, 3, -7),
        (-3, 7, 3, ROT_R),
        (-ROT_R, -1, -8, 1),
        (8, -1, ROT_R, 1),
    )
    hollow_r = ROT_R - 1
    walls = [
        (dx, dz)
        for dx, dz in _ring_with_gaps(ROT_R, gaps)
        if dx * dx + dz * dz <= hollow_r * hollow_r
    ]

    # Shell: solid cylinder, then a hollow inside it. The floor stays at y=-1.
    ctx.fill(x0, -1, z0, x1, ROT_TOP, z1, "stone_bricks")
    ctx.fill(x0 + 1, 0, z0 + 1, x1 - 1, ROT_TOP - 1, z1 - 1, "air")

    # Rebuild the ring so the doors stay square after the box hollow.
    for dx, dz in walls:
        ctx.fill(ROT_CX + dx, 0, ROT_CZ + dz, ROT_CX + dx, ROT_TOP, ROT_CZ + dz, "stone_bricks")

    # The floor is the plaza stone at y=-1. The door cuts above removed it
    # under each opening, so lay one small fill back under every door.
    for gx0, gz0, gx1, gz1 in gaps:
        ctx.fill(ROT_CX + gx0, -1, ROT_CZ + gz0, ROT_CX + gx1, -1, ROT_CZ + gz1, "smooth_stone")
        ctx.fill(ROT_CX + gx0, 0, ROT_CZ + gz0, ROT_CX + gx1, 1, ROT_CZ + gz1, "air")

    # Open the court passage south of the south door, through the old wall.
    ctx.fill(107, -1, 109, 113, -1, 112, "smooth_stone")
    ctx.fill(107, 0, 109, 113, 3, 112, "air")

    # Story floors in polished stone, with a shaft left open at the centre.
    # y=2 and y=5 leave the ground floor a full three-block doorway.
    for y in (2, 5):
        ctx.fill(x0 + 1, y, z0 + 1, x1 - 1, y, z1 - 1, "polished_andesite")
        ctx.fill(ROT_CX - 1, y, ROT_CZ - 1, ROT_CX + 1, y, ROT_CZ + 1, "air")
    ctx.fill(ROT_CX - 1, -1, ROT_CZ - 1, ROT_CX + 1, -1, ROT_CZ + 1, "polished_andesite")

    # Light on the ground floor.
    ctx.setblock(ROT_CX, 0, ROT_CZ + 4, "lantern")
    ctx.setblock(ROT_CX - 5, 0, ROT_CZ, "lantern")
    ctx.setblock(ROT_CX + 5, 0, ROT_CZ, "lantern")

    # Glass dome over the stone cap.
    for layer, radius in enumerate((9, 7, 5, 3, 2, 1)):
        for dx, dz in _ring(radius):
            ctx.setblock(ROT_CX + dx, ROT_TOP + layer, ROT_CZ + dz, "glass")
    ctx.setblock(ROT_CX, ROT_TOP + 6, ROT_CZ, "glass")

    # Four pillars between the doors, coloured like the academic wing.
    for dx, dz, block in (
        (-2, -9, "orange_wool"),
        (2, -9, "black_wool"),
        (-2, 9, "orange_wool"),
        (2, 9, "black_wool"),
    ):
        ctx.fill(ROT_CX + dx, 0, ROT_CZ + dz, ROT_CX + dx, ROT_TOP, ROT_CZ + dz, block)


# --------------------------------------------------------------------------
# Keep


def _keep(ctx) -> None:
    """A tall keep with one arched door and an armor stand on the ground floor."""
    x0, z0, x1, z1 = KEEP_X0, KEEP_Z0, KEEP_X1, KEEP_Z1
    ctx.shell(x0, -1, z0, x1, KEEP_TOP, z1, "stone_bricks")
    ctx.fill(x0 + 1, -1, z0 + 1, x1 - 1, -1, z1 - 1, "polished_andesite")

    # One arched door on the west face.
    ctx.fill(x0, -1, KEEP_DOOR_Z, x0, 1, KEEP_DOOR_Z + 1, "air")
    ctx.setblock(x0, 2, KEEP_DOOR_Z, "stone_brick_stairs")
    ctx.setblock(x0, 2, KEEP_DOOR_Z + 1, "stone_brick_stairs")
    ctx.setblock(x0, 3, KEEP_DOOR_Z, "stone_bricks")
    ctx.setblock(x0, 3, KEEP_DOOR_Z + 1, "stone_bricks")
    ctx.setblock(x0, 2, KEEP_DOOR_Z - 1, "stone_bricks")
    ctx.setblock(x0, 2, KEEP_DOOR_Z + 2, "stone_bricks")
    ctx.setblock(x0, 3, KEEP_DOOR_Z - 1, "stone_bricks")
    ctx.setblock(x0, 3, KEEP_DOOR_Z + 2, "stone_bricks")

    # Light inside so the rider can read the stand.
    ctx.setblock(x0 + 2, 2, z0 + 2, "lantern")
    ctx.setblock(x1 - 2, 2, z1 - 2, "lantern")

    # One armor stand. The name is an original line about a rider and a dragon.
    # It carries no comma: a comma inside a quoted selector name is not safe.
    # Zones do not import build_map, so the tildes are written here. Every
    # stage function runs at the build_anchor, which is the player's feet.
    ctx.add(
        'summon armor_stand "A rider kneels and the dragon decides." '
        f"~{x0 + 4} ~ ~{(z0 + z1) // 2}"
    )


# --------------------------------------------------------------------------
# Dorm block


def _dorm(ctx) -> None:
    """Three stories, four rows of red_wool beds, one door on the north face."""
    x0, z0, x1, z1 = DORM
    ctx.shell(x0, -1, z0, x1, 9, z1, "stone_bricks")
    ctx.fill(x0 + 1, -1, z0 + 1, x1 - 1, -1, z1 - 1, "polished_andesite")

    # Three stories: open floor, slab, open floor, slab, open floor.
    for y in (2, 5):
        ctx.fill(x0 + 1, y, z0 + 1, x1 - 1, y, z1 - 1, "stone_bricks")

    # Door gap on the north face, toward the quad.
    ctx.fill(x0 + 6, -1, z0, x0 + 7, 1, z0, "air")
    ctx.setblock(x0 + 5, 2, z0, "stone_brick_stairs")
    ctx.setblock(x0 + 8, 2, z0, "stone_brick_stairs")

    # A ladder shaft at the north-west corner so all three stories connect.
    ladder_x, ladder_z = x0 + 1, z0 + 1
    for y in (2, 5):
        ctx.setblock(ladder_x, y, ladder_z, "air")
        ctx.setblock(ladder_x, y - 1, ladder_z, "ladder [facing_direction=2]")
    ctx.setblock(ladder_x, -1, ladder_z, "ladder [facing_direction=2]")

    # Doorway through to the private room.
    ctx.fill(x1, -1, PRIVATE_DOOR_Z, x1, 1, PRIVATE_DOOR_Z, "air")

    # Four rows of red_wool beds.
    for z in (86, 88, 90, 92):
        for x in range(x0 + 3, x1 - 1, 2):
            ctx.setblock(x, -1, z, "red_wool")

    # Light on each landing.
    ctx.setblock(x0 + 1, 2, z0 + 3, "lantern")


def _private_room(ctx) -> None:
    """One small hollow room with a door gap, for a bonded rider."""
    x0, z0, x1, z1 = PRIVATE
    ctx.shell(x0, -1, z0, x1, 4, z1, "stone_bricks")
    ctx.fill(x0, -1, PRIVATE_DOOR_Z, x0, 1, PRIVATE_DOOR_Z, "air")
    ctx.setblock(x0 + 1, -1, z0 + 1, "red_wool")
    ctx.setblock(x0 + 1, 0, z1 - 1, "lantern")


# --------------------------------------------------------------------------
# Classroom


def _classroom(ctx) -> None:
    """A hollow classroom shell with lecterns and one door on the west face."""
    x0, z0, x1, z1 = CLASS
    ctx.shell(x0, -1, z0, x1, 5, z1, "stone_bricks")
    ctx.fill(x0 + 1, -1, z0 + 1, x1 - 1, -1, z1 - 1, "polished_andesite")
    ctx.fill(x0, -1, 116, x0, 1, 117, "air")
    ctx.setblock(x0, 2, 116, "stone_brick_stairs")
    ctx.setblock(x0, 2, 117, "stone_brick_stairs")

    lecterns = (
        (x0 + 4, z0 + 3, 2),
        (x0 + 8, z0 + 3, 2),
        (x0 + 12, z0 + 3, 2),
        (x0 + 6, z0 + 6, 3),
        (x0 + 10, z0 + 6, 3),
        (x0 + 4, z1 - 2, 4),
        (x0 + 14, z1 - 2, 4),
        (x0 + 16, z0 + 5, 1),
    )
    for x, z, facing in lecterns:
        ctx.setblock(x, 1, z, f"lectern [facing_direction={facing}]")
    ctx.setblock(x0 + 16, 2, z0 + 2, "lantern")
    ctx.setblock(x0 + 2, 2, z1 - 2, "lantern")
