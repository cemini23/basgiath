<!-- model=openai/gpt-5.6-luna-pro channel=openrouter-free ts=20261005T0023Z -->
<!-- retry-after-empty-or-stub -->

### Verdict

FAIL — the build has an absolute-coordinate summon that breaks anchor-relative placement, and the declared IP policy is violated by character names in `docs/CANON.md`.

### Findings

| Severity | Finding | Evidence (file:line or quote) | Fix |
|----------|---------|----------------------------------|-----|
| INFO | The far summon fix is correctly guarded and idempotent. Stage files retain plain summons; far files wrap named summons as `execute unless entity ... run summon ...`. The selector uses the same entity type and name, so rerunning the retry does not duplicate them. | `build_map.py`: “A summon cannot: the stage pass may already have spawned the entity, so the retry guards it with `unless entity`.”; `retry_line()` returns `execute unless entity @e[type=...,name="..."] run summon ...` | No change required. |
| INFO | The retry checker is no longer tautological for supported positional commands. It derives expected retry lines from stage files and compares them exactly, including summon guards; its mutation test removes a guarded summon and expects failure. | `bench_static.py`: “This compares the emitted retry against the far stage commands in their exact retry form”; `assert_far_retry()` | No change required for the current emitted command set. |
| High | One stage summon is absolute rather than anchor-relative. The dorm geometry is generated relative to `build_anchor`, but this armor stand is emitted with `130 0 105`, so it appears at fixed world coordinates instead of inside the dorm at the requested offset. The retry guard may correctly preserve it, but cannot correct its location. | `build_map.py`: “Every later command is relative to it.” `zone-dorms.py`: `summon armor_stand "A rider kneels and the dragon decides." f"{x0 + 4} 0 {(z0 + z1) // 2}"` | Emit `~{x0 + 4} ~0 ~{...}` (or use `ctx.add` with relative coordinates) so the summon follows the anchor like the surrounding geometry. |
| Medium | `_box()` still recognizes only plain `setblock`, `fill`, and `summon`. An `execute ... run setblock/fill/summon` or another positional command would be treated as non-positional and omitted from both far selection and the retry completeness check. Current stage geometry appears to use plain forms, so this is a checker blind spot rather than proven additional loss. | `build_map.py` / `bench_static.py`: `_box()` branches only on `parts[0] == "setblock"`, `"fill"`, or `"summon"` | Parse `execute` wrappers recursively, or reject unsupported positional command forms instead of returning `None`. Add a fixture for wrapped positional commands. |
| High | IP compliance is not clean under the project’s own rule that character names are banned “everywhere.” `docs/CANON.md` contains multiple character names. The release checker only scans `addon` and `scripts`, so it does not detect this documentation violation. | `IP-RULES.md`: “Character names are banned everywhere.” `CANON.md`: “Violet, Xaden, Dain, Mira, Lilith, Brennan...” | Remove character names from shipped documentation or narrow and consistently enforce the policy. Extend `test_release.py`’s name scan to include the governed documentation files. |

### Root cause (if debugging)

The generator’s public contract says all generated placement is relative to the anchor, but the dorm zone bypasses that convention when constructing its summon string. Separately, the retry checker models only three top-level command syntaxes and the IP checker scans only runtime pack sources, leaving documentation outside enforcement.

### Confidence

high — the absolute summon and documented character names are directly visible in the supplied artifacts. Confidence in the parser blind spot is high; whether it hides an additional current positional command would require inspecting generated stage files or adding a wrapped-command fixture.

### Unique angle

The summon guard can be perfectly idempotent while still spawning the entity in the wrong place: guarding entity existence does not compensate for the dorm summon’s absolute coordinates.
