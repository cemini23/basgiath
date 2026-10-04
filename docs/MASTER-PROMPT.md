# Master prompt — Basgiath swarm build

Paste this whole file into the agent you choose. It is written for a Grok Build or Claude Code session that can shell out.

---

## Role

You are the build orchestrator for the `dragon-rider-map` repo. You do not write the bulk code yourself. You scope the work, fan it out to the right model per task, integrate the result, audit it, and fix what the audit finds.

Work from the repo root: `/Users/claudiobarone/Projects/dragon-rider-map`.

## Read these first

| File | Why |
|------|-----|
| `docs/CANON.md` | The seven story beats, the canon numbers, the art inventory, the naming table |
| `docs/IP-RULES.md` | The non-negotiable fan-project rules. This file wins on any conflict |
| `DESIGN.md` | The current four-zone spec, the scope cuts, and the interface pins |
| `scripts/build_map.py` | The geometry generator. All world code flows from here |
| `scripts/test_release.py` | The build gate. It currently bans book names. It must change |
| `briefs/2026-10-04_canon-verification.md` | What two free models already checked |
| `BUILD_CHECKLIST.md` | The install and playtest steps |

## Goal

Turn the current four-zone map into the canon seven-beat world, in canon order:

Parapet, Formation, College, Gauntlet, Presentation, Threshing, Signet.

The gaps are listed in `docs/CANON.md` under "The current build against canon". Build as many as you can, in this priority order:

1. **Threshing** — rework the valley and add the event. Highest value.
2. **Courtyard and Formation** — wall ring, roll call, unit structure.
3. **Citadel** — rotunda, keep, dorm block, classrooms.
4. **Gauntlet** — the cliff, the five switchbacks, the obstacles.
5. **Flight field and Presentation** — box canyon, dais, bleachers, the walk.
6. **Signet move** — move the trigger from the plaza stone to after the bond.
7. **Docs and tests** — README, DESIGN, and the naming test.

## Hard constraints

These are not negotiable. Every agent must respect them.

- **Platform:** Minecraft Bedrock, `@minecraft/server` 2.0.0 and `@minecraft/server-ui` 2.0.0. Do **not** bump the versions. Do **not** enable Beta APIs.
- **No custom dimension.** Bedrock custom dimensions are experimental and void-only. Use the Overworld plus teleports.
- **No custom block art.** Vanilla blocks only.
- **Budget:** each `stage_NN.mcfunction` holds at most 50 commands. Each `fill` holds at most 32768 blocks. Total air commands stay under 80000.
- **Original code.** No copy-paste from another addon.

### IP rules — read every time

- No official art, no book covers, no map illustrations, no logos. Build from vanilla blocks only.
- No book text. Write original lines. The keep arch line in the canon file is **book text**. Replace it with an original line.
- Naming table:

| Category | Allowed |
|----------|---------|
| Place names | Yes: Parapet, Basgiath, the Vale, the Gauntlet, the Citadel, the flight field, Navarre, the Iakobos River, Aretia, Morraine |
| Favourite dragons | Yes, only with a lookalike model that matches the canon colour and tail type |
| People names | Never |
| Series and book titles | Title only, never in file ids, entity ids, or pack strings |
| Official art, book text | Never |

## Lanes

Use the cheapest lane that can do the job. Do not use frontier models. Claude and OpenAI are banned on this run.

| Lane | How to invoke | Use for |
|------|---------------|---------|
| Grok Build / Grok CLI | This session. `grok` CLI via `handoff-to-grok` | Orchestration, integration, the hardest merge work. **Budget: about 4% of the weekly limit. Spend it only on integration.** |
| DeepSeek Flash | `claude-ds -Prompt "<task>"` | Zone implementation. Cheap and strong at code |
| OpenCode free | `opencode run --auto --dir <dir> --model free "<task>"` | Zone implementation, second opinion |
| OpenRouter free | `pwsh -File ~/Projects/agent-toolkit/scripts/ask-openrouter.ps1 "<task>"` | Docs, tests, small code, review |
| OpenRouter paid cheap | `ask-openrouter.ps1 -Model <id> "<task>"` | The integrator, and any task that needs more than free can give |
| jev-mcp | MCP server `jev` via `scripts/mcp_jev.sh` | Optional. Only to screen fetched text, classify, or check a claim. Skip it if no agent fetched external text |
| route-task | `route-task "<task>"` | The fix phase. It picks the lane for you |
| runpod MCP | In Grok Build | Smoke test in a clean Linux container |

### Model selection rules

- Never hardcode a free model id. The live catalog moves. Get ids from `~/Projects/agent-toolkit/.cursor/skills/free-audit/scripts/select_free_or_models.py`.
- For the paid integrator, pick the cheapest model in the DeepSeek or Qwen coder family from the live OpenRouter catalog. Check the catalog first, then choose. Do not guess an id.
- Keys live in `~/.cemini/llm-routing.env` and `~/Projects/OSINT WORKSPACE/.env`. The scripts read them. Do not print a key.

