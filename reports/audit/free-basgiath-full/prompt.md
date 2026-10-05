# Basgiath — full project re-audit (readonly)

You are one auditor in a **low-cost multi-model audit**. This is a re-audit after a fix.

**Mode:** `code-debug` · **Readonly** — markdown report only; no edits; no secrets.

---

## Mission (single sharp question)

**Would this project build a coherent, playable Bedrock world, and is anything left wrong?**

Answer with a verdict, then rank what you find. Cover these four in order:

1. **Correctness.** Does the generator emit a world that matches the design? Any bug that breaks a walk, a fall, a building, or a stage?
2. **The two-pass build.** The generator emits `stage_*.mcfunction` (near pass) and `far_*.mcfunction` (a retry for chunks a phone has not loaded), with `fill_far.mcfunction` running on area load. Is that design correct and complete after the fix?
3. **IP compliance.** Does any file break `docs/IP-RULES.md`? The rules allow place names, allow a favourite dragon name on a lookalike model, and ban character names, series and book titles in ids and strings, official art, and book text.
4. **Anything else.** Dead code, drift between docs and code, or a claim in a doc that the code does not support.

---

## Context

A Minecraft Bedrock fan map for the Empyrean series. Python generates `.mcfunction` files. A behavior pack holds a script UI. The world is flat.

Recent history, in order:

- Phase 0 split `scripts/build_map.py` into `scripts/zones/` behind a `build(ctx)` interface.
- Phase 1 wrote seven zones: parapet, quad (Formation), dorms (College), gauntlet, flight (Presentation), valley (Threshing), signet.
- Phase 2 wired them into `geometry()` in canon order and joined the zone live lines.
- A free audit failed Phase 2. The far retry dropped every air fill. The far pass is the only place those commands run for an unloaded chunk, so the air never landed and hollow buildings kept solid insides.
- Phase 4 fixed it: it cut a 34,272-block no-op chasm carve, restored the retry, added an air-count assert, and taught `bench_static.py` to replay the phone path.

Known numbers on the current tree:

- 32 stages, 1595 build commands.
- Air volume counted by the gate: 34,328 (limit 80,000). It was 84,376 before the fix.
- The far retry holds 217 air lines across 25 far files.
- Gates: `validate.sh`, `node --check main.js`, `package.sh`, `test_release.py`, `bench_static.py`.

Where the money is: read `scripts/build_map.py` first, then the zones, then the tests.

---

## Already ruled out

- The zone modules were audited and are inside budget.
- `manifest.json` keeps `@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0. Beta APIs are off. Do not raise that.
- No Bedrock client ran. Do not ask for one. Report only what the emitted commands prove.
- The canon facts in `docs/CANON.md` were checked by two free models separately.

---

## Data pack files

Grok CLI may open these paths with Read tools. **HTTP auditors** receive the same files **inlined** — you must not emit tool calls.

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
