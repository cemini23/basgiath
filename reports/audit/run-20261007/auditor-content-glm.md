<!-- model=z-ai/glm-5 pack=pack-audit2-modcontent usage={'prompt_tokens': 12446, 'completion_tokens': 8867, 'total_tokens': 21313, 'cost': 0.0242473176, 'is_byok': False, 'prompt_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 0, 'audio_tokens': 0, 'video_tokens': 0}, 'cost_details': {'upstream_inference_cost': 0.02449224, 'upstream_inference_prompt_cost': 0.0074676, 'upstream_inference_completions_cost': 0.01702464}, 'completion_tokens_details': {'reasoning_tokens': 8496, 'image_tokens': 0, 'audio_tokens': 0}} -->

| # | Property | Verdict | Evidence (file:line) | If WRONG, what Java needs |
|---|----------|---------|----------------------|---------------------------|
| 1 | Pending flow cleanup | OK | BasgiathForms.java:117-119 | |
| 2 | Form ID validation | WRONG | BasgiathForms.java:120-128 | Compare `answer.formId()` against expected ID before processing; store formId in Pending or track expected ID per player |
| 3 | Signet reachability and tie-break | OK | Signets.java:30-37, 80-96 | |
| 4 | Vault withdraw atomicity | OK | Vault.java:87-96 | |
| 5 | depositAll slot iteration | OK | Vault.java:46-55, 72-80 | |
| 6 | Keepers.tick iteration safety | OK | Keepers.java:87-103 | |
| 7 | Rename roll call handling | OK | BasgiathForms.java:181-188, Keepers.java:68-77 | |
| 8 | Codices static init order | OK | Codices.java:17, 33-47 | |
| 9 | CodexFlow action list consistency | OK | BasgiathForms.java:202-233 | |
| 10 | FlightHud state lifecycle | OK | FlightHud.java:49, 119-121 | |
| 11 | DragonEntity rider control | OK | DragonEntity.java:79-81, 97-126 | |
| 12 | GeckoLib implementation | OK | DragonEntity.java:60, 68-70, 82-84 | |
| 13 | Tick handler exception safety | OK | FlightHud.java:89-96 | |
