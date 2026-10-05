<!-- model=anthropic/claude-opus-5.5 channel=openrouter-free ts=20261005T0256Z -->
<!-- degraded-empty-or-tool-stub -->

I need to produce a careful audit under 1500 words, so I'm digging for real issues. Looking at the world config, I notice GameType is set to creative with achievements disabled, but the build script only forces adventure mode on currently connected players via a command rather than setting ForceGameType — meaning anyone joining later, including through LAN or multiplayer, would spawn into creative mode instead.

I'm also checking adventure-mode interactions like lodestones and lecterns, confirming commands work fine since cheats are enabled, and verifying the difficulty, fall damage, keepinventory, and mob-spawning settings all align with the intended design. The time and weather settings look consistent with a static midnight scene, and I'm now checking whether the flat world's spawn height actually lines up with the generated terrain layers so players don't spawn inside blocks or falling through air.

Looking closer at relative coordinates, the build's anchor points and ground fills seem to line up correctly with the computed spawn Y, and the ticking area radius covers the build fine. The bigger concern is a version mismatch: NetworkVersion 827 suggests the world was last touched by 1.21.100, but lastOpenedWithVersion and the README say 1.21.90, which could cause a client on 1.21.90 to flag the world as newer and possibly block loading.

I'm also checking other compatibility flags: baseGameVersion is "*" so it's not locked to a specific release, MinimumCompatibleClientVersion is set appropriately, and multiplayer/LAN settings look standard with ForceGameType off so joiners default to creative. One thing I want to verify is who the executor context is for the scheduled function that raises terrain — since it runs without a player trigger, using @p or @a inside it could behave unpredictably in a fresh multiplayer session.

Checking finish() gamerule and spawnpoint lines — since they're non-positional, they run in the stage pass regardless of far/near logic, which seems fine. The setblocks for pressure plates in finish() are far from the box so they retry, but they're purely decorative with no redstone connected, so they shouldn't affect anything functionally.

I also notice world_resource_packs.json isn't fully verifiable since only the behavior pack manifest was checked, not the resource pack — flagging that as a minor evidence gap. The levelname.txt having a trailing newline is a low-risk cosmetic issue. Now I'm looking at the world spawn coordinates versus where the player is actually anchored in the shipped build.

The spawnpoint command sets spawn relative to the nearest player within the anchor stage, which checks out. Checkpoints then update spawn progressively — cp_east at the tower, cp_quad on the plaza near the pressure plate, and cp_valley at the dragon pad — and since spawn tags are never cleared, this works fine as a one-way progression. I'm also noting the bond trigger zone's coordinate boundaries to verify it lines up with the intended area.

Crucially, I realize the bond trigger zone for `in_center` exactly matches the cp_valley region, meaning the player gets bonded the instant they enter the valley, which actually aligns with the intended open-area design. More importantly, there's no sequencing enforcement at all: since the valley sits just south of the starting point with flat, unobstructed terrain, a player can walk roughly 28 blocks south from spawn and trigger the bond immediately — completely bypassing Parapet, Formation, College, Gauntlet, and Presentation. This means Threshing and Signet become simultaneously reachable, revealing a major gating flaw since the bond trigger is purely positional with no prerequisite checks.

Further checking the Parapet area, I find the chasm floor is walkable stone at ground level, and the Quad's west gate opens right at ground level too, so the player can just walk around the span entirely on flat terrain without ever engaging the tower puzzle — making Parapet fully skippable. This doesn't appear in any known report, so I should flag it. I'm also considering how respawn and spawnpoint behavior interacts with adventure mode settings, particularly what happens if a player dies in the Gauntlet after already triggering the valley checkpoint.

Another finding: spawn points never revert once a checkpoint tag is set, since these tags are permanent and spawn only updates the first time a tag triggers — not based on story progress. So if a player skips to the valley first, then later visits the east tower checkpoint, dying afterward sends them back to the east tower roof instead of the valley, which breaks the intended narrative beat.

The gauntlet scoring system is also broken — #gauntlet is tracked on a single global fake player rather than per-player, there's no timer start/stop logic, and nothing in the datapack actually reads that score, so the armor stand "timekeeper" does nothing meaningful. The rope penalty message only fires once ever since rope_told is never cleared, and the rope hitbox placement is offset by one block in the z-direction from where the ropes actually are.

Checking the next band's walkway and rope heights confirms clearance too—player head stays below the rope at 3.8 vs 4. I'm also verifying the gauntlet's reset command for rope-touch tags, then considering whether the starting band near the College is actually reachable.

Looking at the approach stairs at the stone brick cliff, the step-up heights work fine through leg one into the turn. For the chimney on leg five, I'm checking the ladder placement in the interior air shaft—since no facing state is specified, the default facing_direction=0 might cause the ladder to not attach properly in Bedrock.

