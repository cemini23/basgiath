# Phase 2 — integrate the zones

## WorkDir

`/Users/claudiobarone/Projects/dragon-rider-map`

## Context

Phase 0 split the generator into `scripts/zones/`. Phase 1 wrote six zone modules. The generator is **red**:

```
python3 scripts/build_map.py
far retry missed the lodestone
```

Cause: `scripts/zones/quad.py` no longer places a lodestone. `scripts/zones/signet.py` places one at `(50, -1, 130)`, but `geometry()` does not call `signet.py`. So the signet stone never reaches the world, and the driver's assert at `scripts/build_map.py:466` fails.

The zone modules are correct and inside budget. Only the driver is wrong.

## Plan

### 1. Import the three new zones

In `scripts/build_map.py`, next to the four existing imports, add:

```python
from zones.flight import build as build_flight
from zones.gauntlet import build as build_gauntlet
from zones.signet import build as build_signet
```

### 2. Reorder `geometry()`

Canon order: Parapet, Formation, College, Gauntlet, Presentation, Threshing, Signet.

```python
lines.extend(build_parapet(ctx))   # Parapet
lines.extend(build_quad(ctx))      # Formation
lines.extend(build_dorms(ctx))     # College
lines.extend(build_gauntlet(ctx))  # Gauntlet
lines.extend(build_flight(ctx))    # Presentation
lines.extend(build_valley(ctx))    # Threshing
lines.extend(build_signet(ctx))    # Signet
paths(ctx)
finish(ctx)
lines.extend(ctx.take())
```

`paths()` and `finish()` stay last. They carry the world rules and the plates.

### 3. Join the live lines

`LIVE` at `scripts/build_map.py:329` is a string. `zones.gauntlet.live_lines()` and `zones.valley.live_lines()` each return a list of tick commands. Join them into the live function.

Keep the existing `LIVE` body first. Append `*build_gauntlet_live()` and `*build_valley_live()` after it. Import them the same way. Do not drop the existing wind line.

`zones.flight` has no `live_lines`.

### 4. The lodestone assert

Line 466 reads:

```python
if not any("lodestone" in line for line in far):
    raise SystemExit("far retry missed the lodestone")
```

Once `signet` is wired, the valley stone at `x=50` is outside the 48-block box, so it lands in `far` and the assert passes. **Keep the assert.** Only change it if it still fails, and then explain why in the report.

The same applies to the east-stairs check at line 464, `setblock ~91`.

### 5. Do not change the stage writer

`write_functions` numbers the stages in order. Leave it. The reserved ranges in `scripts/zones/README.md` were a coordination device for parallel agents. With one integrator they are not needed. Update that README line so it does not mislead later.

### 6. `scripts/bench_static.py`

Line 30: `LODESTONE = (128, 0, 40)`.

The plaza marker is now `chiseled_stone_bricks`. The signet stone moved into the valley. Change it to:

```python
LODESTONE = (50, -1, 130)
```

### 7. `scripts/test_release.py`

`FORBIDDEN` currently bans eleven names. The naming table in `docs/IP-RULES.md` rule 3 now allows dragon names on a lookalike model. Remove these three:

```python
_phrase("ta", "irn"),
_phrase("anda", "rna"),
_phrase("sga", "eyl"),
```

Keep the rest. Character names and the series and book titles stay banned in `addon/` and `scripts/`.

### 8. Route the overland path

`paths()` at `scripts/build_map.py:136` lays `108,-1,79 → 112,-1,89`. The new courtyard south wall (10 thick, at `z=69..78`) now sits on that route. Walk the path around the outside of the ring, or move it to the west gate. Record what you chose in the report.

### 9. Docs

Update `README.md` and `DESIGN.md` from the four-zone world to the seven beats. Keep the tone. Do not use a person name and do not paste book text.

## Success criteria

1. `python3 scripts/build_map.py` exits 0.
2. All four gates pass.
3. The emitted command list follows the canon order.
4. The signet stone at `(50, -1, 130)` appears in a `far_*` file.
5. `zones.gauntlet.live_lines()` and `zones.valley.live_lines()` appear in `live.mcfunction`.

## Verify

```
python3 scripts/build_map.py
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh
python3 scripts/test_release.py
```

All five must pass.

## NEVER

- Do not change `addon/behavior_pack/manifest.json`. Keep `@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0. Do not enable Beta APIs.
- Do not use a person name anywhere.
- Do not paste book text.
- Do not copy official art.
- Do not print, write, or commit an API key.
- Do not edit the zone modules. If a zone is wrong, report it; do not fix it here.
- Do not commit or push.
