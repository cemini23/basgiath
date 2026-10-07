# Audit 2 — cross-edition. Status: RAN. 1 of 3 findings survived, 2 refuted.

**Date:** 2026-10-06 · **Scope:** whole project, Bedrock + Java · **Cost:** $0.00

## Lanes

| Model | Result |
|---|---|
| `nvidia/nemotron-3-ultra-550b-a55b:free` | **Answered.** 25-row table, 110k prompt tokens. The main report. |
| `nvidia/nemotron-3-super-120b-a12b:free` | **Answered.** One finding, refuted below. |
| `inclusionai/ling-3.1-flash` | HTTP 429, rate-limited. |
| `google/gemma-4-26b-a4b-it:free` | HTTP 429, rate-limited. |

Budget was $0.75. It was not needed: the free pool answered, so **$0.00 was spent**.
No paid model was used, and therefore **no model from outside the writer's family gave a
verdict.** That is a real gap against the prompt's rule for Audit 2, stated here rather
than glossed over.

## Findings that survived

**1. The Bedrock-only id guard did not scan Java sources.** *(Fixed.)*

`check_no_bedrock_ids_in_the_tree` in `scripts/test_editions.py` walked
`java/src/main/resources/**/*.mcfunction` only. The mod's own `.java` sources were never
scanned, so a Bedrock-only id could be named in Java code and pass. The one occurrence was
a comment, which has been reworded; the check now scans both trees.

## Findings refuted

**2. "tellraw is converted to a title actionbar on Java."** *(refuted)*

Counted in both emitted files: `tellraw` appears **6 times in each edition**. Bedrock has
`titleraw @s actionbar` ×2 and `titleraw @s title` ×1; Java has `title @s actionbar` ×2 and
`title @s title` ×1 — a faithful one-to-one map. The auditor saw the Java `title` lines and
assumed they came from `tellraw`.

**3. "The Java chain has two `positioned` and the second shifts the wind box."** *(refuted —
hallucinated evidence)*

The auditor quoted `generated/live.mcfunction:3` as containing both
`positioned ~15 ~33 ~19` and a relative selector `x=~4,y=~32,z=~14`. Line 3 has no relative
selector in either edition; the selector it quoted belongs to line 7. It merged two lines to
manufacture the conflict. `grep -c "positioned.*positioned"` over every Java function: **0**.

## Findings noted and dismissed, with reasons

| Claim | Why it is not a finding |
|---|---|
| `displayClientMessage(c, true)` is "a chat overlay, not an action bar" | The boolean selects the action bar. This is the correct Java API. |
| `Vault` `stack.is(item)` may miss components | `ItemStack.is` is the right test and what vanilla uses. |
| `Keepers` tick countdown "drifts" vs a timeout | Both are 60 ticks. A tick countdown is the more correct of the two. |
| The smoke test builds at world spawn, not at a player | Deliberate, documented, and the only position guaranteed loaded headlessly. |
| Dropping `on_area_loaded` means the far pass never runs | `open` calls every far stage; the far pass does run. |
| `bench_static` does not test the Java datapack | True, but the Java smoke test covers the equivalent ground by running the real server. |

## What this audit could not see

The two refutations are the finding. **Both free audits this session produced a confident,
well-formatted, wrong "High" finding** — one misread its own quoted evidence, one invented
the evidence. Neither was caught by the model; both were caught by checking the claim
against the file. An audit report is a hypothesis, not a result.

**No independent family verdict exists on `java/com/basgiath/*.java`.** The prompt asks for
Audit 2 to be run by a different family than the writer. That did not happen here, and this
audit should be repeated with a non-NVIDIA, non-DeepSeek model before the Java release is
called audited.
