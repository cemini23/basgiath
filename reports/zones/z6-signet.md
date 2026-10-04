# z6 — Signet agent report

Scope: move the signet form off the day-one plaza trigger and onto the
post-bond state, per canon section 7. Two files edited, one report written.

## What I built

### `addon/behavior_pack/scripts/main.js`

The interact listener still runs on
`world.beforeEvents.playerInteractWithBlock`. It still cancels a lodestone
use, so the compass screen never opens. The listener now gates the form on
the bond:

- `bonded` tag present → `runSignetQuiz(player)` runs.
- tag absent → no form. One message is sent:
  `A signet comes after a dragon chooses you.`

The tag name is `bonded`, held in `BOND_TAG`. Threshing sets it. This script
only reads it; nothing here writes the tag or the `#bond` score.

`/scriptevent dragon_rider:signet` is unchanged as a test bypass. It opens
the quiz with or without the tag, so the form stays testable before the
Threshing beat exists.

The four outcomes are unchanged: Stormcaller, Shadowwalker, Emberwright,
Stoneward. No other signet name was added. The only text change inside the
quiz is the action-form title, `Conscription` → `Signet`, because the form is
no longer part of intake day.

The two strings the release test greps for are intact:

- `world.beforeEvents.playerInteractWithBlock`
- `runCommand("function basgiath/tick")`

There is no `afterEvents.playerInteractWithBlock` listener.

### `scripts/zones/signet.py` (new)

Stage range 61–64, reserved for this zone. It places one lodestone at
`x=50, y=-1, z=130`, inside the valley bowl, and clears the block above it to
air. It ends with `return ctx.take()`. It uses only `ctx.setblock` and does
not import `build_map`. Emitted commands under the real `rel()`:

```
setblock ~50 ~-1 ~130 lodestone
setblock ~50 ~0 ~130 air
```

The plaza lodestone is left in place. The courtyard agent owns that block;
the gate in `main.js` is what keeps the form from opening there on day one.

## Versions and flags

Not touched. `addon/behavior_pack/manifest.json` still depends on
`@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0. No Beta APIs
module was added. No version was bumped.

## Files touched

| File | Action |
| --- | --- |
| `addon/behavior_pack/scripts/main.js` | edited |
| `scripts/zones/signet.py` | created |
| `reports/zones/z6-signet.md` | created (this report) |

No other file was edited. No git checkout, restore, reset, or clean was run.

## Commands I ran

Read-only and local checks only:

1. `python3 -m py_compile scripts/zones/signet.py` → passed.
2. A Python snippet imported `zones.signet` and ran `build(ctx)` against a
   stub context. Output: stage range `61 64`, commands
   `['setblock ~50 ~-1 ~130 lodestone', 'setblock ~50 ~0 ~130 air']`.
3. `node --check` on a copy of `main.js` in `/tmp` → passed. The copy was
   made so no new file landed in the repo.
4. A Python string check confirmed the two required release strings are
   present, the `afterEvents` interact listener is absent, the four outcome
   names are present, the `bonded` gate is present, and neither edited file
   contains a forbidden name.
5. `git status --short` and `git diff -- addon/behavior_pack/scripts/main.js`
   to confirm the edit set.

I did not run `scripts/build_map.py`, `scripts/package.sh`, or
`scripts/test_release.py`. I did not commit or push. No key was printed.

## What I could not do

- **No in-game check.** There is no Bedrock client or server run here, so I
  could not watch a tagged player get the form and an untagged player get the
  message. The gate is verified by reading the code and by the syntax check
  only.
- **Release test not run.** `scripts/test_release.py` was off limits for this
  task. I checked its two signet greps and its forbidden-name list by hand
  instead of executing it.
- **`signet.py` is not wired in.** The driver's zone list and call order live
  in `scripts/build_map.py`, which I was told not to edit. Until the
  integrator adds `signet.py` to the canonical order and the driver's
  stage 65–68 block, the lodestone in the valley will not appear in a built
  world. The module itself is ready for that call.
- **The bond signal is a dependency, not a guarantee.** Threshing must set
  the `bonded` tag. Until it does, the only way into the form is the
  `/scriptevent` bypass. If Threshing chooses to set only the `#bond` score
  and not the tag, the gate must be reworked; I could not confirm the tag
  against a Threshing implementation because none exists in the tree yet.
- **`hasTag` inside `system.run`.** Moving the read out of the before-event
  callback avoids read-only restrictions, but I could not execute the
  `@minecraft/server` 2.0.0 API to confirm the call shape at runtime.

## Open item for the integrator

Add `zones.signet` to `scripts/build_map.py` after `valley.py` in the canon
order, within the reserved 61–64 range, and keep Threshing's `bonded` tag
name in sync with `BOND_TAG` in `main.js`.
