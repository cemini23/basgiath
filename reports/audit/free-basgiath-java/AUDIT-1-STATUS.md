# Audit 1 — status: RAN (free + paid). Every finding refuted.

**Date:** 2026-10-06 · **Scope:** `java/` and the Java-emitting half of the shared generator
**Cost:** **$0.286** — $0.071 on `anthropic/claude-haiku-4.5`, $0.215 on `openai/gpt-5.1-codex`.
**This overran the $0.25 ceiling.** The overrun is entirely the codex leg, which returned
nothing at all. See the paid section below.

## Paid run (added after the free pool proved unusable)

The writer of this code is DeepSeek-powered, so the auditor has to come from another family.
Two paid, non-DeepSeek legs were run against the full pack:

| Model | Cost | Result |
|---|---|---|
| `anthropic/claude-haiku-4.5` | $0.071 | **Answered** — one High finding, refuted below. |
| `openai/gpt-5.1-codex` | $0.215 | **Returned nothing.** Spent all 16k output tokens on `reasoning_content` and emitted an empty answer, even with `reasoning.effort` capped at medium. This is the entire budget overrun. |

The "different family from the writer" gap is now **closed in form** — OpenAI and Anthropic
both reviewed the pack. It is not closed in substance: one leg gave a single finding, the
other gave none, and **neither audited `java/com/basgiath/*.java`**. No verdict exists on the
screens, the payloads, the attachments, the SavedData, the HUD, or the entity class.

### The paid finding, refuted

> **High** — `@p` does not exist in Java 1.21.1. Java has only `@s`, `@a`, `@e`, `@r`.
> `open.mcfunction` uses `@p`, so the welcome title silently matches nothing.
> Confidence: **High**.

**Refuted, from evidence already on disk.** `@p` is a core Java selector and always has been.
Decisively: `open.mcfunction:29-32` uses `@p`, and the smoke test asserts that **all 67
generated functions loaded**. A function containing an invalid selector does not half-load —
it is dropped, which is exactly how `grass_path` and the relative-selector bugs announced
themselves. `open` loaded. Therefore `@p` parses.

The auditor's stated grammar was simply wrong. This is the **third** confident, well-formatted
false positive of the session, from a third model family.

## The lanes

| Lane | Outcome |
|---|---|
| `OPENROUTER_API_KEY` | **Present** at line 26 of the operator env file. It was not there when the audit first ran; it appeared later in the session. |
| OpenCode Zen free (`--model free`) | **Unusable.** This `opencode` build (1.18.18) has no `free` alias. |
| OpenCode Zen free, named models | **Did not converge.** `mimo-v2.6-flash-free` ran 35+ minutes and produced a 2721-line trace with no findings. |
| DeepSeek `deepseek-v4-pro` / `deepseek-flash` | **No answer.** Reasoning-first: spend the whole budget on `reasoning_content`, return empty `content`. |
| OpenRouter free, 6 models | **1 of 6 answered.** See below. |

### OpenRouter free legs

| Model | Result |
|---|---|
| `nvidia/nemotron-3-super-120b-a12b:free` | **Answered.** Report at `auditor-or-nvidia-nemotron-3-super-120b-a12b-free.md`. |
| `nvidia/nemotron-3-ultra-550b-a55b:free` | Still reasoning when the run was stopped. Trace kept. |
| `inclusionai/ling-3.0-flash-sante:free` | HTTP 429 — rate-limited upstream (shared pool). |
| `poolside/laguna-s-2.1:free` | HTTP 429 — rate-limited upstream. |
| `google/gemma-4-31b-it:free` | HTTP 429 — rate-limited upstream. |
| `thinkingmachines/inkling:free` | HTTP 403 — "only available on agentic harnesses". |

The free pool was congested for the whole session. `run_audit.py` gained a `provider`
argument for this; it now reaches both endpoints.

## The one finding, and why it is wrong

`nvidia/nemotron-3-super-120b-a12b:free` raised exactly one finding:

> **High** — the `c=` → `limit=` rewrite fails when `c=` is the first argument in a
> selector, because the regex `(?<=[,\[])c=(\d+)` needs a preceding comma or bracket.
> `@e[c=1,type=armor_stand]` would keep the invalid `c=`.

**Refuted.** The lookbehind character class `[,\[]` is "a comma, or a literal `[`". The
bracket case is already in it. Checked directly:

```
'tag @e[c=1] add x'                  -> 'tag @e[limit=1] add x'
'tag @e[c=1,type=armor_stand] add x' -> 'tag @e[limit=1,type=minecraft:armor_stand] add x'
'tag @e[type=armor_stand,name="a",c=1] add x' -> '... limit=1] ...'
```

The auditor read its own quoted evidence and mistook `[,\[]` for `[,\[]`-without-the-bracket.
Its stated test case passes.

## What the audit did find

The earlier partial pass (same family as the writer) found one real latent bug, now fixed:
**two relative boxes on one line would compose.** The hoisted `positioned` moves the
execution position, and a second relative box in the run command would then measure from
the moved position. The generator does not produce this today; `to_java` now stops the
build instead of translating it, with a test.

Fixing that guard exposed a second bug in the guard itself: `return hoisted,
_CHAIN_SELECTOR_RE.sub(...)` reports `hoisted` from before the substitution runs, because a
tuple is built left to right.

## Coverage honestly stated

- **Not audited by any independent model:** `java/com/basgiath/*.java`. The screens, the
  payloads, the data attachments, the SavedData, the HUD, and the entity class have no
  external verdict.
- **No second opinion from a different family.** The prompt's rule for Audit 2 —
  "prefer a different model family than the one that wrote the code" — was not met here
  either; the only usable output came from outside the writer's family but was thin.
- **The block-id, entity-id, particle, and effect tables** were exercised by the free
  lane's own scripting and by the live smoke test, but no report confirms completeness.

## What actually guards this port

The headless smoke test (`./gradlew runSmoke`, 10/10) proves the class of bug this audit
was aimed at, from the other side: every one of the **67 generated functions loads in a
real server**, the stages place the intended blocks, and the dragon is summonable. Both
generation bugs found this session — `grass_path` and the relative selector — were caught
by running the game, not by reading code.

**Audit 1 is not complete.** It should be re-run when the free pool is less congested, with
a model from a different family than the writer, and it should cover the mod classes.
