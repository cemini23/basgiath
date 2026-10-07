<!-- model=anthropic/claude-haiku-4.5 pack=pack-audit2-modcontent usage={'prompt_tokens': 15601, 'completion_tokens': 2661, 'total_tokens': 18262, 'cost': 0.02861694, 'is_byok': False, 'prompt_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 0, 'audio_tokens': 0, 'video_tokens': 0}, 'cost_details': {'upstream_inference_cost': 0.028906, 'upstream_inference_prompt_cost': 0.015601, 'upstream_inference_completions_cost': 0.013305}, 'completion_tokens_details': {'reasoning_tokens': 1887, 'image_tokens': 0, 'audio_tokens': 0}} -->

# Checklist Audit Results

| # | Property | Verdict | Evidence (file:line) | If WRONG, what Java needs |
|---|----------|---------|----------------------|---------------------------|
| 1 | `BasgiathForms.PENDING` cleared by `forget` | UNSURE | Cannot locate invocation of `forget(ServerPlayer)` in provided files | Call `BasgiathForms.forget()` on `ServerPlayer` disconnect event |
| 2 | `handle` compares returned `formId` against pending one | WRONG | BasgiathForms.java:218 — `handle` removes and processes without checking `formId` | Store `formId` in `Pending`, retrieve and compare at line 218 before routing |
| 3 | Signet resolve: all archetypes reachable, tie-break deterministic | OK | Signets.java:36-48, 60-78 — 8 archetypes each offered twice; line 89 tie-break prefers `last` consistently |
| 4 | `Vault.withdraw` charges only after full success | OK | Vault.java:213-216 — early return if `add()` fails or partial; charge only reached on full acceptance |
| 5 | `Vault.depositAll` iterates pre-computed list | OK | Vault.java:171 — `markSlots()` called once, list used in loop; no concurrent modification |
| 6 | `Keepers.tick` safe iteration, one roll call per expiry | OK | Keepers.java:112-127 — explicit `Iterator` with safe `remove()`; `read()` called once per expired entry |
| 7 | `Keepers.read` heard once, not twice or never | OK | Keepers.java:93-94 — tag check and add; BasgiathForms.java:305 clears tag on keeper rename |
| 8 | `Codices.forItem` static init order safe | UNSURE | Cannot verify `BasgiathContent` initialisation sequence — `BY_ITEM` populated at Codices.java:21-29; order relative to `BasgiathContent` unknown |
| 9 | `CodexFlow.answer` rebuild matches button build | OK | BasgiathForms.java:394-401 rebuilds identically to lines 365-372; logic consistent across page states |
| 10 | `FlightHud.STATES` map bounded, states removed on logout | UNSURE | Cannot locate invocation of `FlightHud.forget()` in provided files | Call `FlightHud.forget()` on `ServerPlayer` disconnect event |
| 11 | `DragonEntity.travel` checks rider presence | OK | DragonEntity.java:198 — guards with `controller instanceof Player rider` and `isControlledByLocalInstance()` |
| 12 | `DragonEntity` GeckoLib setup correct | OK | DragonEntity.java:142, 157-167 — cache created once; `registerControllers` and `getAnimatableInstanceCache` both present |
| 13 | `FlightHud.tick` exception safe | OK | FlightHud.java:254-257 — `RuntimeException` caught; no tick loop crash risk |
