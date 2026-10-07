<!-- model=poolside/laguna-s-2.1:free pack=pack-free-basgiath-java usage={'prompt_tokens': 49806, 'completion_tokens': 847, 'total_tokens': 50653, 'cost': 0, 'is_byok': False, 'prompt_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 0, 'audio_tokens': 0, 'video_tokens': 0}, 'cost_details': {'upstream_inference_cost': 0, 'upstream_inference_prompt_cost': 0, 'upstream_inference_completions_cost': 0}, 'completion_tokens_details': {'reasoning_tokens': 0, 'image_tokens': 0, 'audio_tokens': 0}} -->

# Audit Report: Basgiath Java Port

## Findings

| Severity | Finding | Evidence (file:line) | Fix |
|----------|---------|----------------------|-----|
| **High** | `tp @s ~ ~ ~0.18` silently does nothing on Java | `generated/live.mcfunction:4` | Translate to `tp @s ~ ~ ~0.18` → `tp @s ~ ~ ~ 0.18` (Java requires a space between `~` and the decimal) |
| **Medium** | `tp @s ~ ~ ~0.18` is not caught by `to_java()` strictness | `scripts/editions.py:233` (the `tp` verb passes through unrewritten) | Add a `tp` handler in `to_java()` that validates coordinate syntax |

## Root Cause

The `tp` command passes through `to_java()` unchanged (line 233 of `editions.py` lists `tp` among the verbs that are "identical on both editions"). However, Bedrock and Java differ in how they parse relative coordinates with decimal offsets.

In Bedrock, `tp @s ~ ~ ~0.18` is valid — the `~0.18` is parsed as a relative coordinate with a decimal offset. In Java 1.21.1, the command parser does not accept `~0.18` as a single token. The `~` and `0.18` must be separated by a space: `tp @s ~ ~ ~ 0.18`.

When Java encounters `tp @s ~ ~ ~0.18`, it fails to parse the command. Since this is inside an `execute ... run` chain, the entire command fails silently — no error is thrown, no entity is teleported, and the player's position is not adjusted. The wind mechanic that this command implements (pushing players back to the ground when they fall off the span) simply never fires.

This is exactly the class of bug the audit was looking for: a command that names a coordinate syntax Java doesn't have, which silently does nothing rather than crashing.

## Confidence

**High.** The evidence is direct:
1. `generated/live.mcfunction:4` contains `tp @s ~ ~ ~0.18`
2. `scripts/editions.py:233` shows `tp` is in the pass-through list
3. Java's command parser requires a space between `~` and decimal values in coordinates

The only thing that would change my mind is if Java 1.21.1 actually accepts `~0.18` as a coordinate token, which would contradict my understanding of Brigadier's coordinate parsing.

## Unique Angle

The `tp` command is listed as "identical on both editions" in the code's own comment, which is precisely why this slipped through. The translation layer assumes that because the verb is the same, the arguments are the same. But coordinate syntax is an argument-level concern, not a verb-level one. The strictness check in `to_java()` never inspects the coordinate tokens of a `tp` command, so it never catches this divergence.

This is also notable because it's the *only* `tp` command in the generated output, and it's the one that implements a core gameplay mechanic (the wind pushback). Every other `tp` in the codebase uses integer offsets or absolute coordinates, which Java handles fine.

## What I Checked

- All `tp` commands in `generated/*.mcfunction` — only `live.mcfunction:4` uses a decimal relative coordinate
- The `to_java()` function in `scripts/editions.py` — confirmed `tp` is in the pass-through list at line 233
- The test suite in `scripts/test_editions.py` — no test covers `tp` with decimal relative coordinates
- All other coordinate syntaxes in the generated files — all use either integer relative coordinates (`~4`, `~-1`) or absolute coordinates, which Java accepts
