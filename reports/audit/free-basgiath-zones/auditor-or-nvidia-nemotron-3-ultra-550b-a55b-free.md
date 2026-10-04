<!-- model=nvidia/nemotron-3-ultra-550b-a55b:free channel=openrouter-free ts=20261004T2344Z -->

### Verdict
FAIL — Dropping all far air fills leaves structure interiors (east tower, rotunda, keep, dorm, classroom) solid because their hollowing air fills are stripped from the retry pass while the outer solid fills are retried.

### Findings
| Severity | Finding | Evidence | Fix |
|----------|---------|----------|-----|
| critical | Far retry filters out every line ending with ` air`, including hollowing fills for the east tower, rotunda, keep, dorm block, private room, and classroom. The load pass cannot place them (chunks unloaded), so the retry places the solid shells but never the interior air. | `build_map.py:382` (`far = [line for line in far if not line.endswith(" air")]`); `zone-parapet.py:78-81` (east tower solid+air pair, both far); `zone-dorms.py:94-97` (rotunda solid+air pair, both far); `zone-dorms.py:118-121` (keep shell); `zone-dorms.py:140-143` (dorm shell); `zone-dorms.py:160-163` (private room shell); `zone-dorms.py:178-181` (classroom shell) | Keep only *redundant* far air (chasm, valley floor, staircase clearance) in the retry. Drop air fills that are strictly inside a matching solid fill (same zone, nested bounding box). E.g., pair each `fill … stone_bricks` with its following `fill … air` and retain the air if the air box is contained in the solid box. |
| high | The comment at `build_map.py:377-380` claims "the load pass already places every air fill while the anchor holds the player inside the loaded box" — false for any air fill whose bounding box exceeds `LOADED=48`. | `build_map.py:377-380`; `build_map.py:247-260` (`is_far` returns true for x0>48) | Remove or correct the misleading comment. |
| medium | Canon play order in `geometry()` matches the zone README and the shared `bonded` signal: Parapet → Formation → College → Gauntlet → Presentation → Threshing → Signet. Threshing sets `#bond map_state=1` and `bonded` tag; `main.js` gates the signet quiz on `player.hasTag("bonded")`. | `build_map.py:198-210` (`geometry` call order); `zones-README.md:38-45` (canon order + shared signal); `zone-valley.py:180-185` (sets bond); `main.js:48-55` (reads tag) | No fix needed — ordering and signal are correct. |

### Root cause
The far-retry filter was written as a blunt "drop all air" to pass the 80k air-volume gate in `test_release.py:186`. It did not distinguish between *redundant* air (clearing already-empty world space) and *structural* air (hollowing a solid fill that the retry will re-place). The east tower, rotunda, keep, dorm, private room, and classroom all use a `shell()` or explicit solid-then-air pattern where the air fill is strictly inside the solid fill; both are far, so pass 1 places neither, pass 2 places only the solid.

### Confidence
high — The code paths are explicit: every zone that uses `shell()` or a manual solid/air pair in the far zone (x > 48)
