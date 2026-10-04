<!-- model=nvidia/nemotron-3-ultra-550b-a55b:free channel=openrouter-free ts=20261003T2216Z -->
<!-- retry-after-empty-or-stub -->

### Verdict
WARN — Several defects risk breaking the signet form, dragon rideability, and CI strictness; install and build function appear sound.

### Findings
| Severity | Finding | Evidence | Fix |
|----------|---------|----------|-----|
| HIGH | Signet form uses `ActionFormData` which requires `@minecraft/server-ui` 1.1.0+, but manifest declares `@minecraft/server-ui` 2.0.0 — version mismatch may cause runtime script error on older clients | `behavior_manifest.json:23` declares `"@minecraft/server-ui": "2.0.0"`; `main.js:3` imports `ActionFormData` from `@minecraft/server-ui` | Align manifest dependency to minimum version that provides `ActionFormData` (1.1.0) or bump to 2.0.0 only if confirmed available on target 1.21.80 |
| HIGH | Dragon rideable seat position `[0.0, 2.1, -0.2]` may not align with model chest top at Y=32 (model space) — rider could float or clip | `dragon.json:48` seat position; `build_dragon_model.py:63` comment "Top of the chest is Y=32. Z covers 0."; `build_dragon_model.py:72` body cube origin `[-12, 16, -28]` size `[24, 16, 32]` → top at Y=32, Z from -28 to 4 | Verify seat Y=2.1 matches model Y=32 after entity scaling; if not, adjust seat Y in `dragon.json` (allowed) or document the offset |
| MEDIUM | `dragon.entity.json` references `controller.render.dragon` but no render controller file exists in pack | `dragon.entity.json:18` `"render_controllers": ["controller.render.dragon"]`; no `render_controllers/dragon.render_controllers.json` in resource pack | Add minimal render controller or change to `controller.render.default` |
| MEDIUM | `main.js` uses `player.onScreenDisplay.setTitle()` which was added in `@minecraft/server` 1.8.0 — manifest declares 2.0.0 but target 1.21.80 may have older module | `main.js:72` `player.onScreenDisplay.setTitle`; `behavior_manifest.json:22` `"@minecraft/server": "2.0.0"` | Confirm 1.21.80 ships with `@minecraft/server` ≥1.8.0; if not, replace with `titleraw` command via `system.runCommand` |
| MEDIUM | CI `validate.sh` only checks JSON parse and UUID uniqueness — does not validate entity/component schema, animation format, or geometry format | `validate.sh:1-22` only `json.load` and UUID check | Extend `validate.sh` to run schema validation (e.g., `bedrock-addon-validator` or custom checks for required fields) |
| LOW | `package.sh` builds `.mcaddon` but CI does not verify `.mcaddon` can be imported — only `.mcworld` is tested | `package.sh:10-14` creates `.mcaddon`; `ci.yml` runs `test_release.py` which only checks `.mcworld` | Add CI step to validate `.mcaddon` structure (manifests at root, both packs present) |
| LOW | `build_map.py` generates `stage_07.mcfunction` with `setblock ~44 ~8 ~20` and `setblock ~47 ~8 ~20` but `test_release.py` only checks for `setblock ~45 ~8 ~20 air` and `setblock ~46 ~8 ~20 air` — polished blackstone blocks at gap edges not verified | `build_map.py:134` parapet sets X=44,47 to polished_blackstone; `stage_07.mcfunction` not shown but `build_map.py:260` finish() only clears 45,46; `test_release.py:73` checks for `setblock ~44 ~8 ~20` and `setblock ~47 ~8 ~20` in blob | Ensure `stage_07.mcfunction` explicitly sets X=44,47 to polished_blackstone (or stone_bricks) so gap edges are solid |
| LOW | `dragon.animation.json` fly animation rotates wings on Z axis only — may look stiff; no body/head/tail movement during flight | `dragon.animation.json:27-40` only `wing_left` and `wing_right` rotation Z | Consider adding subtle body pitch, head bob, tail sway to fly animation for better feel (non-blocking) |

### Root cause
The signet form and dragon rideability depend on Bedrock module versions and model-seat alignment that cannot be verified without a client. CI validates syntax and UUIDs but not runtime schema compatibility. The render controller reference is a missing file that will cause the dragon to be invisible or use fallback rendering.

### Confidence
medium — A real Bedrock 1.21.80 client test would confirm or refute the seat alignment, module version compatibility, and render controller issue. The signet form module version mismatch is the highest-risk defect.

### Unique angle
The custom PNG encoder in `build_dragon_model.py` (stored-block, no compression) guarantees cross-platform byte identity — this is a strength, not a defect. Other auditors may flag the lack of Pillow in CI as a risk, but the encoder eliminates that variance.