## Phase 0 — Refactor for parallel work

Do this **first**, and do it alone. One agent. This unlocks everything else.

The problem: every zone writes into the same `scripts/build_map.py`. Parallel agents would collide.

The fix: split `build_map.py` into zone modules under `scripts/zones/`. Give them one fixed interface:

```python
def build(ctx) -> list[str]:
    """Return a list of Minecraft commands."""
```

Each zone module owns one region and the stage-number range assigned to it. `build_map.py` keeps the driver, the coordinate constants, and the stage-file writer. It imports the zone modules and calls them in order.

Seed the split with the four current zones, so the tests still pass after Phase 0. Add a `scripts/zones/README.md` that states the interface and the stage-range allocation.

**Do not change the world yet.** Phase 0 is a refactor only. `test_release.py` must pass at the end of it.

## Phase 1 — The swarm

Fan out one agent per zone. Run the independent ones in parallel. Assign by strength:

| Zone | Work | Lane |
|------|------|------|
| Z1 Threshing | Rework the valley into a forested dell. Add the dragon-choice event, the relic mark, the flight trial, and the roll-keeper | DeepSeek Flash, then OpenCode free |
| Z2 Courtyard and Formation | Wall ring (10 thick, 8 tall, one opening). Roll-call beat. Wing, section, squad text | OpenCode free |
| Z3 Citadel | Rotunda shell with four doors. Keep with an original arch line. Dorm block. Classrooms | DeepSeek Flash |
| Z4 Gauntlet | Cliff, five switchbacks, six obstacles, safety ropes with a time penalty | DeepSeek Flash |
| Z5 Flight field and Presentation | Box canyon, dais, bleachers, the footpath walk | OpenCode free |
| Z6 Signet move | Move the trigger in `addon/behavior_pack/scripts/main.js` and the zone code from the plaza stone to after the bond | DeepSeek Flash |
| Z7 Docs and tests | Rewrite the naming gate in `test_release.py` to match the table. Update `README.md` and `DESIGN.md` to the seven beats | OpenRouter free |

Rules for every zone agent:

1. Read `docs/CANON.md` for your zone before you write code.
2. Touch only your zone module and your stage-range files.
3. Respect the command and fill budgets.
4. Do not rename the coordinate constants.
5. Return a short report: what you built, the files you touched, the commands you ran, and what you could not do.

Collect each report. Do not let any agent edit another agent's file.

## Phase 2 — Integrate

One agent, on Grok or on the cheapest strong OpenRouter paid model. This is the "bring it together" step.

1. Wire the zone modules into `build_map.py` in canon order.
2. Resolve the stage-range collisions.
3. Run the build and fix the errors.
4. Regenerate `dist/basgiath.mcworld`.
5. Confirm the world matches the canon order end to end.

## Phase 3 — Free audit

After the work is frozen, run the audit. Use the free-audit skill.

- Skill: `~/Projects/agent-toolkit/.cursor/skills/free-audit/`
- Mode: `code-debug`
- Target: the full diff since commit `5e61f75`
- Auditors report. They do not edit.

If the skill is not available in your runtime, drive its scripts directly:

```
select_free_or_models.py      # pick the two free legs
build_audit_pack.py           # pack the diff
prepare_free_audit.py         # write the handoff
run_non_grok_legs.py          # run the non-Grok auditors
```

Each auditor returns a verdict (PASS, WARN, FAIL), a findings table, a root cause, confidence, and one unique angle.

## Phase 4 — Fix and route

1. Read the audit synthesis.
2. Rank the findings: critical, then warning, then info.
3. Fix the critical and warning findings.
4. Route the fixes with `route-task`, as recommended.
5. Re-run the audit on the fixes if the criticals were many.
6. Re-run the gates. The run is not done until they pass.

## Smoke test

Use the runpod MCP to spin a clean Linux container with Python 3 and Node 20, then run:

```
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh
python3 scripts/test_release.py
```

Report the result. A green run in a clean container is the proof.

## Verify — the gates

```
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh
python3 scripts/test_release.py
```

All four must pass. `package.sh` must write `dist/basgiath.mcaddon` and `dist/basgiath.mcworld`.

## Deliverables

1. The refactored `scripts/zones/` layout.
2. The new and changed zone modules.
3. A green gate run.
4. `reports/` holding: the zone reports, the audit pack, the auditor files, and the synthesis.
5. A short finish report in `briefs/` that states the beats built, the beats skipped, and the evidence.

## Never

- Never use a frontier model (Claude, OpenAI) on this run.
- Never print or commit an API key.
- Never copy official art or book text.
- Never let two agents write the same file at the same time.
- Never mark a beat done without a passing gate.
- Never `git push` unless the operator asks.
