# Basgiath

```
              /\                                   /\
             /  \                                 /  \
            /    \            ___               /    \
           /      \        .-'   `-.           /      \
          /   /\   \      /  /\ /\  \         /   /\   \
         /   /  \   \    |  /  V  \  |       /   /  \   \
        /   /    \   \   | |  o o  | |      /   /    \   \
       /   /      \   \  | |   ^   | |     /   /      \   \
      /   /        \   \ |  \ --- /  |    /   /        \   \
     /   /          \   \ \  `---'  /    /   /          \   \
    /   /            \   \ `-.___.-'    /   /            \   \
   /   /              \   \    ||      /   /              \   \
  /   /                \   \   ||     /   /                \   \
 /___/                  \___\  ||    /___/                  \___\
                               ||   ||
                              /  \ /  \
                             /    V    \
                            /  /\   /\  \
                           /  /  \ /  \  \
                          /  /    V    \  \
                         /__/           \__\
```

A free, fan-made Minecraft **Bedrock** map and add-on for the *Empyrean* fandom.

**Not official. Not affiliated with Rebecca Yarros, Entangled Publishing, or Red Tower Books. Not monetised. No official art.**

## Why this exists

The fandom is peaking right now. The official "Dragonkind" experience launched 2026-10-01 and drew half a million people on day one. TikTok is full of "which dragon claims you" clips. This project rides that attention with a free, clippable Minecraft world, and grows into a persistent Rider's Quadrant later.

## What you play

One command raises the college. Then you play seven beats, in order.

1. **The Parapet** — a one-block stone span over a chasm, in a storm, with wind that pushes you. A two-block gap sits in the middle. This is the clip.
2. **Formation** — the walled courtyard past the span. Four wings, three sections, three squads. Roll call reads the death roll. Learn the square, then find your row.
3. **The College** — the Citadel group: the Dragon Rotunda, the keep, the dorm block, the private room, and the classrooms. This is where the first year passes.
4. **The Gauntlet** — the stepped cliff east of the dorms. Six switchbacks, six obstacles, and chain ropes that add 30 seconds if you touch one.
5. **Presentation** — the box canyon south of the college. Squads walk the footpath; the dragons form up and watch. This is not the choosing.
6. **Threshing** — the forested dell southwest of the courtyard. Stand in the open and a dragon chooses you. You do not choose it.
7. **The Signet** — after the bond, the form stone in the dell reads the bond and offers one of four original signets.

## Why Bedrock

- It runs on phones, tablets, and consoles. The fandom is on phones.
- Free distribution through MCPEDL and CurseForge.
- Java is PC-only, so it cuts off most of the audience.

## Layout

```
README.md              this file
DESIGN.md              the map spec and the Parapet moment
BUILD_CHECKLIST.md     install and playtest steps
DISTRIBUTION.md        where it ships and how it gets found
docs/IP-RULES.md       the non-negotiable fan-project rules
docs/BLOCKBENCH-SPEC.md the dragon model spec (bones, UV, export)
docs/ascii-dragon.txt  a larger dragon variant (62 lines, 111 columns)
addon/
  behavior_pack/       manifest, dragon entity, the basgiath functions, scripts/main.js
  resource_pack/       manifest, client entity, model, animations, texture
scripts/               validate.sh, package.sh, test_release.py, build_map.py,
                       build_dragon_model.py, build_world.py, nbt_le.py
scripts/zones/         one module per beat: parapet, quad, dorms, gauntlet,
                       flight, valley, signet
