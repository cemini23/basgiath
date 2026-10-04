# Zone modules

`scripts/build_map.py` owns the driver, the coordinate constants, and the stage-file writer. Each zone owns one region. A zone returns commands. It does not write a stage file.

## Interface

```python
def build(ctx) -> list[str]:
    """Return a list of Minecraft commands."""
```

`ctx` is the only input. Use these methods:

- `ctx.fill(x0, y0, z0, x1, y1, z1, block)`
- `ctx.setblock(x, y, z, block)`
- `ctx.shell(x0, y0, z0, x1, y1, z1, block)`
- `ctx.add(command)`
- `ctx.take()` returns the commands this zone added, then clears that buffer

Read the coordinate values from the context. Do not rename them in `scripts/build_map.py`.

- `ctx.DECK_Y` is `DECK_Y` (32)
- `ctx.SPAN_Z` is `SPAN_Z` (20)
- `ctx.START` is `START` `(8, 0, 66)`

Do not import `build_map` from a zone. That import loop breaks the generator.

End `build` with `return ctx.take()`.

## Budgets

- One `stage_NN.mcfunction` holds at most 50 commands. The driver enforces this.
- One `fill` holds at most 32768 blocks. The driver splits a larger box.
- Keep the total air commands under 80000.
- Use vanilla blocks only.
- Do not add a custom dimension.
- Keep `@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0.

## Call order today

Phase 0 joins the zones, then the driver adds the paths and the world rules. The emitted commands match the four-zone world.

1. `parapet.py`
2. `quad.py`
3. `dorms.py`
4. `valley.py`
5. Driver: paths, gap, plates, night, thunder, spawn point

The writer still splits that full list into groups of 50. The ranges below are reserved for Phase 2. A zone agent must not write `addon/behavior_pack/functions`.

## Stage ranges

| Module | Beat | Stages | Who may edit |
| --- | --- | --- | --- |
| `parapet.py` | Parapet | 01-12 | No Phase 1 agent. Leave it. |
| `quad.py` | Formation | 13-20 | Courtyard agent only |
| `dorms.py` | College | 21-30 | Citadel agent only |
| `gauntlet.py` | Gauntlet | 31-40 | Gauntlet agent creates this file |
| `flight.py` | Presentation | 41-48 | Flight-field agent creates this file |
| `valley.py` | Threshing | 49-60 | Threshing agent only |
| `signet.py` | Signet | 61-64 | Signet agent creates this file |
| driver paths and finish | shared | 65-68 | Integrator only |

Canon play order is Parapet, Formation, College, Gauntlet, Presentation, Threshing, Signet. The integrator wires that order. Phase 0 does not.

## Shared signal

Threshing sets the bond. The signet reads it. Neither agent edits the other file.

- Score name: `#bond map_state`
- `0` means no bond yet.
- `1` means a dragon has chosen the player.
- The signet quiz must not open from the plaza lodestone.
- The lodestone block may stay. The courtyard agent owns that block. The signet agent owns `addon/behavior_pack/scripts/main.js`.

## Text rules

Write original lines. Do not copy book text. Do not use a person name. Place names in the naming table are allowed. A favourite dragon name is allowed only on a lookalike that matches the canon colour and the tail type, and never in a file id.
