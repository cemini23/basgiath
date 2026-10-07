<!-- model=z-ai/glm-5 pack=pack-audit2-modcore usage={'prompt_tokens': 11526, 'completion_tokens': 4054, 'total_tokens': 15580, 'cost': 0.0145522872, 'is_byok': False, 'prompt_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 0, 'audio_tokens': 0, 'video_tokens': 0}, 'cost_details': {'upstream_inference_cost': 0.01469928, 'upstream_inference_prompt_cost': 0.0069156, 'upstream_inference_completions_cost': 0.00778368}, 'completion_tokens_details': {'reasoning_tokens': 3661, 'image_tokens': 0, 'audio_tokens': 0}} -->

| # | Property | Verdict | Evidence (file:line) | If WRONG, what Java needs |
|---|----------|---------|----------------------|---------------------------|
| 1 | Bus registration | OK | Basgiath.java:35-48 | — |
| 2 | BasgiathNetwork bus default | OK | BasgiathNetwork.java:15-19 | — |
| 3 | EntityAttributeCreationEvent bus and timing | OK | Basgiath.java:41; BasgiathContent.java:68-75 | — |
| 4 | Attachment persistence | OK | BasgiathData.java:26-43 | — |
| 5 | WingRoster level and round-trip | OK | BasgiathData.java:73; 77-103 | — |
| 6 | WingRoster eviction order | OK | BasgiathData.java:105-117 | — |
| 7 | buildOrigin cache staleness | OK | BasgiathEvents.java:26-27; 46-72 | — |
| 8 | Box coverage for SIGNET_STONE and Keepers | UNSURE | BasgiathEvents.java:20; 23 | Cannot verify Keepers.ALL offsets — Keepers.java not provided |
| 9 | deny() stops lectern screen | OK | BasgiathEvents.java:107-110 | — |
| 10 | Cancel before codex form | OK | BasgiathEvents.java:112-124 | — |
| 11 | Vale teleport and arrival | OK | BasgiathCommands.java:44; 62-77 | — |
| 12 | Exception safety | UNSURE | BasgiathEvents.java:89-124; 128-140 | Cannot verify without Keepers.java, FlightHud.java, BasgiathForms.java, Codices.java, DragonEntity.java, BasgiathClient.java |
