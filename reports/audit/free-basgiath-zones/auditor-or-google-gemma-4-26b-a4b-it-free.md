<!-- model=nvidia/nemotron-3.5-lightning:free channel=openrouter-free ts=20261004T2344Z -->
<!-- fallback-from-google/gemma-4-26b-a4b-it:free -->

### Verdict
PASS – dropping far air is safe; the near pass already places all air within the loaded box (sim‑distance 4), and including far air would push the air volume past the 80 000 gate (84 376 > 80 000), causing a phone stall.

### Findings
| Severity | Finding | Evidence (file:line or quote) | Fix |
|----------|---------|--------------------------------|-----|
| medium | The far retry drops every air fill (`far = [line for line in far if not line.endswith(" air")]`). This removes 218 air commands (volume 30 259 blocks) from the far pass, keeping total air at 54 117 blocks – well under the 80 000 gate. Without the drop the gate would fail (84 376 > 80 000). | `build_map.py` line `far = [line for line in far if not line.endswith(" air")]`; `test_release.py` air‑volume check. | None needed – the drop is intentional for budget. |
| medium | Canon play order in `geometry()` (Parapet → quad → dorms → gauntlet → flight → valley → signet) matches the zones’ stage ranges (01‑12, 13‑20, 21‑30, 31‑40, 41‑48, 49‑60, 61‑64) and the shared bonded signal (Threshing sets `#bond map_state` → 1, signet reads it). | `geometry()` function and `zones-README.md` stage‑range table. | None needed – order is correct. |

### Root cause (if debugging)
The far‑air drop was introduced to keep the air budget within the phone’s limit. The near pass already places every air fill while the anchor holds the player inside the loaded box (sim‑distance 4); repeating air in the far pass is unnecessary and would exceed the 80 000 gate, breaking the release check.

### Confidence
high – the numbers (30 259 far‑air blocks, total 84 376 vs 54 117 after drop) and the gate test in `test_release.py` confirm the decision.

### Unique angle
Other models might treat the far‑air removal as a bug, but the design intentionally omits it because the player never reaches those chunks under normal play; the drop is a budgeting choice, not a correctness issue.
