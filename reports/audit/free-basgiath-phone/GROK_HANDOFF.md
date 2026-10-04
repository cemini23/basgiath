# Free audit — Grok handoff (readonly orchestration)

You are **auditor #1 and orchestrator** for a Cemini **free-audit**.

**Mode:** `code-debug`
**Workspace:** `/Users/claudiobarone/Projects/dragon-rider-map`
**Pack:** `/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/pack-free-basgiath-phone`
**Out dir:** `/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/free-basgiath-phone`

## Hard rules

- Readonly — do **not** edit product code or configs. Write only under `/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/free-basgiath-phone`.
- **No secrets** in prompts or reports (no `.env`, tokens, keys).
- Always-approve / skip-permissions is intentional for this readonly run.
- Free OpenRouter models may log prompts — keep the pack free of credentials.

## Pre-selected free OpenRouter models (≥2, excludes DeepSeek/Grok)

- `thinkingmachines/inkling-small:free` (family=thinkingmachines, ctx=1048576)
- `nvidia/nemotron-3-ultra-550b-a55b:free` (family=nvidia, ctx=1000000)

## Your steps (do in order)

### 1) Your auditor report

Read `/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/pack-free-basgiath-phone/PACK_INDEX.md` and `/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/pack-free-basgiath-phone/audit_prompt.md` (and listed artifacts).
Write your own audit to:

`/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/free-basgiath-phone/auditor-grok.md`

Use the required output format from the audit prompt (Verdict / Findings / Root cause / Confidence / Unique angle).
Lens for this mode: see skill `reference.md` (Grok column).

### 2) Non-Grok legs (claude-ds + free OR)

Run from the workspace:

```bash
python3 "/Users/claudiobarone/.cursor/skills/free-audit/scripts/run_non_grok_legs.py" \
  --pack "/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/pack-free-basgiath-phone" \
  --out "/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/free-basgiath-phone" \
  --models-json "/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/free-basgiath-phone/free_models.json" \
  --mode "code-debug"
```

This writes `auditor-claude-ds.md` (DeepSeek V4 Flash / claude-ds slot) and `auditor-or-*.md` for each free model.

If DeepSeek key is missing, note it in SYNTHESIS and continue with free OR + your report.

### 3) Synthesize

Write Glasswing rollup to:

`/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/free-basgiath-phone/SYNTHESIS.md`

Use this structure:

```markdown
# Free audit — Basgiath phone build

**Mode:** code-debug · **Auditors:** Grok + claude-ds + free OR
**Pack:** `/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/pack-free-basgiath-phone` · **Out:** `/Users/claudiobarone/Projects/dragon-rider-map/reports/audit/free-basgiath-phone`

| Slot | Channel | Model | Verdict |
|------|---------|-------|---------|
| 1 | grok | grok-cli | … |
| 2 | claude-ds | deepseek-v4-flash | … |
| 3 | openrouter-free | … | … |
| 4 | openrouter-free | … | … |

## Consensus (≥2 auditors agree)
## Unique
## Conflicts (Glasswing — do not silently pick)
## Recommended fix order
## Verdict rollup
**Overall:** SHIP | SHIP-WITH-FIXES | REWORK | REJECT — one paragraph
```

### 4) Stop

When `SYNTHESIS.md` exists, you are done. Do not implement fixes unless the handoff explicitly says so (default: report only).

## Skill docs (optional)

- `/Users/claudiobarone/.cursor/skills/free-audit/SKILL.md`
- `/Users/claudiobarone/.cursor/skills/free-audit/reference.md`
