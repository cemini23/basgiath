"""Signet. The post-bond form stone in the valley.

Stage range 61-64 is reserved. This module does not write stage files.

Canon puts the signet weeks after the bond, not on day one at the plaza.
Threshing sets the bond. This zone only places the stone the form reads
once a dragon has chosen the rider. The plaza lodestone stays as it is;
``addon/behavior_pack/scripts/main.js`` owns the gate.
"""

STAGE_START = 61
STAGE_END = 64


def build(ctx) -> list[str]:
    """Return the signet commands. Place the stone and clear the space above."""
    ctx.setblock(50, -1, 130, "lodestone")
    ctx.setblock(50, 0, 130, "air")
    return ctx.take()
