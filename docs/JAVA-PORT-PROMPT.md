# Basgiath — Java port prompt (2026-10-06)

**Paste this whole file into a fresh session in this repo** (`/Users/claudiobarone/Projects/dragon-rider-map`, GitHub `cemini23/basgiath`).

This is a **separate track** from the Bedrock next-actions prompt. Do not run it in the same session. **Run the Bedrock prompt first** (it is done). Reason: the Java port must copy a *correct* generator. The Bedrock bug fix means the port starts from working command output, not from a generator that silently drops blocks.

---

## Operator decision — ANSWERED (2026-10-06): the Java port SHIPS PUBLICLY

The Java port is a **public, free release**, published beside the Bedrock addon. Consequences:

- **The dragon-model rewrite gets the full effort** — GeckoLib animation, Java model JSON, textures. This is the expensive part, and it is now warranted.
- **The Java-only scope is in.** A custom dimension, custom block art, and custom shaders and fonts are what make the Java release worth publishing. See task 11.
- **The Java release needs its own distribution** — Modrinth, its own version tags and README — while Bedrock continues on MCPEDL and CurseForge. **Two public releases, one repo, one generator.**
- **The same IP and free rules apply to both.** No money, no Marketplace, no official art or book text.

## Repo layout — DECIDED (2026-10-06): same repo, `java/` subfolder

The Java port lives in **the same repo**, in a self-contained `java/` project. Do **not** create a new repo.

```
dragon-rider-map/            # GitHub cemin23/basgiath — unchanged name
  CLAUDE.md
  docs/                      # IP-RULES.md wins on any conflict
  scripts/                   # SHARED generator — emits Bedrock AND Java output
    build_map.py
    zones/                   # the generator the port reuses
  addon/                     # Bedrock packs (behavior_pack, resource_pack)
  dist/                      # Bedrock build outputs (.mcaddon, .mcworld)
  tests/                     # Bedrock GameTest dev pack
  java/                      # NeoForge project — SELF-CONTAINED, own toolchain
    settings.gradle
    build.gradle
    gradlew
    gradle/
    src/main/java/...
    src/main/resources/      # generated Java datapack functions land here
```

**Rules for this layout:**

- **Gradle stays inside `java/`.** Do not put Gradle at the repo root. Run `cd java && ./gradlew build`. The repo root keeps the existing Bedrock chain.
- **The generator stays in `scripts/`.** It is one source. Do not fork it into `java/`.
- **The Java project consumes the generated output, never the generator source.** When the generator learns to emit Java datapack functions, those functions are copied into `java/src/main/resources/`. The Java project never contains a second copy of generator code.
- **The two toolchains are independent.** Bedrock CI must not run Gradle. The Java CI job must not run the Python gate chain. Add one Java job that does `cd java && ./gradlew build`.
- **`.gitignore`** must add `java/build/`, `java/.gradle/`, `java/run/`.

**Why same-repo.** The port is cheap only because Basgiath ships no hand-built world — one generator raises the college on both editions. Splitting repos duplicates that generator or adds a sync step, which is the "two generators" problem this port is meant to avoid. The Java port **ships publicly**, and it still lives here. Publishing is per-artifact, not per-repo: the Bedrock addon goes to MCPEDL and CurseForge, the Java mod goes to Modrinth, both from this one repo.

## Where the port stands (2026-10-06)

- **Nothing is built yet.** This is greenfield inside `java/`.
- **The port is a code port, not a world conversion.** `scripts/build_map.py` writes `.mcfunction` and `/function basgiath/build` raises the college at runtime. The dragon comes from `build_dragon_model.py`. The script is one file, `main.js`.
- **Bedrock worlds are LevelDB; Java worlds are Anvil.** `.mcworld` cannot be imported. Nothing here needs importing — the world is regenerated from source each time. Port the generator, the script, and the entity, and the map reappears on Java.

## Read first

1. `briefs/2026-10-05_java-port-and-tooling.md` — the full research. Read it before planning.
2. `docs/IP-RULES.md` — **non-negotiable. Wins on any conflict.** Unchanged on either edition.
3. `README.md`, `DESIGN.md`, `DISTRIBUTION.md`
4. `scripts/build_map.py`, `scripts/zones/*`, `scripts/build_dragon_model.py`, `addon/behavior_pack/scripts/main.js`

## Target choices (decide once, then sit on them)

- **Loader: NeoForge.** It is the successor to Forge and the feature-rich lane. The map needs a custom entity, custom blocks, and events. Fabric is lighter but weaker here. Do not use Architectury — Bedrock and Java cannot share source.
- **Mappings: official Mojang (Mojmap). Never Yarn.** Mojang dropped obfuscation after 1.21.11. Yarn is deprecated and Intermediary ceases to exist. Do not start a new project on Yarn.
- **Version: pick one and sit on it.** Java mods break per release. Hold a stable version rather than chase drops. No mod built for 1.21.11 or earlier runs on the new line without recompilation, so an existing mod is not a free template.

