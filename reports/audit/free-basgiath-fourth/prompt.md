# Basgiath at a6ed964 — fourth audit (readonly)

You are one auditor in a multi-model audit. **Target commit: `a6ed964`.**

**Mode:** `code-debug` · **Readonly** — a markdown report only. No edits. No tool calls.

---

## Output rules — read these first

- **Start your reply with the line `### Verdict`. Nothing before it.** No preamble, no "let me work through this", no restating the task.
- **Total length: under 1200 words.** A shorter, precise report beats a long one.
- Cite `file` plus a quoted line. Line numbers are optional.
- If unsure, write `insufficient evidence` and name what to inspect. Do not speculate for paragraphs.

Earlier auditors failed this task by reasoning out loud until they ran out of output budget. Do not repeat that.

---

## Mission

**Would this project build and run correctly at `a6ed964`, and is anything still wrong?**

Work these in order and stop when you run out of room.

### 1. The origin class — the highest-value question

The generator emits **anchor-relative** commands. `scripts/build_map.py` wraps every stage as:

```
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_NN
```

So `setblock ~128 ~1 ~34 lectern` lands at `anchor + (128, 1, 34)`. The script API, however, sees **absolute** world positions.

This exact mismatch was just fixed for the two keeper lecterns: `main.js` now resolves the anchor and compares `Math.floor(anchor) + relative`.

**Find any other place with the same shape.** Look for script-side coordinate constants, block or entity lookups, distance or containment checks, the tick interval, the zones' `live_lines()`, and the benches. A constant that is relative in the commands and absolute in the script, or the reverse, is a defect.

### 2. The two keepers and the roll call

- Does the form store the name and read it back correctly?
- Does the roll call fire exactly once, and can it be made to fire twice?
- Can a player-supplied name reach a command, a selector, or a JSON string?
- Can the `rollcall_done` tag leak between players, or survive a rename wrongly?
- What happens with no anchor stand, a missing lectern, or a player who disconnects mid-form?

### 3. The verification stack

What can still pass while the product is broken? The checks are `scripts/validate.sh`, `scripts/test_release.py`, `scripts/bench_static.py`, and `scripts/bench_bds.sh`. A shared blind spot between the generator and its checkers has already produced two shipped bugs. Name any that remain.

### 4. IP compliance

`docs/IP-RULES.md`. Place names are allowed. Character names, dragon names in ids, series titles in ids, official art, and book text are banned.

---

## Context

A Minecraft Bedrock fan map. Python generates `.mcfunction` files; a behaviour pack holds a script. The world is flat.

Four audits so far:

- **1** — the far retry dropped all air fills. Fixed.
- **2** — the far retry dropped all `summon` commands, because the command parser read only `setblock` and `fill`. Fixed, and the parser now unwraps `execute … run`.
- **3** — one dorm summon used absolute coordinates instead of the anchor. Fixed.
- **4** — this one.

Two bugs came from the same root: **the generator and its checkers share one parser, so a class the parser does not understand is invisible to both.**

Measured at this commit: 32 stages, 1596 build commands, 39 summons, air volume 34,328 against an 80,000 gate, a lectern at both keeper spots. The official Bedrock dedicated server `1.26.52.3` loads the pack with `pack_error=none` and passes every block probe.

---

## Already ruled out

- Audit 1 and 2 items are closed. Do not re-report them.
- `manifest.json` keeps `@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0. Beta APIs are off.
- No Bedrock client has run. Do not ask for one. Report only what the code and commands prove.
- Bedrock `tickingarea add circle` takes its radius in **chunks**, not blocks. Raised wrongly before; do not raise it again.
- The canon facts in `docs/CANON.md` were verified separately.

---

## Required output format

### Verdict
PASS | WARN | FAIL — one line why

### Findings
| Severity | Finding | Evidence (file:line or quote) | Fix |
|----------|---------|----------------------------------|-----|

### Root cause (if debugging)
One paragraph, or "insufficient evidence" plus what to inspect.

### Confidence
high | medium | low — and what would change your mind.

### Unique angle
One thing you suspect other models might miss.

---

## Data pack

```
{pack_index}
```
