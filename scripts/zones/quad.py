"""Quad. Formation. The stone court east of the span, now a walled courtyard.

Stage range 13-20 is reserved. This module does not write stage files.

The courtyard wall is 10 blocks thick and 8 blocks tall. It fills the rim of
x=96..168 by z=4..78. One opening is left on the west face at x=96..105,
z=18..26: the ground route in from the Parapet. The ring is a silhouette, not
a roof. The east descent flies over the wall at y=18..27 and lands inside, so
the gate is the ground route, not the only route.

The stone floor stays. The bleachers, the wool poles, and the bell tower stay
inside the wall line; the bleachers and the tower move inboard so the wall does
not bury them. The plaza marker at 128, 0, 40 becomes chiseled_stone_bricks.
No summoning stone is placed in this file. That stone moves to the valley.

A roll-call square of armor stands on the plaza teaches the unit shape: four
wings, three sections (Flame, Claw, Tail), three squads in a section. Six
tellraw lines run once from build(). The death roll line names no person.

ctx.DECK_Y (the span deck) and ctx.START (the west landing) sit outside this
box, so the plan only writes ctx.SPAN_Z. The gate is centered on the span path.
"""

from __future__ import annotations

STAGE_START = 13
STAGE_END = 20

# The courtyard box. The wall fills the rim of this box.
X0, X1 = 96, 168
Z0, Z1 = 4, 78
WALL = 10
WALL_TOP = 7

# The inner footprint, past the wall.
IX0, IX1 = X0 + WALL, X1 - WALL
IZ0, IZ1 = Z0 + WALL, Z1 - WALL

# The wing square on the plaza: 4 rows of wings, 9 columns of squads.
FORM_X0 = 124
FORM_Z0 = 36
WINGS = 4
SECTIONS = 3
SQUADS_IN_SECTION = 3
SECTIONS_NAMED = ("flame", "claw", "tail")

# The lines the unit hears at roll call. All original.
ROLL_CALL = (
    "Roll call. Four wings answer in this courtyard. Find your row.",
    "Each wing carries three sections: Flame, Claw, and Tail.",
    "Each section holds three squads. Nine marks stand in three groups of three.",
    "First-years hold the back two rows of the square until a name is read.",
    "Wingleaders and section leaders are third years. A rare second year may lead a squad.",
    "The scribes read the death roll. We answer for the cadets who did not live to stand here.",
)


def build(ctx) -> list[str]:
    """Return the Formation commands. Vanilla blocks only."""
    _floor(ctx)
    _wall(ctx)
    _plaza(ctx)
    _bleachers(ctx)
    _wool_poles(ctx)
    _lantern_posts(ctx)
    _bell_tower(ctx)
    _roll_call(ctx)
    return ctx.take()


def _floor(ctx) -> None:
    """The stone court floor stays. Nothing here writes below it."""
    ctx.fill(X0, -1, Z0, X1, -1, Z1, "stone_bricks")


def _wall(ctx) -> None:
    """A solid stone_bricks ring, 10 thick and 8 tall, with one west gate."""
    gate_z0 = ctx.SPAN_Z - 2
    gate_z1 = ctx.SPAN_Z + 6

    # The north and south bands span the full width, corners included.
    ctx.fill(X0, 0, Z0, X1, WALL_TOP, Z0 + WALL - 1, "stone_bricks")
    ctx.fill(X0, 0, Z1 - WALL + 1, X1, WALL_TOP, Z1, "stone_bricks")

    # The west band, split around the one opening.
    ctx.fill(X0, 0, IZ0, X0 + WALL - 1, WALL_TOP, gate_z0 - 1, "stone_bricks")
    ctx.fill(X0, 0, gate_z1 + 1, X0 + WALL - 1, WALL_TOP, IZ1, "stone_bricks")
    # The opening stays open. It is the path from the span, not a wall.
    ctx.fill(X0, 0, gate_z0, X0 + WALL - 1, WALL_TOP, gate_z1, "air")

    # The east band.
    ctx.fill(X1 - WALL + 1, 0, IZ0, X1, WALL_TOP, IZ1, "stone_bricks")


def _plaza(ctx) -> None:
    """The plaza platform. Its centre block becomes chiseled stone."""
    ctx.fill(124, 0, 36, 132, 0, 44, "stone_bricks")
    ctx.setblock(128, 0, 40, "chiseled_stone_bricks")
    for z in range(ctx.SPAN_Z, 36):
        ctx.setblock(124, -1, z, "sea_lantern")


def _bleachers(ctx) -> None:
    """Four seat rows on each inner rim, tallest against the wall."""
    for row, height in enumerate((3, 2, 1, 0)):
        ctx.fill(IX0 + 2, 0, IZ0 + row, IX1 - 2, height, IZ0 + row, "stone_bricks")
        ctx.fill(IX0 + 2, 0, IZ1 - row, IX1 - 2, height, IZ1 - row, "stone_bricks")


def _wool_poles(ctx) -> None:
    poles = (
        (122, 34, "cyan_wool"),
        (134, 34, "purple_wool"),
        (122, 46, "orange_wool"),
        (134, 46, "light_gray_wool"),
    )
    for x, z, wool in poles:
        ctx.fill(x, 0, z, x, 4, z, wool)


def _lantern_posts(ctx) -> None:
    for x in (110, 116, 140, 152):
        for z in (20, 60):
            ctx.setblock(x, 0, z, "stone_bricks")
            ctx.setblock(x, 1, z, "lantern")


def _bell_tower(ctx) -> None:
    """The bell tower moves inboard so the wall line does not bury it."""
    x0, z0 = 144, 20
    x1, z1 = x0 + 6, z0 + 6
    ctx.shell(x0, -1, z0, x1, 16, z1, "stone_bricks")
    ctx.setblock(x0 + 3, 15, z0 + 3, "bell")
    ctx.setblock(x0 + 3, 16, z0 + 3, "sea_lantern")


def _roll_call(ctx) -> None:
    """A square of armor stands on the plaza teaches the unit shape.

    Nine columns are three sections of three squads. Four rows are the wings.
    One lectern holds the roll. Every line here is original.
    """
    ctx.setblock(128, 0, 34, "chiseled_stone_bricks")
    ctx.setblock(128, 1, 34, "lectern")
    for wing in range(WINGS):
        for squad in range(SECTIONS * SQUADS_IN_SECTION):
            section = SECTIONS_NAMED[squad // SQUADS_IN_SECTION]
            name = f"wing{wing + 1}_{section}_squad{squad % SQUADS_IN_SECTION + 1}"
            x = FORM_X0 + squad
            z = FORM_Z0 + wing * 2
            ctx.add(f'summon armor_stand "{name}" ~{x} ~1 ~{z}')
    for text in ROLL_CALL:
        ctx.add('tellraw @a {"rawtext":[{"text":"' + text + '"}]}')