## Task order

Do these in order. Finish a whole numbered task before starting the next. Report exactly what you completed if you stop early.

### 1. Scaffold the NeoForge project inside `java/`

Use the NeoForge **ModDevGradle** plugin and the NeoForge web Mod Generator. Add **MinecraftDev** (IntelliJ plugin, LGPL-3.0) for Mixin and loader setup. Set **Mojmap** mappings. Keep every Gradle file inside `java/`. Get an empty mod that **builds and loads** before porting anything. Add the `.gitignore` entries and the one Java CI job.

### 2. Teach the shared generator to emit Java output

`scripts/zones/*` and `build_map.py` produce Bedrock `.mcfunction` today. On Java these become **datapack functions — the same concept, different command syntax** (medium). Change the **shared generator only**; it stays in `scripts/`.

- One generator emits **both** editions. Do not write a second generator.
- Command-syntax differences to handle: block-state syntax, ids that differ per edition, entity-summon syntax. Scoreboard is the same concept — low effort.
- The generated Java functions are copied into `java/src/main/resources/` for the mod to ship.

### 3. Port the script and its persistence

`addon/behavior_pack/scripts/main.js` (`@minecraft/server` 2.0.0) becomes NeoForge event handlers and commands (medium). Lives in `java/src/main/java/`.

| Basgiath today | Java equivalent | Difficulty |
|----------------|-----------------|------------|
| `main.js` events | NeoForge event handlers + commands | Medium |
| `@minecraft/server-ui` forms | A custom `Screen`, or **dialogs** (1.21.6+), or a written book | Medium |
| Player dynamic property (signet result) | NeoForge **data attachments** or a capability | Low |
| World dynamic property (wing roster) | **`SavedData`** | Low |
| `#bond map_state` scoreboard | Java scoreboard — **identical concept** | Low |

### 4. Bring up the first Java world

Build and load the mod. Confirm: `/function basgiath/build` raises the college on Java, and one entity — a summonable dragon — exists. This is the "new Java world" that Audit 1 examines. Do not start the dragon-model polish yet.

### 5. AUDIT 1 — the new Java world, early and cheap

Run this audit on the **new Java code and world**, because all of it is new. Full detail in *Auditing and routing* below.

- **Scope:** everything under `java/`, plus the Java-emitting half of the shared generator.
- **Budget: $0.20 OpenRouter — a ceiling, not a target.** Use the free lanes first. A good free audit that finds the real issues spends close to $0.
- **Purpose:** catch the cheap-to-fix mistakes while the code is young — wrong ids, wrong command syntax, missing persistence, dead paths. A miss here is expensive later.
- The auditor is **not** the writer.

### 6. Fix every Audit 1 finding

Fix all of them. Do not defer. For each fix: change the code, re-run the local checks, and note the fix. Route the work per *Auditing and routing* — **Grok is out of usage**, so use the free lanes and the Flash fallback. Then re-run the whole gate chain.

### 7. Port the dragon model — full effort (public release)

`build_dragon_model.py` emits Bedrock geometry. Java model JSON is a **different format**, so this is a **real rewrite** (high). Use **GeckoLib** — the standard for Bedrock-style animated entities on Java. Because the port ships publicly, do the full job: the model, the animations, and the textures. The dragon is the headline feature of the Java release.

### 8. AUDIT 2 — the whole project (Bedrock + Java), once Java is fully built

Run this only after the Java build is complete. Full detail in *Auditing and routing* below.

- **Scope:** the whole project, both editions — Bedrock pack, generator, script, world, bench, **and** Java.
- **Budget: $0.75.** **Spend it.** This is the audit where you do **not** cheap out. Use the most capable model the budget allows. The operator would rather spend a full dollar now than pay more downstream to fix what a weak audit missed.
- This is the cross-edition audit: it catches Bedrock/Java divergence, the shared-generator seam, and the IP-rule surface on both sides.
- The auditor is **not** the writer. Prefer a different model family than the one that wrote the code.

### 9. Fix every Audit 2 finding; re-run both gate chains

Fix all of them, then re-run the Bedrock chain **and** `cd java && ./gradlew build`.

### 10. CI and publish to Modrinth

Use the **Minotaur** Gradle plugin (Modrinth) or the `mc-publish` GitHub Action. Publish the Java mod under its own version tags and README — free and fan-made, the same stance as Bedrock. Keep the same original-wording and denylist rules as Bedrock. Add the Java build job beside the existing Bedrock jobs; do not let the two chains call each other.

### 11. Wire the extra Java-only scope (it ships publicly)

The Bedrock scope cuts stop being necessary on Java: a **custom dimension**, **custom block art**, **custom shaders and fonts**, and **arbitrary code**. Build these after the base port is green and both audits pass. They are what makes the Java release worth publishing, not the start.

## Auditing and routing

**Two audits. Run them at the two points above. The auditor is never the writer.**

### Audit 1 — new Java world (budget $0.20)