Tracing the exit from the chimney top at floor 21, the player climbs out onto leg six's standing surface at y=22, then walks south toward the floor 21 band at z=101. I still need to verify the ramp connecting leg six up to the summit band at floor 25, checking the stair placement across x148..151.

Following that path, the ramp top lands at y=25 with standing height y=26, letting the player walk south into the summit edge at z=105 — this seems consistent with the wall and floor placements for the summit band, and the earlier obstacles on legs four and five at floors 13 and 17 don't interfere with this route.

But I'm now realizing a real problem: the summit at y=26 has no staircase down to the field, and the canyon's east wall tops out at y=32 — so a player reaching the summit via Gauntlet could get stuck, with only a risky 26-block fall as an exit, which exceeds the kill-line threshold of 23. I need to check whether the summit parapet at z=140/x=168 leaves any other way down toward Presentation plaza.

Checking the flight gate posts and beam placement — the gap between x121..123 looks walkable, and the college classroom/rotunda/canyon edges all line up fine. The valley-to-college path checks out too, so I'm setting aside the threshing bond issue and the dragon-summon command tied to each bonded player for now.

Then I notice something important: the bond region overlaps the trial pad itself, so a player could get bonded while already standing on the pad and trigger the "flew" flag without ever actually flying — the flight trial is essentially fake, satisfied just by proximity, especially on respawn. Moving on to the keeper region with the lectern and armor stand near 50,-1,123.

I'm catching a story contradiction: the live dialogue tells the player to say only the colour, but the keeper's lectern form asks for the full name, which also conflicts with the canon instruction to give the roll-keeper the full name. The at_keeper box also overlaps the in_center region, though that seems harmless, and the lodestone placement at 50,-1,130 checks out fine on the cleared valley floor.

I'm noting the bond already triggers its own dragon summon for bonded players, so the summon_dragon command near the pad is redundant, spawning a second dragon — a minor issue but worth flagging, especially since the bonded tag persists afterward. I'm also sizing up the per-tick load on the live script: with roughly 20 rope specs doubled into 36+ lines and armor-stand name lookups via @e selectors, each tick is running something like 60 commands, which could add up performance-wise.

I'm checking the stage/tick control flow — before the build phase, the map_state scoreboard objective doesn't exist yet, so the scoreboard operation throws silently each tick until build creates it and sets #stage to 0, letting live execute. The remaining concern is that live runs immediately once #now equals 0, potentially firing spawnpoint/checkpoint logic even while the player is still mid-teleport.

I'm tracing where the raise effect teleports the player relative to the plaza bounding box — landing around x=120,y=8,z=40 puts them just outside the cp_quad region (x>=124), and falling further settles them near the floor edge, still outside the quad zone, which seems acceptable.

The storm scheduling repeats a weather-thunder command every 200 ticks even with doweathercycle off, which is redundant but harmless since it just resets the thunder duration. I'm now considering whether lightning strikes during the storm could ignite flammable blocks like the oak trees, planks, and stairs in the valley, since doFireTick defaults to true — though I recall fire spread from lightning may depend on difficulty settings, which I need to check for Bedrock versus Java behavior.

Skeleton horse traps are tied to doMobSpawning in Java, so I'll skip that.

There's also a wind push mechanic teleporting the player southward by 0.18 blocks every 4 ticks within a specific zone, which amounts to roughly 0.9 blocks/sec of continuous drift the player must walk against to avoid being pushed off. I need to check whether that teleport command preserves rotation in Bedrock.

The bigger concern is whether the tp call resets vertical momentum mid-jump on Bedrock — if it kills velocity during the 2-block gap jump, that could make the jump unreliable, so this is a medium-low risk area to flag. The wind box also extends into the gap region and the east roof gate zone, but those seem fine to leave as is.

Now I'm looking at the welcome tellraw message instructing the player to touch the stone in the Quad and then run the summon_dragon function.

I notice the Quad's lodestone was relocated to the valley and the plaza area is now chiseled stone bricks, so that instruction is stale and contradicts the current design — worth flagging as a real finding. The fall-back message on the span and the west roof tellraw both seem consistent though.

The "dragon waits on the gold pad" line is also stale since the pad is now moss, so that's another low-priority text inconsistency to note. I'm also checking the welcome_lines logic that gates gamemode changes on the #done score, and the open.mcfunction once-per-open logic using #done, both of which look fine. I'm now looking at whether fill_far gets scheduled twice on area load.

Now I'm tracing whether far-pass summons in the dorms and quad wing stands are properly guarded by name across repeated far retries, and checking if any summon is actually near rather than far — they all seem to be far, which is good. I'm worried about whether stage-pass commands could double-run far summons if the ticking area gets added right before stage calls execute, since that would mean the chunk is loaded during both passes.
