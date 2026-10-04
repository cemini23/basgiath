# Dragon entity

Identifier: `dragon_rider:dragon`. Summon it with `/summon dragon_rider:dragon`.

The model comes from `scripts/build_dragon_model.py`. A Bedrock client still has to prove the flight.

## How the rider flies

The seat count is 1. A player mounts from the ride prompt. Look where you want to go, then move forward. Jump adds upward speed.

`minecraft:behavior.controlled_by_player` is on the entity. That goal steers a mount when the rider holds a control item. This mount has no control item. Steering in the air uses `minecraft:input_air_controlled` and `minecraft:vertical_movement_action`. Those components need entity format `1.21.90`. The pack min engine is `1.21.90`. Test on Bedrock 1.21.90 or newer. A 26.x client can open the pack.

The `dragon_rider` component group is added on spawn. It keeps gravity off and sets the fly speed again. Gravity is already off on the base entity, so the dragon hovers when you leave it.

Fall damage is cancelled on the dragon. The rider can still take fall damage after a dismount.

## Numbers to tune

Change these in `dragon.json`.

| Field | Value | Effect |
| --- | --- | --- |
| `minecraft:health` `value` and `max` | 200 | Hit points |
| `minecraft:movement` `value` | 0.25 | Base speed |
| `minecraft:flying_speed` `value` | 0.15 | Speed in the air. Set in the base components and in the `dragon_rider` group |
| `minecraft:vertical_movement_action` `vertical_velocity` | 0.4 | Rise speed while the rider holds jump |
| `minecraft:behavior.controlled_by_player` `mount_speed_multiplier` | 1.2 | Speed scale for the player-control goal |
| `minecraft:input_air_controlled` `strafe_speed_modifier` | 1.0 | Sideways speed |
| `minecraft:input_air_controlled` `backwards_movement_modifier` | 0.5 | Reverse speed |
| `minecraft:collision_box` `width` / `height` | 2.5 / 2.0 | Hit box, in blocks |
| `minecraft:rideable` `seats.position` | `[0.0, 2.1, -0.2]` | Rider offset from the entity feet |
| `minecraft:knockback_resistance` `value` | 0.8 | 1.0 ignores knockback |

Lower `flying_speed` if the dragon is too fast for the Parapet clip.
