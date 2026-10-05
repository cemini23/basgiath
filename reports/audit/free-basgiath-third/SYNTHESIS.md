# Third audit — Basgiath at e2acf93

**Mode:** code-debug · **Pack:** `reports/audit/pack-free-basgiath-third` · **Out:** `reports/audit/free-basgiath-third`

**Target:** commit `e2acf93`, whole project.
**Models:** `meta-llama/llama-4-scout` (1.31M ctx) · `xiaomi/mimo-v2.5-pro` (1.05M ctx) · `openai/gpt-5.6-luna-pro` (1.05M ctx). Paid, same tier as round 2, families not used in round 2.
**Grok:** out of credits. The orchestrator wrote this rollup.

| Slot | Model | Verdict | Usable? |
|------|-------|---------|---------|
| 1 | meta-llama/llama-4-scout | PASS | **No** — template noise |
| 2 | xiaomi/mimo-v2.5-pro | PASS | Yes |
| 3 | openai/gpt-5.6-luna-pro | **FAIL** | Yes |

**Overall: FAIL.** One confirmed High defect that audits 1 and 2 both missed.

## Slot 1 is not an audit

llama-4-scout echoed the template. Its verdict line reads `PASS | WARN | FAIL — The project build a coherent, playable Bedrock world.` — it left the enum in place. Every finding is `INFO` and restates the task. It cites functions that are not in the pack. Discount it.

## Confirmed High findings

### H1 — one summon uses absolute coordinates

`scripts/zones/dorms.py` builds the rider stand as a raw string:

```python
ctx.add(
    'summon armor_stand "A rider kneels and the dragon decides." '
    f"{x0 + 4} 0 {(z0 + z1) // 2}"
)
```

It never passes through `rel()`. Every other placement in the project is anchor-relative. The emitted line proves it:

```
stage file:  summon armor_stand "A rider kneels and the dragon decides." 130 0 105
other:       summon armor_stand "wing1_flame_squad1" ~124 ~1 ~36
```

The build places the college at the player's feet, so the anchor is the player. A stand at world `(130, 0, 105)` lands inside the dorm only when the player happens to stand at the origin. Anywhere else it is ~45 blocks off.

The far retry carries the same wrong coordinates. **A guard cannot fix a position.**

GPT-5.6's unique angle is worth keeping: the summon guard can be perfectly idempotent while still spawning the entity in the wrong place.

### H2 — the IP rule and the IP doc disagree with each other

`docs/IP-RULES.md` rule 3 says: *"Character names are banned everywhere."*
`docs/CANON.md` line 220 lists fifteen of them: *"Violet, Xaden, Dain, Mira, Lilith, Brennan, Rhiannon, Imogen, Garrick, Bodhi, Sloane, Ridoc, Sawyer, Liam, Jack."*
`scripts/test_release.py` scans only `addon/` and `scripts/`, so the docs are unenforced.

The list is a **denylist** — the doc names them in order to forbid them. That is normal practice and low risk. The defect is the word "everywhere", which the doc contradicts. The rule is what is wrong, not the list.

GPT-5.6's suggested fix — delete the names from the docs — would leave a naming policy that cannot name what it bans. Rejected. Reword the rule to scope it to the map, the pack, and the shipped strings.

## Confirmed informational findings

`xiaomi/mimo-v2.5-pro` passed the commit and added two precise notes. Both verified:

- The `execute`-guarded retry lines return `None` from `_box()`, so `is_far()` cannot see their position. This is **safe by design**: `bench_static.assert_far_retry()` compares the written files as strings, not through the parser. Two layers — parsing to generate, string equality to verify.
- `_box()` reads the **last three tokens** of a summon as coordinates. Bedrock allows optional `spawnEvent` and `nameTag` after the position. No summon in this tree uses them, so no defect fires today, but a future one would silently shift the box.

GPT-5.6 raised the same parser point as a Medium: `_box()` understands plain `setblock`, `fill`, and `summon`, but not a wrapped `execute … run setblock`. No such command is emitted today.

## Recommended fix order

1. **H1.** Make the dorm summon anchor-relative. Use the `rel()` helper, or emit `~{x0+4} ~ ~{(z0+z1)//2}`.
2. **H2.** Reword `docs/IP-RULES.md` rule 3 so the character-name ban names its scope, and say the denylist lives in `docs/CANON.md`.
3. **Info.** Document that `_box()` covers the three plain forms only, and that the checker verifies by string comparison for that reason. Add a fixture so a wrapped positional command cannot slip in unnoticed.

## Verdict rollup

**Overall: FAIL.** The entity-spawn retry itself is correct and idempotent, and two of three models confirmed the checker is no longer tautological. One summon is misplaced, and one policy sentence contradicts the policy. Both are small, precise fixes.
