# The two keepers — name yourself, then name your dragon

## WorkDir

`/Users/claudiobarone/Projects/dragon-rider-map`

## What this adds

Two naming beats, matching the story order:

1. **The Scroll-keeper** — in the courtyard, after the Parapet and before roll call. The player gives a rider name. It is written down and read back.
2. **The Roll-keeper** — in the vale, after the bond. The player gives the dragon's full name. Only the rider and the keeper learn it.

Today the Roll-keeper is an armor stand that only speaks a line. Nothing is recorded, and there is no way to name yourself at all. This closes a promise the map already makes in text.

## What already exists — use it, do not rebuild

- **A lectern already stands at `(128, 1, 34)`** on `chiseled_stone_bricks` at `(128, 0, 34)`. `scripts/zones/quad.py` calls it the roll desk. That is the Scroll-keeper. **Do not move it.**
- **The Roll-keeper** is at `KEEPER = (50, -1, 124)` in `scripts/zones/valley.py`, on stone at `(50, -2, 124)`.
- **The input pattern already works.** `addon/behavior_pack/scripts/main.js` subscribes to `world.beforeEvents.playerInteractWithBlock`, cancels the block's own screen, and opens a form with `@minecraft/server-ui`. That is how the signet quiz runs. Copy that shape.

## Plan

### 1. Add the Roll-keeper's lectern — `scripts/zones/valley.py`

In `_keeper()`, add one lectern one block north of the stand, on the open ground:

```python
ctx.setblock(kx, ky, kz - 1, "lectern")
```

That is `(50, -1, 123)`. The dell floor is already there, so it replaces a ground block and needs no support. The footprint is inside `OPEN_X0..OPEN_X1` and `OPEN_Z0..OPEN_Z1`, so no tree is disturbed. **Verify that before you change anything.**

Do not move the armor stand.

### 2. The two forms — `addon/behavior_pack/scripts/main.js`

Add two dynamic properties:

```js
const RIDER_PROPERTY = "dragon_rider:rider_name";
const DRAGON_PROPERTY = "dragon_rider:dragon_name";
```

Add a keeper table and extend the existing interact subscriber. Keep the signet path working exactly as it is.

```js
const LECTERN_BLOCK = "minecraft:lectern";

const KEEPERS = [
  {
    id: "scroll",
    block: { x: 128, y: 1, z: 34 },
    property: RIDER_PROPERTY,
    needTag: null,
    title: "The scroll",
    ask: "The scribe waits. Give your name.",
    refusal: null,
  },
  {
    id: "roll",
    block: { x: 50, y: -1, z: 123 },
    property: DRAGON_PROPERTY,
    needTag: BOND_TAG,
    title: "The roll",
    ask: "Give the name of the one that chose you.",
    refusal: "§7A name comes after a dragon chooses you.",
  },
];
```

Structure the subscriber like this:

```js
world.beforeEvents.playerInteractWithBlock.subscribe((event) => {
  if (!event.isFirstEvent) return;
  const player = event.player;
  const type = event.block?.typeId;

  if (type === BONDING_BLOCK) {
    event.cancel = true;
    system.run(() => { /* the existing bond gate and quiz, unchanged */ });
    return;
  }
  if (type !== LECTERN_BLOCK) return;

  const loc = event.block.location;
  const keeper = KEEPERS.find(
    (k) => loc.x === k.block.x && loc.y === k.block.y && loc.z === k.block.z
  );
  if (!keeper) return;

  event.cancel = true;
  system.run(() => runKeeperForm(player, keeper));
});
```

### 3. `runKeeperForm` and `cleanName`

```js
function cleanName(raw) {
  if (typeof raw !== "string") return "";
  let s = raw
    .replace(/§./g, "")
    .replace(/[\u0000-\u001f\u007f]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (s.length > 16) s = s.slice(0, 16);
  return s;
}
```

`runKeeperForm(player, keeper)`:

1. If `keeper.needTag` and the player lacks it, `player.sendMessage(keeper.refusal)` and return.
2. Show a `ModalFormData` with `keep.title` and one text field, placeholder from `keep.ask`.
3. On cancel, return.
4. Clean the first `formValues` entry. If empty after cleaning, send `§7That name will not do. Speak again.` and return.
5. `player.setDynamicProperty(keeper.property, name)`.
6. Confirm with `player.sendMessage`. The Scroll-keeper ties the name to roll call. The Roll-keeper says only the rider and the keeper know it.

**Use `player.sendMessage`, never a command string.** Player input must never reach `runCommand`. That is the difference between a name and an injection.

### 4. Test bypasses

The file already has `/scriptevent dragon_rider:signet`. Add the same shape for each keeper:

- `dragon_rider:rider_name`
- `dragon_rider:dragon_name`

Each opens its form for the source entity, without the tag gate, so the forms stay testable.

### 5. Tests

**`scripts/test_release.py`** — assert `main.js` still has `world.beforeEvents.playerInteractWithBlock` and `runCommand("function basgiath/tick")`, and add: both property keys, both keeper ids, and `ModalFormData`. Also assert the emitted world holds a lectern at each keeper spot.

**`scripts/bench_bds.sh`** — add two probes beside the existing ones. The bench summons the anchor at `(0, 80, 0)`, so add the anchor offset: a lectern at relative `(128, 1, 34)` is absolute `(128, 81, 34)`, and relative `(50, -1, 123)` is absolute `(50, 79, 123)`.

```bash
probe LECTERN_SCROLL 128 81 34 lectern
probe LECTERN_ROLL 50 79 123 lectern
```

Add both names to the `need_true` list so a missing lectern fails the run.

## Success criteria

1. `python3 scripts/build_map.py` exits 0.
2. All gates pass, including `bench_static.py`.
3. The emitted world holds a lectern at both keeper spots.
4. `main.js` opens a form on each lectern and stores the name on the player.
5. No player input reaches `runCommand` anywhere.
6. The signet quiz still opens on the lodestone and still respects `bonded`.

## Verify

```
python3 scripts/build_map.py
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh
python3 scripts/test_release.py
python3 scripts/bench_static.py
```

`bench_bds.sh` cannot run on this Mac. It runs on RunPod after this is pushed.

## NEVER

- Do not move the roll desk lectern at `(128, 1, 34)`, or the Roll-keeper armor stand at `(50, -1, 124)`.
- Do not change `addon/behavior_pack/manifest.json`. Keep the two 2.0.0 deps. No Beta APIs.
- Do not put player input into a command string. Use the script API.
- Do not ship a book dragon name in any string or placeholder.
- Do not use a person name or book text.
- Do not print, write, or commit a key.
- Do not commit or push.
