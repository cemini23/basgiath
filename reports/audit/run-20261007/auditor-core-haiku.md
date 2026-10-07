<!-- model=anthropic/claude-haiku-4.5 pack=pack-audit2-modcore usage={'prompt_tokens': 14751, 'completion_tokens': 1949, 'total_tokens': 16700, 'cost': 0.02425104, 'is_byok': False, 'prompt_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 0, 'audio_tokens': 0, 'video_tokens': 0}, 'cost_details': {'upstream_inference_cost': 0.024496, 'upstream_inference_prompt_cost': 0.014751, 'upstream_inference_completions_cost': 0.009745}, 'completion_tokens_details': {'reasoning_tokens': 1433, 'image_tokens': 0, 'audio_tokens': 0}} -->

| # | Property | Verdict | Evidence (file:line) | If WRONG, what Java needs |
|---|----------|---------|----------------------|---------------------------|
| 1 | Correct buses for registrations | OK | java/Basgiath.java:26-31 | |
| 2 | `RegisterPayloadHandlersEvent` on mod bus | OK | java/BasgiathNetwork.java:11-14 | |
| 3 | Entity attributes on mod bus, before summon | OK | java/Basgiath.java:30, java/BasgiathContent.java:67-79 | |
| 4 | Attachments survive restart and death | OK | java/BasgiathData.java:37-53 | |
| 5 | `WingRoster` on overworld, round-trip fields | OK | java/BasgiathData.java:92, 105-133 | |
| 6 | `remember` evicts oldest entry | OK | java/BasgiathData.java:119-133 | |
| 7 | Build origin cache can serve stale position | WRONG | java/BasgiathEvents.java:31-32, 60-65 | Clear `cachedAnchor` and `cachedOrigin` on dimension or level change, or validate the anchor's level |
| 8 | Guard offsets within search radius | UNSURE | java/BasgiathEvents.java:21, 28 | Unable to verify: `Keepers.ALL` not provided in audit files |
| 9 | `deny()` stops block use on 1.21.1 | OK | java/BasgiathEvents.java:195-200 | |
| 10 | Cancel before opening codex form | OK | java/BasgiathEvents.java:210-215 | |
| 11 | Vale teleport call and arrival height | OK | java/BasgiathCommands.java:73-85 | |
| 12 | No unguarded throws in handlers | OK | java/BasgiathEvents.java, java/BasgiathCommands.java, java/BasgiathSmokeTest.java | |
