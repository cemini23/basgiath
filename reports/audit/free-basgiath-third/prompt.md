# Basgiath at e2acf93 — third audit (readonly)

You are one auditor in a low-cost multi-model audit. **Target commit: `e2acf93`.**

**Mode:** `code-debug` · **Readonly** — a markdown report only. No edits. No tool calls.

---

## Output rules — read these first

- **Start your reply with the line `### Verdict`. Nothing before it.** No preamble, no "let me work through this", no restating the task.
- **Total length: under 1200 words.** A shorter, precise report beats a long one.
- Cite `file` plus a quoted line. Line numbers are optional.
- If you are unsure, write `insufficient evidence` and name what to inspect. Do not speculate for paragraphs.

Two earlier auditors failed this task by reasoning out loud until they ran out of output budget. Do not repeat that.

---

## Mission

**Would this project build a coherent, playable Bedrock world at `e2acf93`, and is anything still wrong?**

Check these in order. Stop when you run out of room.

1. **The entity-spawn fix.** The far retry used to drop every `summon`. It now wraps each far summon in `execute unless entity @e[type=…,name="…"] run summon …`. Is that correct and idempotent? Does the stage pass still summon plainly? Is any guarded summon malformed?
2. **The checker.** `scripts/bench_static.py` now asserts that every positional command outside `LOADED` is in the retry. Is that check sound, or is it still tautological?
3. **Remaining blind spots.** The generator and the checkers both read commands through a `_box()` parser. Is there any command type that parser still does not understand, and would that hide a real defect?
4. **IP compliance.** `docs/IP-RULES.md`. Place names are allowed. Character names, dragon names in ids, series titles in ids, official art, and book text are banned.

---

## Context

A Minecraft Bedrock fan map. Python emits `.mcfunction` files. The world is flat.

Three audits so far:

- Audit 1 found the far retry dropped all air. Fixed.
- Audit 2 found the far retry dropped all summons, because `_box()` read only `setblock` and `fill`. Fixed in `e2acf93`, along with five smaller findings.
- This is audit 3, on the fixed tree.

Measured on this tree: 32 stages, 1595 build commands, 39 summons (39 guarded in the far files, 0 guarded in the stage files), air volume 34,328 against an 80,000 gate, 26 far files.

Gates: `validate.sh`, `node --check main.js`, `package.sh`, `test_release.py`, `bench_static.py`. All pass on this commit.

---

## Already ruled out

- Audit 1's items are closed. Do not re-report them.
- `manifest.json` keeps `@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0. Beta APIs are off.
- No Bedrock client has run. Do not ask for one. Report only what the commands prove.
- The canon facts in `docs/CANON.md` were verified separately.
- Bedrock `tickingarea add circle` takes its radius in **chunks**, not blocks. The four radius-4 circles cover the whole map. This was raised wrongly before; do not raise it again.

---

## Requirements

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
