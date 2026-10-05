# Roll call reads the name, and the keeper lookup stops assuming the origin

## WorkDir

`/Users/claudiobarone/Projects/dragon-rider-map`

## Two things

1. **A real bug in the shipped keepers.** Fix it first.
2. **Roll call reads the rider name.**

## 1. The keeper lookup is wrong off the origin

The generator emits **anchor-relative** commands. `scripts/build_map.py` wraps every stage in:

```
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_NN
```

So `setblock ~128 ~1 ~34 lectern` lands at **anchor + (128, 1, 34)**, wherever the player stood when they ran the build.

But `addon/behavior_pack/scripts/main.js` compares `event.block.location`, which is **absolute**, against the bare table entries:

```js
block: { x: 128, y: 1, z: 34 },
```

Those two agree only when the anchor is exactly on the origin. The Bedrock bench summons its anchor at `(0, 80, 0)`, so both lectern probes passed **by coincidence**. In a real world the build runs at the player's feet, the lecterns land somewhere else, and **neither form would ever open**.

The bench cannot catch this: it probes blocks, not the script's matching.

### The fix

Resolve the anchor, then compare against `floor(anchor) + relative`. Flooring is required because a block command floors its position: an anchor at `x = 8.5` puts `~128` at block `136`, not `136.5`.

```js
let cachedOrigin = null;

function buildOrigin() {
  if (cachedOrigin) return cachedOrigin;
  const dim = world.getDimension("overworld");
  for (const e of dim.getEntities({ type: "minecraft:armor_stand" })) {
    if (e.nameTag === "build_anchor") {
      cachedOrigin = {
        x: Math.floor(e.location.x),
        y: Math.floor(e.location.y),
        z: Math.floor(e.location.z),
      };
      break;
    }
  }
  return cachedOrigin;
}
```

Cache it, but **clear the cache when the build starts again**. `build_text` in `scripts/build_map.py` kills and re-summons the anchor, so a stale origin would point at the old build. Simplest safe route: do not cache at all in the interact handler — it runs on a player's click, so one `getEntities` call is cheap. Cache only if you also invalidate it.

Then match like this:

```js
const origin = buildOrigin();
if (!origin) return;                 // no anchor: not a built world
const loc = event.block.location;
const keeper = KEEPERS.find(
  (k) =>
    loc.x === origin.x + k.block.x &&
    loc.y === origin.y + k.block.y &&
    loc.z === origin.z + k.block.z
);
```

Leave the signet path alone. It matches on block **type** only, so it already works anywhere.

### Prove it, do not just claim it

Add a `prove()`-style check to `scripts/bench_static.py` (or `test_release.py`) that fails if `main.js` compares a keeper location without going through the origin. The weak version — assert the file contains `build_anchor` and `Math.floor` — is acceptable. A stronger version that parses the comparison is welcome.

## 2. Roll call reads the rider name

The roll call is six static `tellraw @a` lines emitted once at build time from `_roll_call()` in `scripts/zones/quad.py`. They teach the unit structure. Leave them.

The rider name cannot come from a command. It lives in a player dynamic property, and commands cannot read one. So the read must come from the script.

Add to `main.js`:

```js
const ROLLCALL_TAG = "rollcall_done";

function readRollCall(player) {
  const name = player.getDynamicProperty(RIDER_PROPERTY);
  if (typeof name !== "string" || !name) return;
  if (player.hasTag(ROLLCALL_TAG)) return;
  player.addTag(ROLLCALL_TAG);
  world.sendMessage(`§7Roll call. §f${name}§7 answers and takes their place.`);
}
```

In the **scroll** branch of `runKeeperForm`, after storing the name:

- Read the old value first. If a name was already stored, the line is `§7The scribe strikes the old name and writes §f${name}§7.` Otherwise: `§7The scribe writes it down: §f${name}§7. Stand in your row.`
- `player.removeTag(ROLLCALL_TAG)` on every write, so renaming reads the roll again.
- `system.runTimeout(() => readRollCall(player), 60)` — three seconds, so the writing and the call are two beats, not one.

**Use `world.sendMessage`, never a command string.** The name is player input. `cleanName` already strips colour codes and control characters, and `sendMessage` does not parse, so a name can never become an injection.

The Roll-keeper branch is unchanged. Do not read the roll for the dragon name.

### The known trade

If a player disconnects inside those three seconds, they miss the call. Talking to the keeper again clears the tag and reads it again, so it self-heals. Say so in the code comment rather than building a catch-up loop.

## 3. Tests

- `scripts/test_release.py`: assert `ROLLCALL_TAG` and `readRollCall` exist, that the keeper lookup goes through `build_anchor` and `Math.floor`, and keep the existing "only one `runCommand`" assertion.
- `scripts/bench_static.py`: the origin check from part 1.

## Success criteria

1. `python3 scripts/build_map.py` exits 0.
2. All gates pass.
3. No keeper coordinate is compared without the anchor origin.
4. `main.js` still has exactly one `runCommand`, the map tick.
5. Naming yourself at the scroll desk produces a roll-call line carrying that name.

## Verify

```
python3 scripts/build_map.py
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh
python3 scripts/test_release.py
python3 scripts/bench_static.py
```

## NEVER

- Do not write outside `/Users/claudiobarone/Projects/dragon-rider-map`. Never touch `~/.pyenv`, `~/.local`, `~/.cemini`, or any home-directory dotfile.
- Do not change the signet path, the roll desk coordinates, or the keeper stand.
- Do not put player input into a command string.
- Do not change `addon/behavior_pack/manifest.json`. No Beta APIs.
- Do not use a person name, a dragon name, or book text.
- Do not print, write, or commit a key.
- Do not commit or push.
