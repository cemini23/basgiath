# Free audit — basgiath-ship

**Mode:** prod-ship · **Auditors:** Grok + claude-ds (deepseek-v4-flash) + free OR (thinkingmachines/inkling-small:free failed, nvidia/nemotron-3-ultra-550b-a55b:free)
**Pack:** `/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/pack-free-basgiath-ship` · **Out:** `/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/free-basgiath-ship`

| Slot | Channel | Model | Verdict |
|------|---------|-------|---------|
| 1 | grok | grok-cli | WARN — lodestone touch does not open the signet form |
| 2 | claude-ds | deepseek-v4-flash | FAIL — treats the Y=80 anchor as a world-absolute offset (see Conflicts) |
| 3 | openrouter-free | thinkingmachines/inkling-small:free | CHANNEL FAIL — HTTP 403, empty stub. No product verdict |
| 4 | openrouter-free | nvidia/nemotron-3-ultra-550b-a55b:free | WARN — module version and a render file the pack did not include |

`run_non_grok_legs.py` also wrote `auditor-or-nvidia-nemotron-3.5-lightning-free.md` after the Inkling 403. That file is degraded. It claims `main.js` contains series dragon names. The quiz uses Stormcaller, Shadowwalker, Emberwright, and Stoneward. Do not count that file as a vote.

## Consensus (≥2 auditors agree)
- The map is not a clean PASS. Grok and Nemotron Ultra both say WARN. They do not agree on the defect.
- Install packaging is intact. `package.sh` writes the addon and calls `build_world.py` for `dist/basgiath.mcworld`. `test_release.py` checks the zip root, the pack UUIDs, and the flat-world flags.
- Water stays on relative Y=-39..-37. The deepslate floor at relative Y=-40 stays. The span gap is X=45 and X=46. The seat stays `[0.0, 2.1, -0.2]`.
- Series names, character names, and dragon names are absent from `addon/` and `scripts/`. The short in-game credit does not name the author or the publishers. Listing tags are outside that scan on purpose.
- A Bedrock client was not run. Picture, texture, form pixels, flight feel, and a phone crossing stay unverified. That gap is not a code defect.

## Unique (single auditor — still investigate)
- [grok] `main.js` subscribes to `afterEvents.playerInteractWithBlock`. That event runs after a successful use. A lodestone succeeds with a compass. The player has an empty hand, and stage 7 sets adventure mode. The quiz never opens from the stone. `/scriptevent dragon_rider:signet` still works. Mojira MCPE-218040 describes this split between the before-event and the after-event.
- [grok] The fresh world lifts the player to exact Y=80, then summons a gravity armor stand. The college is one stage per tick. One gravity step can change the block column before the span stages finish. Place one support block under the stand in `build.mcfunction` on the summon tick.
- [grok] Signet ties keep object-key order. Stormcaller wins 28 of 64 answer patterns. Emberwright and Stoneward win 10 each. Break ties at random, or use the last answer.
- [grok] Entity format `1.21.90` is required for `minecraft:input_air_controlled`. The manifest minimum is still `[1, 21, 80]`. Raise the published minimum to the retail build that accepts that format. The entity note already says to test on Bedrock 26.20.
- [grok] The anchor armor stand is invisible and can be hit. If it dies, wind, rescue, checkpoints, and the summon stop.
- [nemotron-ultra] Wants a schema check beyond `json.load`, and a check that the `.mcaddon` zip has both manifests. CI already runs `package.sh`. A schema check is extra strictness, not a current break.

## Conflicts (Glasswing — do not silently pick)
| Topic | Grok | claude-ds | OR inkling | OR nemotron-ultra | Resolution |
|-------|------|-----------|------------|-------------------|------------|
| Y=80 anchor | Relative build. Gravity during the 7 ticks is the risk. | FAIL. Geometry is "80 blocks too high." Dragon summon misses the pad. Wind misses the deck. | no report | not raised | Stage commands run `at` the anchor. `~-5` and `~8` move with that stand. The gold pad and the dragon use the same origin. Keep the lift. It moves a low player off the void. Do not rewrite the offsets. |
| Chasm rescue | Fallers from the deck enter the box at relative Y=-4, above the water. | FAIL. `dy=36` misses the top of the air column. Later rows in the same report call the same teleport correct. | no report | not raised | The box is relative Y=-40 through Y=-4. It does not cover Y=-3..-1. A player who leaves the span still falls into the box before the water. Leave the selector. |
| Signet trigger | critical. Switch to `beforeEvents`, then `system.run` the quiz. | Says the subscribe is correct. | no report | HIGH on a server-ui version clash. `ActionFormData` is in 2.0.0. | Change the event. Keep `@minecraft/server-ui` at `2.0.0`. Do not hand the player a compass. |
| Rider seat | Keep `[0.0, 2.1, -0.2]`. Chest top is model Y=32 and covers Z=0. | Maybe a float. Verify in a client. | no report | HIGH. Adjust the seat. | Hard rule. Do not move the seat. The chest top did not move. |
| Render controller | `addon/resource_pack/render_controllers/dragon.render_controllers.json` defines `controller.render.dragon`. | not raised | no report | MEDIUM. File missing, dragon invisible. | The audit pack did not include that file. The repo has it. Geometry, material, and texture are `default`. Not a defect. |
| CI pins | Mission says Actions is green on `7e711b6`. | FAIL. `actions/*@v7` and `pillow==12.2.0` cannot resolve. | no report | CI is only a JSON parse. | The workflow in the pack is the one the mission calls green. Do not retarget the actions in this audit. |
| Fan-work names | Clean in `addon/` and `scripts/`. | Listing tags are allowed. | no report | not raised | Lightning's name claim is false. Do not edit the quiz copy. |

## Recommended fix order
1. Open the signet form from `world.beforeEvents.playerInteractWithBlock`, and keep `system.run` around `runSignetQuiz`. Guard `isFirstEvent` and `minecraft:lodestone`.
2. In `build.mcfunction`, set one block under `build_anchor` in the same function as the summon, so the stand cannot fall before stage 1.
3. Raise the README minimum and `min_engine_version` to the retail build that accepts entity format `1.21.90`. Leave pack UUIDs, `dragon_rider:*`, and `geometry.dragon_rider` alone.
4. Break signet ties among the keys that share the top score.
5. If `build_anchor` is missing after the build, summon it again from `basgiath/tick` while `#stage` is 0.
6. On the next edit to `build_world.py`, write the Beta APIs byte as `gametest`. Stable `@minecraft/server` `2.0.0` does not need that toggle today.

## Verdict rollup
**Overall:** SHIP-WITH-FIXES — A stranger can package the world, run `/function basgiath/build`, and get the span, the water, the gap, and a rideable `dragon_rider:dragon` whose seat and fly components match the current schema. CI, as stated for commit `7e711b6`, already checks generators, names, and the world zip. The signet beat still fails on the path the listing tells the player to use: touch the lodestone with an empty hand. Fix that listener before you call the Quad proven. Do not adopt the DeepSeek coordinate rewrite or the Nemotron seat change. Inkling did not review the pack.
