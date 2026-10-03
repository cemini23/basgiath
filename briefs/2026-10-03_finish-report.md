# Finish report — Basgiath

Date: 2026-10-03. This report separates what a command proved from what a Bedrock client still has to prove.

## Proven

Local checks on commit `45033da`, then again after the generators ran a second time. `git diff` on the generated files was empty.

| Check | Result |
| --- | --- |
| `bash scripts/validate.sh` | `parsed 8 JSON files; 5 pack UUIDs are unique` |
| `node --check addon/behavior_pack/scripts/main.js` | exit 0 |
| `bash -n scripts/*.sh` | exit 0 |
| `python3 scripts/test_release.py` | `map ok: 7 stages`, `dragon ok: 18 bones`, `world ok: 19036 bytes`, `release checks ok` |
| Name grep on `addon/` and `scripts/` | no blocked series name, character name, or author name |
| Second generator run | PNG bytes and `dragon.geo.json` matched the first run. `git diff --exit-code` stayed clean |

`bash scripts/package.sh` wrote both files from this checkout:

- `dist/basgiath.mcaddon`
- `dist/basgiath.mcworld` — 18653 bytes after the stable PNG encoder, 28 zip entries

The world zip root holds `level.dat`, `levelname.txt`, both pack lists, and the packs at `behavior_packs/basgiath` and `resource_packs/basgiath`. Decoded `level.dat` has:

- `LevelName` Basgiath
- `Generator` 2 (flat) and `GameType` 1 (creative)
- `commandsEnabled` 1
- spawn `0, -60, 0`
- `experiments_ever_loaded` 1 and `beta_apis` 1
- rain level 1 and lightning level 1
- the behavior pack UUID and version copied from the manifest

The build function is inside that zip. The summon line in the zip is `summon dragon_rider:dragon ~43 ~-5 ~117`.

### Map

`scripts/build_map.py` writes the functions. A player runs `/function basgiath/build`. The run here did not open Minecraft. It did check the commands.

- 7 stage files, 322 build commands. No stage has more than 50 commands.
- Every `fill` box is at most 32768 blocks.
- The deck at Y=8, Z=20 is stone, with air at X=45 and X=46. X=44 and X=47 are polished blackstone.
- Chasm water is Y=-39 to Y=-37. The deepslate floor stays at Y=-40, so the water has a block under it.
- A simulated top view shows the two towers, the span, the gap, the Quad, the bleachers, three dorms, the valley, the paths, and the gold pad.
- A simulated slice at Z=20 shows the span, the gap, the east stairs, and the water on the floor.

### Dragon

The generator writes `geometry.dragon_rider` at 128 by 128. Bones include a neck, a jaw, three wing segments on each side, four legs, and a tail in four parts. The left wing pivot X is positive. The right wing pivot X is negative. The head parent is the neck. One body cube has its top at Y=32 and covers Z=0, so the seat `[0.0, 2.1, -0.2]` still matches the chest. The seat line was not edited.

An orthographic drawing of the cubes shows a horned head, a jaw, a neck, a body, four legs, three-part wings, and a segmented tail with a spade. That drawing is not a Minecraft render.

Idle animation keys are the tail, the head, and the jaw. The fly keys rotate the left wing to -28 degrees on Z and the right wing to +28 degrees on Z.

### Signet

`main.js` still opens on a lodestone and on the test event `dragon_rider:signet`. After the form, it stores a name and a signet on `dragon_rider:wing`, keeps the last 24 riders, and says "1 rider" or "N riders". `node --check` passed. No form was opened in a game.

### Identity

Pack ids stay `dragon_rider:*`. The geometry id stays `geometry.dragon_rider`. The pack UUIDs in the two manifests were not edited. The GitHub repo name is `basgiath`.

GitHub Actions on `main` passed for commit `3cbf749`: https://github.com/cemini23/basgiath/actions/runs/37157510271

The run before it failed. Pillow wrote different PNG bytes on Linux than on this Mac. The generator now writes the PNG itself, with one stored block, so the bytes match. That failed run is https://github.com/cemini23/basgiath/actions/runs/37157437615

## Unverified

This machine is macOS. Docker is not installed. The RunPod CLI is not installed. The home env files have no RunPod key. No dedicated server was started. A server could load the behavior pack and run the functions. It still could not show the model or the texture.

Only a real Bedrock client can prove these:

1. The dragon picture, the texture, the wing flap, and the jaw.
2. The rider sits on the back and the dragon flies when you steer it.
3. The lodestone opens the form and the buttons work.
4. The wind push, the gap, the fall rescue, and the four checkpoints feel right in a world.
5. A phone can open `basgiath.mcworld`, run `/function basgiath/build`, and finish the crossing.

## Notes a later edit should keep

- Do not put a series name, a character name, or a dragon name in `addon/` or `scripts/`. The place name Basgiath is allowed.
- Do not change pack UUIDs, pack ids, or `geometry.dragon_rider`.
- The in-game credit stays short: "Fan-made. Not official. Not affiliated with any publisher."
- The full credit, with the author and the publishers, stays in the README, the listing, and the clip scripts.
- Water must not replace the deepslate at relative Y=-40.
