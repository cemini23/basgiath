# Grok Build prompt — finish Basgiath

Paste everything below the line into Grok Build, run from
`/Users/claudiobarone/Projects/dragon-rider-map`.

---

# Build Basgiath to a finished product

## What this is

This repo is a free, fan-made Minecraft **Bedrock** map and add-on for the *Empyrean* fandom. It is fan work. It is never sold. The goal is a finished product a fan can download, open on a phone, and play, and that is good enough that they share it.

**Read these first, in order:**

1. `README.md`
2. `docs/IP-RULES.md` — non-negotiable
3. `DESIGN.md`
4. `DISTRIBUTION.md`
5. `BUILD_CHECKLIST.md`
6. `docs/BLOCKBENCH-SPEC.md`
7. `briefs/2026-10-03_two-path-research.md` — the research behind the strategy

## Task 0 — rename the repo

Rename the GitHub repo to **`basgiath`**:

- `gh repo rename basgiath --yes`
- Update the remote URL.
- Replace every path reference to `dragon-rider-map` in docs, scripts, and CI with `basgiath`.
- **Do not** change the pack ids (`dragon_rider:*`), the geometry id, or the pack UUIDs. Changing them breaks saved worlds.

## Hard constraints — never break these

1. **No series name, character name, or dragon name** in any file id, entity id, or pack string. The place name **Basgiath** is allowed in the title.
2. **No official art or assets.** No book covers, no Dragonkind art, no official map illustrations, no logos. Build everything from vanilla blocks.
3. **No book text.** Do not reproduce passages or dialogue. Write original lines.
4. **Never sell it.** No paid access, no Marketplace, no ads, no paywalled builds.
5. **Label it.** Every listing and every video says: fan-made, not official, not affiliated.
6. **Evoke, do not replicate.** A block-built evocation is fine. A one-to-one copy of any licensed illustration is not.
7. **Do not touch other repos.** Read-only outside this one.
8. **Never commit secrets.**

CI must stay green and get stricter, never weaker: `bash scripts/validate.sh`, `node --check addon/behavior_pack/scripts/main.js`, `bash scripts/package.sh`, and the IP-name grep.

## What "finished" means

1. **A playable map, built by command.** Do not hand-build in the editor. Write `scripts/build_map.py` that emits `.mcfunction` files into the behavior pack, so a player runs `/function basgiath/build` in a flat world and the whole map appears. Cover: the Parapet (a one-wide span over a chasm, with wind), the Quad, the dorms, the Threshing Valley, and checkpoints.
2. **The add-on works end to end** — the signet form, the rideable dragon, the Parapet functions, the checkpoints.
3. **A good dragon.** Improve `scripts/build_dragon_model.py` into a model that reads clearly as a dragon: a horned head with a jaw, a neck, three-segment wings, four legs, a segmented tail. Go to a 128×128 texture if it helps. Keep the bone names the animations drive (`tail`, `wing_left`, `wing_right`) and keep the geometry id.
4. **Shippable artifacts.** `dist/basgiath.mcaddon` and `dist/basgiath.mcworld` build from a clean checkout.
5. **Distribution assets.** A listing description for MCPEDL and CurseForge, six short vertical clip scripts for TikTok / Reels / Shorts, and the tag list.
6. **Docs a stranger can follow.**

## You have the keys — use them

- **Fan out Grok subagents** for independent workstreams.
- **Fan out cheap models** — DeepSeek, OpenCode free models, and OpenRouter models at **HY3 cost tier or less** — for bulk drafting, art passes, listing copy, and grunt work.
- **Use opencli** for social and site reads.
- **Use any tool or plugin** installed on this machine.
- **Use RunPod** to spin up a server when you need one. A Linux pod runs **Bedrock Dedicated Server**: it loads the behavior pack, so you can prove the map builds and the entity spawns and runs. It **cannot** verify the model or the texture, because those render on the client. Say plainly what only a real Bedrock client can check.
- **Consult the SEO wiki** at `/Users/claudiobarone/Projects/SEO:GEO B&M Business/wiki/` for lore angles, listing copy, and SEO ideas. **Read only — do not edit it.**

Research the setting from **public descriptions only**. Place names and the general setting are fair to use. Do not work from copied book text.

## How to work

- Plan first. Write the plan to `briefs/`. Then execute.
- Small commits, clear messages. Push when CI is green.
- Run the CI checks locally before every commit.
- Do not force-push. Do not rewrite history.
- If you cannot verify something, say so. Do not claim success you did not prove.

## Definition of done

- CI green on `main`.
- `dist/basgiath.mcaddon` and `dist/basgiath.mcworld` build from a clean checkout.
- The map, the signet form, and the dragon are playable.
- A stranger can install it from the docs.
- No series name, character name, or official art anywhere in the packs.
- A final report that separates what is **proven** from what is **unverified**, with the evidence.
