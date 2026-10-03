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

One command raises the college. Then you play three beats.

1. **The Parapet** — a one-block stone span over a chasm, in a storm, with wind that pushes you. A two-block gap sits in the middle. This is the clip.
2. **The Quad** — a parade ground. Touch the lodestone. Answer three questions. You get one of four original signets.
3. **The valley** — three barracks on the way, then a gold pad. Summon the dragon and ride it.

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
  behavior_pack/       manifest, dragon entity, Parapet functions, scripts/main.js
  resource_pack/       manifest, client entity, model, animations, texture
scripts/               validate.sh, package.sh, build_map.py, build_dragon_model.py
briefs/                the research and build handoffs
docs/LISTING.md        the download text, six clip scripts, and the tag list
```

## How to play

1. Install **Minecraft Bedrock** 1.21.80 or newer.
2. Build the files from the repo root with `bash scripts/package.sh`.
3. Open `dist/basgiath.mcworld` in Minecraft. On a phone, tap the file and choose Minecraft.
4. Run `/function basgiath/build`. Wait for the title "Welcome, candidate".
5. Cross the Parapet. Touch the lodestone in the Quad. In the valley, run `/function basgiath/summon_dragon` and ride.

Cheats are already on in that world. The build sets adventure mode, locks the night, and starts a storm.

To use the packs in a flat world you already have, import `dist/basgiath.mcaddon`. Enable both packs, cheats, and the **Beta APIs** toggle. Stand on open ground and run the same function. The function lifts you if the ground is too close to the bottom of the world.

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

The map is built by `/function basgiath/build`. The signet form stores a result and a wing roster. The dragon is a generated model with a horned head, a jaw, a neck, three-segment wings, four legs, and a segmented tail.

These checks do not open a Bedrock client. A phone or a Windows client still has to show the model, the texture, the form, and a Parapet crossing before you call those parts proven.

## Version note

Bedrock uses year versioning. Current stable is **26.20**. The manifests here target `@minecraft/server` 2.x. If the game rejects the pack, bump the dependency versions to match your game build.

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