- **When:** after task 4, when the first Java world loads.
- **Scope:** `java/` and the Java half of the shared generator.
- **Lane:** free-first. Use `route-task` / the OpenCode Zen free lane / OpenRouter free. The **$0.20 OpenRouter budget is a ceiling**, not a target — most of a young-code audit should cost nothing.
- **What to look for:** wrong block/entity ids, wrong command syntax, missing or wrong persistence, dead code paths, IP-rule slips, anything the Bedrock side already fixed (do not re-introduce a fixed bug).
- **Output:** a findings list with file and line. Then fix every one (task 6).

### Audit 2 — whole project, Bedrock + Java (budget $0.75)

- **When:** after the Java build is fully complete (after task 7).
- **Scope:** the whole project. Bedrock pack and bench, the shared generator, both scripts, the world writer, the dragon model on both editions, and the Java project.
- **Budget: $0.75 — spend it.** Use the **most capable model the budget allows**. Do not pick a cheaper model to save the budget and miss issues; the operator would rather spend a full dollar now. If the honest answer is that more budget would find more, say so and ask before exceeding.
- **What to look for:** cross-edition divergence, the shared-generator seam (does one edition's output corrupt the other?), persistence correctness, IP-rule compliance on both sides, anything a per-edition audit cannot see.
- **Output:** a findings list with file and line. Then fix every one (task 9).

### Routing — how to send the work

- **Grok is OUT of usage. Do not plan on the Grok lane.** The cheap chain is **OpenRouter free (chat) → OpenCode Zen free (tools) → claude-ds Flash (paid fallback)**.
- `opencode` is installed. Run the OpenCode Zen free sidecar with the prompt in a file (never `$` interpolation in argv):

  ```bash
  cd /Users/claudiobarone/Projects/dragon-rider-map
  opencode run --auto --dir "$PWD" --model free "$(cat /tmp/task.md)"
  ```

  `--model free` (or empty) = the live strongest listed-free coding pick; do not lock one id. `-f` / `--file` **attaches** files. The unified wrapper is:

  ```bash
  route-task -Profile claudio "mid: <the task>"
  ```

- **Keys.** `OPENROUTER_API_KEY` and `DEEPSEEK_API_KEY` are in `/Users/claudiobarone/Projects/OSINT WORKSPACE/.env`. The **jev MCP** details are in the Cursor config if needed. **Never print, write, or commit a key.**
- **Premium only for the plan and the audit.** Write the plan in the premium session; let the cheap lanes implement.
- **Never send secrets or protected IP text to a free OpenRouter or OpenCode model.** They may log or train.

## Hard constraints (never break)

- **Everything stays inside `/Users/claudiobarone/Projects/dragon-rider-map`.** The Java work lives in `java/` under that root. Do not create a sibling repo.
- **Same IP rules as Bedrock.** No official art, no book text, no series name. Free, fan-made only. No client-modification code, no anticheat evasion, no hacked clients. `docs/IP-RULES.md` wins.
- **No Yarn.** Official Mojang mappings only.
- **No `.mcworld` import.** Regenerate the world from source.
- **Keep Bedrock shipping in parallel.** This is a parallel track, not a migration. If the port threatens the Bedrock release, stop.
- **Original code and wording.** No copy-paste.

## NEVER

- Do not publish the Java mod as anything other than a free, fan-made Modrinth release. **Never the Minecraft Marketplace.** No money, no donation, no paid tier.
- Do not skip Audit 1 or Audit 2. Do not defer the fixes from either.
- Do not create a new repository. The port lives in `java/` in this repo.
- Do not fork the generator into `java/`. One generator, in `scripts/`.
- Do not put Gradle at the repo root.
- Do not write outside `/Users/claudiobarone/Projects/dragon-rider-map`.
- Do not print, write, or commit a key.
- **Do not commit or push** unless the operator asks.

## Verify

- `cd java && ./gradlew build` succeeds; the mod loads on the chosen NeoForge version.
- `/function basgiath/build` raises the college on Java (the generator port works).
- One entity — a summonable dragon — exists on Java (proves the entity port).
- **Audit 1** ran and every finding is fixed.
- **Audit 2** ran and every finding is fixed.
- The **Bedrock** chain stays green: `python3 scripts/build_map.py`, `bash scripts/validate.sh`, `node --check addon/behavior_pack/scripts/main.js`, `bash scripts/package.sh`, `python3 scripts/test_release.py`, `python3 scripts/bench_static.py`. The port must not break the Bedrock build.

## Order to run the two prompts

1. **Bedrock next-actions prompt first** (`docs/NEXT-ACTIONS-PROMPT-v2-2026-10-06.md`) — done.
2. **This Java-port prompt second**, as a parallel track. It **ships publicly**, lives in the same repo under `java/`, and runs **Audit 1 → fix → build the dragon → Audit 2 → fix → publish to Modrinth**.

The Bedrock release is the priority. The port is additive.
