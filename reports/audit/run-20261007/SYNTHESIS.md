# Multi-model audit — the run that worked

**Date:** 2026-10-07 · **Cost:** $0.092 · **Coverage:** `java/com/basgiath/*.java`, all 15 classes
**Result:** 6 of 6 runs answered. 1 finding survived verification. 5 did not.

## Why the earlier audits failed, and what fixed it

Every previous attempt produced either nothing or a confident false positive. The cause was
not the models. It was three things, all in the harness:

1. **Uncapped reasoning.** A reasoning model handed a large open-ended prompt spends its
   entire output budget thinking and returns an empty `content`. This happened to DeepSeek
   three times and to `gpt-5.1-codex` three times. `reasoning.max_tokens` did **not** fix it —
   codex ignored the cap and spent 11,968 tokens thinking anyway, twice, at $0.12 a time.
   The fix was to stop using that model, not to tune it.
2. **Packs too large.** One 49k-token pack gave the model unlimited surface to ruminate on.
   Split into two focused packs of ~15k tokens each, every model answered.
3. **Open-ended questions.** "Find the third silent bug" invites unbounded search. A closed
   checklist of 12 and 13 specific, verifiable properties bounds it.

`scripts/run_audit.py` now retries with a rising thought budget, so a stubborn model is not
simply lost. Three models were dropped for cause: `openai/gpt-5.1-codex` (never answered, 2
attempts, $0.34 total across the session) and both DeepSeek reasoning models.

## What ran

Two focused packs, three models, three families:

| Model | Family | core pack | content pack |
|---|---|---|---|
| `nvidia/nemotron-3-super-120b-a12b:free` | NVIDIA | answered | answered |
| `anthropic/claude-haiku-4.5` | Anthropic | answered | answered |
| `z-ai/glm-5` | Zhipu | answered | answered |

Total $0.092. Two of the three legs were free.

## Findings that survived verification

### 1. A form answer is not tied to the form it answers — CONFIRMED, fixed

`BasgiathForms.open` sent a `formId`, but `Pending` never carried it and `handle` never
checked it. Both `claude-haiku-4.5` and `glm-5` flagged this independently.

The race: the server sends form B while the client is still drawing form A. The player clicks
a button on A. That answer arrives carrying A's id, and `handle` applies it to B's flow — a
click on "Stand your ground" landing on the wrong question, or a vault button firing against
a signet step.

Fixed by tracking the live form id per player and dropping any answer that does not match,
**before** touching the pending flow, so a stale answer cannot destroy the live one.

### 2. `cachedOrigin` was redundant state — fixed

`BasgiathEvents` kept both the anchor's UUID and its position. The position was written and
returned but never consulted: the cache-hit path read the entity again anyway. Removed. The
claimed staleness bug was **not** real — the id lookup fails on a rebuild, so the search
re-runs and the position is always current.

## Findings refuted

| Claim | Model | Why it is wrong |
|---|---|---|
| The anchor cache can serve a stale position | haiku | The hit path re-reads the entity and re-floors it. Only the id is cached. |
| A pending flow can leak forever | nemotron | One entry per player by construction, replaced on the next form, cleared on logout. Bounded by player count. |
| `Vault.withdraw` can give the item free | nemotron | Both writes are in-memory in one tick. A crash loses or saves both; there is no exploitable window. |
| A handler in `BasgiathSmokeTest` can throw | nemotron | It is a test harness. It catches everything and halts the server on purpose. |
| `forget()` is never called (×2) | haiku | It is called from `onLogout` in `BasgiathEvents`, which that model could not see. |
| Codices static-init order is unsafe | haiku (UNSURE) | `BY_ITEM` initialises before the codex fields, and `BasgiathContent` never references `Codices`, so there is no cycle. |

Five of the six UNSURE verdicts were **my packing error** — `Keepers.java` and
`BasgiathEvents.java` were split across the two packs. Verified by hand instead. A next run
should put the keepers and their offsets in the same pack as `buildOrigin`.

## Honest coverage statement

- **Covered:** all 15 mod classes, by three models across three families, on a closed
  checklist of 25 properties.
- **Not covered by this run:** `scripts/editions.py` and the generated datapack. Those were
  audited separately (`pack-free-basgiath-java-core`), and the Bedrock side was covered by
  Audit 2. Neither got a clean pass.
- **Not covered by anyone:** anything that needs a running client — the screens' layout, the
  GeckoLib render, the shaders.
- **Still true:** every audit this session produced plausible findings that did not survive
  checking. That is the argument for verifying mechanically rather than trusting the report.
  The two bugs that actually mattered here — `grass_path` and the relative selector — were
  caught by running the game, not by any model.