briefs/                the research and build handoffs
docs/LISTING.md        the download text, six clip scripts, and the tag list
```

## How to play

1. Install **Minecraft Bedrock** 1.21.90 or newer. Use a full copy. The free trial turns commands off, so it cannot run the build function.
2. Build the files from the repo root with `bash scripts/package.sh`.
3. Open `dist/basgiath.mcworld` in Minecraft. On a phone, tap the file and choose Minecraft.
4. Run `/function basgiath/build`. Close chat. The screen says "Building". Stay still for about 15 seconds. The game moves you onto the plaza, then back to the start. Then the screen says "Welcome, candidate". If the screen stays dark, quit Minecraft, delete the old Basgiath world, and import this file again.
5. You land on a glowing path. Climb the stairs in front of you, then cross the Parapet. Walk the courtyard, then take the west gate south to the Citadel. East of the dorms is the Gauntlet; south of the college is the flight field where the dragons look. Southwest, in the dell, a dragon chooses you. After the bond, touch the form stone in the dell with an empty hand to open the signet form. `/function basgiath/summon_dragon` still places a dragon on the dell pad if you want the ride.

A phone, a tablet, or Windows can open the file. A Nintendo Switch cannot open it from a folder. Upload the world to a Realm from a phone or from Windows. Then download it on the Switch with the same Microsoft account. Minecraft on a Mac is Java. It cannot open this file.

Cheats are already on in that world. The build sets adventure mode, locks the night, and starts a storm. The script uses stable `@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0. Do not enable Beta APIs.

To use the packs in a flat world you already have, import `dist/basgiath.mcaddon`. Enable both packs and cheats. Stand on open ground and run the same function. The college builds at your feet.

## How to build the files

From the repo root:

```
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh
python3 scripts/test_release.py
```

`package.sh` writes `dist/basgiath.mcaddon` and `dist/basgiath.mcworld`.

The GitHub repo is `basgiath`. Run the commands from the repo root. The folder name on your computer can be anything.

## How to ship

MCPEDL and CurseForge. Free only. See `DISTRIBUTION.md`.

## Status

The map is built by `/function basgiath/build` at your feet. You start on a glowing path. The stairs in front of you climb 32 blocks to the span. A fall from the span kills you, and you respawn on that path. That function places one stone under the anchor and gives the anchor resistance, so the stand stays put. The generator writes all seven beats in one pass: the span and its towers, the courtyard ring and the roll-call square, the Citadel group, the Gauntlet cliff, the flight field, the dell, and the signet stone. An empty-hand interact on that stone opens the signet form, and only after a dragon has chosen you. The form stores a result and a wing roster. The dragon is a generated model with a horned head, a jaw, a neck, three-segment wings, four legs, and a segmented tail.

These checks do not open a Bedrock client. A phone or a Windows client still has to show the model, the texture, the form, and a Parapet crossing before you call those parts proven.

## Version note

The packs and the world need Bedrock **1.21.90** or newer. That engine is the June 2025 Chase the Skies drop. In October 2026 the retail drop is **26.50**, Wilderness Bound (15 September 2026). Small hotfixes after it are 26.51 and 26.52. A 26.x client can open this world.

The manifests pin `@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0. Those modules are stable. Do not enable Beta APIs. Do not bump the dependency versions.

## Support

Thank you for visiting — stars, shares, and kind words all help. The map is free. It will stay free. Tips pay for the build time behind it, and nothing here is ever sold.

**Donation-only addresses** — not trading or production wallets.

| Chain family | Address |
|--------------|---------|
| **X Money** (fiat, US) | Request [@Cemini23](https://x.com/Cemini23) in the X app — scan the Request QR |
| **EVM** (Ethereum, Polygon, Base, Arbitrum, …) | `0x444C5C2eC439E0382aa5a17F70313c536BcC5D58` |
| **Solana / SVM** | `J4zNn4hK9jTrKBFY8sbAGJHLoZvXvQf4B9pQSbSrocZE` |
| **Polymarket** (referral) | [polymarket.com/?r=Cemini23](https://polymarket.com/?r=Cemini23) |
| **Hyperliquid** (referral) | [app.hyperliquid.xyz/join/CEMINI23](https://app.hyperliquid.xyz/join/CEMINI23) |

**Projects & sites**

| Project | Link |
|---------|------|
| **Outlier Weekly** (methodology newsletter) | [outlierweekly.substack.com](https://outlierweekly.substack.com) |
| **Atto** — organize Italian family documents on your computer | [youratto.com](https://youratto.com) |
| **GuruWatcher** — Discord alerts for your newsletter's price levels | [guruwatcher.com](https://guruwatcher.com) |
| **X** | [@Cemini23](https://x.com/Cemini23) | Build logs and walkthroughs |
