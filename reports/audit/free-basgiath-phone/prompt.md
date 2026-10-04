# Basgiath phone build — free audit (readonly)

You are one auditor in a **low-cost multi-model free audit**.

**Mode:** `code-debug` · **Your slot:** `{{MODEL_SLOT}}` · **Readonly** — markdown report only; no edits; no secrets.

---

## Mission (single sharp question)

On a Minecraft Bedrock phone, will `/function basgiath/build` place the Parapet at once and the east stairs plus the plaza before the title "Welcome, candidate"? Which bugs make the player see nothing, or a gate with no stairs, again? Give the smallest fix that places those blocks. The only path proven on this phone is the body of `/function basgiath/build`. Do not use `tick.json` to place blocks.

---

## Context

Fan-made Bedrock map. Non-monetized. One file, `dist/basgiath.mcworld`, is imported on a phone (Bedrock 1.21.90+). Commands are on. Beta APIs stay off in the UI. The world still sets experiments in `level.dat`.

College geometry is not saved as blocks. `scripts/build_map.py` writes functions. An armor stand named `build_anchor` is the origin. Every `setblock` / `fill` is tilde-relative to that stand.

Playtests on the phone:

| File | What the player saw | Cause already proven |
|------|---------------------|----------------------|
| First | Title "Building", about 15 commands, three sea lanterns, no college | `build` did not call the stages. `tick.json` never ran. |
| Inline stages | West tower, glow stairs, Parapet crossing worked. East end was empty, then a gate at about x=78. No stairs down. No plaza. Player said the rest looked too far away. | Phone simulation distance is about 4 chunks (about 64–79 blocks from the player). `setblock` fails in unloaded chunks. The gate at x=78 can land. Stairs start at x=91. The plaza is x=96–168. |
| Wait-for-tick | Nothing. No college. | That file removed the inline stage calls and waited 80 ticks for a script tick. The phone did not run that loop. |
| Current (not played yet) | Not tested | `build` calls all 20 stages at once, adds four ticking areas, then schedules a second pass. |

Current second pass:

- `schedule on_area_loaded add tickingarea college_d basgiath/fill_far` places far blocks when that area loads.
- `schedule delay add basgiath/raise 300` places far blocks again after 300 ticks (15 seconds) and shows "Welcome, candidate" once.
- Far means the command box touches x or z outside -64..79. East stairs, the exit gate, the quad, the dorms, and the valley are far.
- The same far commands also run inside the first `build` pass, while the player still stands on the anchor.
- `#stage` is set to 0 so the tick function does not build. `tick.json` is empty. `main.js` still calls `function basgiath/tick` every tick for wind and checkpoints.
- Pack version is `[0, 1, 5]`. Old worlds with the same pack UUID and version must be deleted.

Map facts that must stay:

- Parapet deck is y=32, z=20, x=15..77, with air at x=45 and x=46. A fall is fatal.
- East gate frames are at x=78 and x=90. Glow stairs run east from x=91 down to about x=123, y=0.
- Quad floor is y=-1, x=96..168. Lodestone is about (128, 0, 40).
- Do not add series names. Do not add client-modification code.

Bedrock facts to use:

- A failed command inside a function does not stop the later commands. A bad parse can reject the whole function file.
- `/schedule` runs the function as the server, at world spawn, not as the player. Tilde coordinates need `execute at` the armor stand.
- A ticking area loads chunks for the server. `setblock` can edit those chunks after they are loaded. It cannot edit them in the same tick they start loading.
- Circle radius is in chunks, 0–4 is legal. One area over about 100 chunks fails. At most 10 ticking areas.
- Single-player chat pauses ticks, so a delay does not count while chat is open.

---

## Already ruled out

- `tick.json` as the builder. It did not run on this phone.
- "One function has too many commands." The build is 984 commands in 20 stage files of at most 50 commands each. That is under the chain limit. The near college already placed from one function.
- Sending the repo folder. The phone needs one `.mcworld`.
- Changing the two-block Parapet gap or making the fall non-fatal.
- A new remote server or RunPod.

---

## Data pack files

Grok CLI may open these paths with Read tools. **HTTP auditors** (claude-ds / free OpenRouter) receive the same files **inlined** by `run_non_grok_legs.py` — they must not emit tool calls.

```
{pack_index}
```

---

## Required output format

### Verdict
PASS | WARN | FAIL — one line why

### Findings
| Severity | Finding | Evidence (file:line or quote) | Fix |
|----------|---------|----------------------------------|-----|

### Root cause (if debugging)
One paragraph — or "insufficient evidence" with what to inspect next

### Confidence
high | medium | low — and what would change your mind

### Unique angle
One thing you suspect other models might miss
