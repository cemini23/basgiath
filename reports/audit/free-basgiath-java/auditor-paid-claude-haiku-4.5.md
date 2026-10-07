<!-- model=anthropic/claude-haiku-4.5 pack=pack-free-basgiath-java usage={'prompt_tokens': 56365, 'completion_tokens': 3168, 'total_tokens': 59533, 'cost': 0.07148295, 'is_byok': False, 'prompt_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 0, 'audio_tokens': 0, 'video_tokens': 0}, 'cost_details': {'upstream_inference_cost': 0.072205, 'upstream_inference_prompt_cost': 0.056365, 'upstream_inference_completions_cost': 0.01584}, 'completion_tokens_details': {'reasoning_tokens': 2787, 'image_tokens': 0, 'audio_tokens': 0}} -->

# Finding: Silent Selector Failure

| Severity | Finding | Evidence (file:line) | Fix |
|----------|---------|----------------------|-----|
| **High** | `@p` selector does not exist in Java 1.21.1 | `generated/open.mcfunction:9,10` | Replace `@p` with `@a[limit=1,sort=nearest]` |

---

## Root cause

Bedrock has `@p` (nearest player). Java 1.21.1 has only `@s`, `@a`, `@e`, and `@r`. The translation in `scripts/editions.py` passes selectors through unchanged, treating them as "identical on both editions." They are not. A command using `@p` will parse correctly on the Java side but match zero entities, so it silently does nothing.

The title commands in `open.mcfunction` fire when the build is complete, attempting to welcome the player to the map. With `@p` matching nothing, the player sees no welcome message and no indication that anything is wrong.

## Confidence

**High.** The Java 1.21.1 selector grammar is fixed and documented. `@p` is not in it. The command is in the real generated output on disk, not a test fixture.

## Unique angle

This is the category all three bugs share: an id, a syntax element, or a default that moved between the editions. The first was a block id. The second was a selector argument syntax (relative coordinates). The third is a selector prefix itself. The translation handles the first two but misses that selectors are not "identical on both editions"—they have different character sets.
