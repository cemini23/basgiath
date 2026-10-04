# Basgiath static bench — free audit (readonly)

You are one auditor in a **low-cost multi-model free audit**.

**Mode:** `code-debug` · **Your slot:** `{{MODEL_SLOT}}` · **Readonly** — markdown report only; no edits; no secrets.

---

## Mission (single sharp question)

Does the new bench actually assert what it claims, or does it pass when the world is broken? Specifically, if the Parapet were deleted from `scripts/build_world.py`, would any automated check fail? If the answer is no, say whether the bench is decoration.

---

## Context

This is a non-monetized Minecraft Bedrock fan map. The college is not stored as blocks in `dist/basgiath.mcworld`. `scripts/build_world.py` writes a flat `level.dat` plus the behavior pack and the resource pack. A player later runs `/function basgiath/build`. `scripts/build_map.py` writes the stage functions. `parapet()` in that file places a one-block span at y=32, z=20, x=15 through x=77, with air at x=45 and x=46.

`scripts/bench_static.py` is the new unattended check. It replays `setblock` and `fill` from `stage_*.mcfunction`, then checks the span, the gap, the fall, a walk from the start, the lodestone, two spawn commands, the dragon id, and the world header. It then mutates a copy of those commands and expects the checker to fail for a deleted span, a filled gap, and a safety floor. CI runs this script. It does not run `scripts/bench_bds.sh`.

`scripts/bench_bds.sh` is a Linux-only Bedrock dedicated server smoke. It was not executed. No container was started. No RunPod resource was created. This machine has no Docker.

A local run of `python3 scripts/bench_static.py` printed:

```
world header ok; leveldb files in the zip: 0
proof ok: the Parapet blocks were deleted
proof ok: the two-block gap was filled
proof ok: a safety floor was added under the span
static bench ok: 61 Parapet blocks, gap at x=45 and x=46
```

`bash scripts/validate.sh`, `python3 scripts/test_release.py`, and `bash scripts/package.sh` also exited 0 after the bench was added.

---

## Already ruled out

- Do not ask for client-modification code.
- Do not treat a manual playtest as an automated check.
- The Bedrock server script has no run log. Do not invent a server result.
- No secrets belong in the report.

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
