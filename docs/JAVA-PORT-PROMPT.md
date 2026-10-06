# Basgiath — Java port prompt (2026-10-06)

**Paste this whole file into a fresh session in this repo** (`/Users/claudiobarone/Projects/dragon-rider-map`, GitHub `cemini23/basgiath`).

This is a **separate track** from the Bedrock next-actions prompt. Do not run it in the same session. **Run the Bedrock prompt first.** Reason: the Java port must copy a *correct* generator. Fixing the shipped-map bug on Bedrock first (task 0 of the main prompt) means the port starts from working command output, not from a generator that silently drops blocks.

---

## The one operator decision — answer this before any code

**Does the Java port ship publicly, or is it a capability experiment?**

- **Ship publicly** → the dragon-model rewrite is worth the full effort (GeckoLib animation, Java model JSON, the works). It is the expensive part.
- **Capability experiment** → do the minimum that proves the concept: the generator and one entity on Java. Skip the dragon-model polish.

**Do not start the dragon-model work until this is answered.** Everything else is cheap either way.

## Where the port stands (2026-10-06)

- **Nothing is built yet.** This is a greenfield track.
- **The port is a code port, not a world conversion.** Basgiath does not ship a hand-built world. `scripts/build_map.py` writes `.mcfunction` files and `/function basgiath/build` raises the college at runtime. The dragon comes from `build_dragon_model.py`. The script is one file, `main.js`.
- **Why that matters:** Bedrock worlds are LevelDB and Java worlds are Anvil, so `.mcworld` cannot be imported. Nothing here needs importing — the world is regenerated from source every time. Port the generator, the script, and the entity, and the map reappears on Java.

## Read first

1. `briefs/2026-10-05_java-port-and-tooling.md` — the full research. Read it before planning.
2. `docs/IP-RULES.md` — **non-negotiable. Wins on any conflict.** Unchanged on either edition.
3. `README.md`, `DESIGN.md`, `DISTRIBUTION.md`
4. `scripts/build_map.py`, `scripts/zones/*`, `scripts/build_dragon_model.py`, `addon/behavior_pack/scripts/main.js`

## Target choices (decide once, then sit on them)

- **Loader: NeoForge.** It is the successor to Forge and the feature-rich lane. The map needs a custom entity, custom blocks, and events. Fabric is lighter but weaker here. Use Architectury only if Bedrock and Java share source — they cannot, so do not.
- **Mappings: official Mojang (Mojmap). Never Yarn.** Mojang dropped obfuscation after 1.21.11. Yarn is deprecated and Intermediary ceases to exist. Do not start a new project on Yarn.
- **Version: pick one and sit on it.** Java mods break per release. Hold a stable version rather than chase drops. Note: no mod built for 1.21.11 or earlier runs on the new line without recompilation, so an existing mod is not a free template.

## Task order

Do these in order. Report exactly what you completed if you stop early.

### 1. Scaffold the project

Use the NeoForge **ModDevGradle** plugin and the NeoForge web Mod Generator. Add **MinecraftDev** (IntelliJ plugin, LGPL-3.0) for Mixin and loader setup. Set **Mojmap** mappings. Get an empty mod that builds and loads before porting anything.

### 2. Port the generator (the shared source)

`scripts/zones/*` and `build_map.py` produce Bedrock `.mcfunction`. On Java these become **datapack functions — the same concept, different command syntax** (medium effort).

**Prefer one generator that emits both editions over two generators.** `build_map.py` emitting Bedrock *and* Java functions is a smaller change than maintaining two. Decide the shape here.

Command-syntax differences to handle: block-state syntax, unique ids that differ per edition, entity-summon syntax, and scoreboard (identical concept — low effort).

### 3. Port the script and its persistence

`addon/behavior_pack/scripts/main.js` (`@minecraft/server` 2.0.0) becomes NeoForge event handlers and commands (medium).

| Basgiath today | Java equivalent | Difficulty |
|----------------|-----------------|------------|
| `main.js` events | NeoForge event handlers + commands | Medium |
| `@minecraft/server-ui` forms | A custom `Screen`, or **dialogs** (1.21.6+), or a written book | Medium |
| Player dynamic property (signet result) | NeoForge **data attachments** or a capability | Low |
| World dynamic property (wing roster) | **`SavedData`** | Low |
| `#bond map_state` scoreboard | Java scoreboard — **identical concept** | Low |

### 4. Port the dragon model (the expensive part)

`build_dragon_model.py` emits Bedrock geometry. Java model JSON is a **different format**, so this is a **real rewrite** (high). Use **GeckoLib** — the standard for Bedrock-style animated entities on Java. **Gate this on the operator decision above.**

### 5. CI and publishing

Use the **Minotaur** Gradle plugin (Modrinth) or the `mc-publish` GitHub Action. Keep the same original-wording and denylist rules as Bedrock.

### 6. Wire the extra Java-only scope (only if shipping publicly)

The Bedrock scope cuts stop being necessary on Java: a **custom dimension**, **custom block art**, **custom shaders and fonts**, and **arbitrary code** (the Bedrock Script API is a sandbox; Java is not). Do not build these until the base port is green. They are the payoff, not the start.

## Hard constraints (never break)

- **Same IP rules as Bedrock.** No official art, no book text, no series name. Free, fan-made only. No client-modification code, no anticheat evasion, no hacked clients. `docs/IP-RULES.md` wins.
- **No Yarn.** Official Mojang mappings only.
- **No `.mcworld` import.** Regenerate the world from source.
- **Keep Bedrock shipping in parallel.** This is a parallel track, not a migration. If the port threatens the Bedrock release, stop.
- **Original code and wording.** No copy-paste.

## NEVER

- Do not start the dragon-model rewrite before the operator answers the ship/experiment question.
- Do not write outside `/Users/claudiobarone/Projects/dragon-rider-map`.
- Do not print, write, or commit a key.
- **Do not commit or push** unless the operator asks.

## Verify

- The mod builds and loads on the chosen NeoForge version.
- `/function basgiath/build` raises the college on Java (the generator port works).
- One entity — a summonable dragon — exists on Java (proves the entity port).
- The gate chain for Bedrock stays green (the port must not break the Bedrock build).

## Order to run the two prompts

1. **Bedrock next-actions prompt first** (`docs/NEXT-ACTIONS-PROMPT.md`): fix the map bug, finish the GameTest, extend the bench on RunPod, polish, post the clips.
2. **This Java-port prompt second**, as a parallel track, after the operator answers the ship/experiment question.

The Bedrock release is the priority. The port is additive.
