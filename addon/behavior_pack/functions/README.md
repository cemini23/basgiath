# Parapet functions

These commands use placeholder coordinates. Build the span first, then replace the numbers below.

The span in these files runs along +X at about y=80, z=0, from x=0 to x=60. Wind pushes toward +Z.

## How to run them

1. Place a repeating command block next to the span. Set it to Always Active. Command: `function parapet_wind`
2. Place a pressure plate at each end, on top of an impulse command block.
3. Start plate command: `function parapet_checkpoint_a`
4. Far-end plate command: `function parapet_checkpoint_b`

Run the wind function every tick only after you lower the push. A push of 0.15 blocks per tick is a hard shove.

## Numbers to replace

### `parapet_wind.mcfunction`

Both commands use the same box. Replace each copy.

| Token | Value | Meaning |
| --- | --- | --- |
| `x` | 0 | West end of the span |
| `y` | 80 | Feet height of a player on the path |
| `z` | -1 | One block north of the path, so the box covers the stone |
| `dx` | 60 | Length of the span, in blocks |
| `dy` | 3 | Height of the box |
| `dz` | 3 | Width of the box |
| `~0.15` in `tp` | 0.15 | Push per run, toward +Z. Use a smaller number on a repeating command block |

### `parapet_checkpoint_a.mcfunction`

| Token | Value | Meaning |
| --- | --- | --- |
| selector `x` `y` `z` | 2, 81, 0 | Centre of the start pad |
| `r` | 4 | Radius, in blocks |
| spawn `x` `y` `z` | 2, 81, 0 | Respawn position. `y` is the air block at the player's feet |

### `parapet_checkpoint_b.mcfunction`

| Token | Value | Meaning |
| --- | --- | --- |
| selector `x` `y` `z` | 58, 81, 0 | Centre of the far pad |
| `r` | 4 | Radius, in blocks |
| spawn `x` `y` `z` | 58, 81, 0 | Respawn position at the far end |
