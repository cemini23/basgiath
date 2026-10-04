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

## Call order

The driver joins the zones in canon order, then adds the paths and the world rules.

1. `parapet.py`
2. `quad.py`
3. `dorms.py`
4. `gauntlet.py`
5. `flight.py`
6. `valley.py`
7. `signet.py`
8. Driver: paths, gap, plates, night, thunder, spawn point

The writer splits that full list into groups of 50. A zone agent must not write `addon/behavior_pack/functions`.

## Stage ranges

The ranges below were a coordination device for Phase 1, when several agents
wrote the zones in parallel. They are **not** reserved any more. Phase 2 wired
the zones in one pass, so the writer now numbers the stage files straight
through the call order above. Read the numbers as a rough map, not as a lock.

| Module | Beat | Phase 1 range | Who may edit |
| --- | --- | --- | --- |
| `parapet.py` | Parapet | 01-12 | Leave it. |
| `quad.py` | Formation | 13-20 | Courtyard owner |
| `dorms.py` | College | 21-30 | Citadel owner |
| `gauntlet.py` | Gauntlet | 31-40 | Gauntlet owner |
| `flight.py` | Presentation | 41-48 | Flight-field owner |
| `valley.py` | Threshing | 49-60 | Threshing owner |
| `signet.py` | Signet | 61-64 | Signet owner |
| driver paths and finish | shared | 65-68 | Integrator only |

Canon play order is Parapet, Formation, College, Gauntlet, Presentation, Threshing, Signet. The driver wires that order.

## Shared signal

Threshing sets the bond. The signet reads it. Neither agent edits the other file.

- Score name: `#bond map_state`
- `0` means no bond yet.
- `1` means a dragon has chosen the player.
- The signet quiz must not open from the plaza lodestone.
- The lodestone block may stay. The courtyard agent owns that block. The signet agent owns `addon/behavior_pack/scripts/main.js`.

## Text rules

Write original lines. Do not copy book text. Do not use a person name. Place names in the naming table are allowed. A favourite dragon name is allowed only on a lookalike that matches the canon colour and the tail type, and never in a file id.
