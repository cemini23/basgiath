# Free audit — full project re-audit

**Mode:** code-debug · **Pack:** `reports/audit/pack-free-basgiath-full` · **Out:** `reports/audit/free-basgiath-full`

**Models:** `z-ai/glm-5.3-flash` · `stealth/space-bunny-alpha` · `xiaomi/mimo-v2.6-pro`
**Grok:** out of credits, so no Grok auditor and no Grok synthesis. The orchestrator wrote this rollup.

| Slot | Model | Outcome |
|------|-------|---------|
| 1 | z-ai/glm-5.3-flash | 28.7 KB of reasoning, **no formal verdict** |
| 2 | stealth/space-bunny-alpha | 29.9 KB of reasoning, **no formal verdict** |
| 3 | xiaomi/mimo-v2.6-pro | **Formal WARN** |

**Overall: WARN.**

## Channel notes

GLM 5.3 Flash and Space Bunny Alpha both led with reasoning instead of the `### Verdict` heading, then ran out of output budget mid-sentence. The harness flagged both DEGRADED. Their reasoning is in the two auditor files and is worth reading, but neither produced a verdict, a findings table, or a root cause. Do not count them as votes.

The fallback slot for each was `thinkingmachines/inkling-small:free`, which returned HTTP 403.

## The one real finding — verified

**MiMo, High: the far retry drops every `summon`.**

`_box()` parses only `setblock` and `fill`. `is_far()` returns `False` for anything else, so an entity spawn can never enter the far set.

The orchestrator verified this on the emitted commands:

```
summon commands: 39
far retry lines by command type: {'fill': 320, 'setblock': 920}
```

**Zero summons are in the retry.** All 39 sit at `x >= 50`, outside `LOADED = 48`. They include:

- The 36 roll-call armor stands at `x=124..132` — the **Formation roll-call beat**.
- `Gauntlet timekeeper` at `~165 ~27 ~110`.
- `Roll-keeper` at `~50 ~-1 ~124` — the Threshing beat.
- A rider stand at `130 0 105`.

On a phone these run in the stage pass against chunks that are not loaded yet, and nothing retries them. The Formation square and two named keepers can simply be absent.

This is the **same class** as the bug Phase 4 fixed: a command class the filter cannot see.

## The root cause, in MiMo's words

> `build_map.is_far`, `bench_static.is_far`, and `bench_static.phone_lines` all derive "what the phone runs" from the same `_box` parser, so the checker and the generator fail in the same direction.

That is the general defect. The generator and the checkers share one parser, so a command class the parser does not understand is invisible to the whole verification stack. The suite can prove it rejects a deleted span. It cannot prove it would reject a dropped spawn.

## Other MiMo findings

| Severity | Finding | Orchestrator note |
|----------|---------|-------------------|
| Medium | `bench_static.phone_lines()`'s `covered == retry` check is tautological — both sides come from the same filter, so it can never catch an ignored command class. | Agreed. This is the blind spot in test form. |
| Medium | The air gate counts `*.mcfunction`, so far air is counted in both passes. | Contested. The phone does run both passes, so it is real work. But re-placing air is a no-op block-wise, so the gate over-states the stall risk. |
| Low | `_NON_SOLID` omits `ladder` and `lectern`, so the walk BFS treats them as solid. | Agreed. A latent checker bug. |
| Low | The courtyard docstring says one opening is the only way through, but the east descent flies over the wall. | Agreed. Doc/code drift. |
| Low | The wait is 20 s in the README, 15 s in the tellraw, and about 19 s in the code. | Agreed. Pick one. |
| Info | IP compliance is clean. No character name, no dragon name, no book text, no official art. Place names only, which rule 3 allows. | Agreed. |

MiMo also flagged that `test_release` hard-codes `"function basgiath/stage_20"`, a stage count the generator chooses. It breaks when a zone grows past 32 stages.

## A claim from the two truncated models — checked and rejected

Both reasoned that the four ticking areas do not cover the valley, the flight field, or the gauntlet's south half, so those far commands fail at every pass. They computed each circle as a 4-block radius.

Bedrock's `tickingarea add circle <x> <y> <z> <radius>` takes the radius in **chunks**, not blocks. Radius 4 is up to 81 chunks. Four circles centred at `(40,40)`, `(120,40)`, `(40,110)`, and `(120,110)` cover `x=-32..192`, `z=-32..182`, which holds the whole map.

The claim is an artifact of the wrong unit. Rejected.

## Recommended fix order

1. **Extend the far filter to positional commands.** Teach `_box()`/`is_far()` to read `summon`, so every entity spawn outside the loaded box joins the retry. This is the High finding.
2. **Make the checker stop sharing the parser.** Have `bench_static.phone_lines()` assert that every positional command outside `LOADED` is in the retry, not only fills and setblocks.
3. Fix `_NON_SOLID` for `ladder` and `lectern`.
4. Reconcile the three wait times to one number.
5. Replace the hard-coded `stage_20` gate with a count derived from the generator.
6. Reword the courtyard docstring, or route the descent through the gate.

Items 3 to 6 are Lows. Item 1 is the one that changes the world.

## Verdict rollup

**Overall: WARN.** The block contract is sound after Phase 4. The entity contract is not. One High finding, verified, of the same class as the bug just fixed.
