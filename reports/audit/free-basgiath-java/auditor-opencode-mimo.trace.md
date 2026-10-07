[0m
> build · mimo-v2.6-flash-free
[0m
[0m$ [0mls -la && ls -la generated/ 2>/dev/null | head -50
total 16
drwxr-xr-x@  7 claudiobarone  staff   224 Oct  6 18:43 .
drwxr-xr-x@ 20 claudiobarone  staff   640 Oct  6 18:43 ..
-rw-r--r--@  1 claudiobarone  staff  4350 Oct  6 18:43 audit_prompt.md
drwxr-xr-x@  3 claudiobarone  staff    96 Oct  6 18:43 ci
drwxr-xr-x@ 11 claudiobarone  staff   352 Oct  6 18:43 generated
drwxr-xr-x@  7 claudiobarone  staff   224 Oct  6 18:43 java
drwxr-xr-x@  5 claudiobarone  staff   160 Oct  6 18:43 scripts
total 112
drwxr-xr-x@ 11 claudiobarone  staff    352 Oct  6 18:43 .
drwxr-xr-x@  7 claudiobarone  staff    224 Oct  6 18:43 ..
-rw-r--r--@  1 claudiobarone  staff   4897 Oct  6 18:43 build.mcfunction
-rw-r--r--@  1 claudiobarone  staff   1462 Oct  6 18:43 far_01.mcfunction
-rw-r--r--@  1 claudiobarone  staff  15002 Oct  6 18:43 live.mcfunction
-rw-r--r--@  1 claudiobarone  staff   3715 Oct  6 18:43 open.mcfunction
-rw-r--r--@  1 claudiobarone  staff    137 Oct  6 18:43 run_start.mcfunction
-rw-r--r--@  1 claudiobarone  staff   1502 Oct  6 18:43 stage_01.mcfunction
-rw-r--r--@  1 claudiobarone  staff    454 Oct  6 18:43 summon_dragon.mcfunction
-rw-r--r--@  1 claudiobarone  staff     42 Oct  6 18:43 tick.json
-rw-r--r--@  1 claudiobarone  staff   7727 Oct  6 18:43 tick.mcfunction
[0m
[0m✱ [0mGlob "**/*"[90m 33 matches[0m
[0m
[0m$ [0mwc -l scripts/*.py java/com/basgiath/*.java generated/* ci/ci.yml java/*.gradle java/gradle.properties
106 scripts/build_java_assets.py
     581 scripts/editions.py
     248 scripts/test_editions.py
      54 java/com/basgiath/Basgiath.java
     167 java/com/basgiath/BasgiathClient.java
      63 java/com/basgiath/BasgiathCommands.java
      96 java/com/basgiath/BasgiathContent.java
     187 java/com/basgiath/BasgiathData.java
     226 java/com/basgiath/BasgiathEvents.java
     373 java/com/basgiath/BasgiathForms.java
      37 java/com/basgiath/BasgiathNetwork.java
     257 java/com/basgiath/BasgiathSmokeTest.java
      80 java/com/basgiath/Codices.java
     117 java/com/basgiath/DragonEntity.java
     145 java/com/basgiath/DragonModel.java
     185 java/com/basgiath/FlightHud.java
     134 java/com/basgiath/Keepers.java
     111 java/com/basgiath/Signets.java
     112 java/com/basgiath/Vault.java
      60 generated/build.mcfunction
      50 generated/far_01.mcfunction
      96 generated/live.mcfunction
      33 generated/open.mcfunction
       4 generated/run_start.mcfunction
      50 generated/stage_01.mcfunction
       3 generated/summon_dragon.mcfunction
       5 generated/tick.json
      66 generated/tick.mcfunction
     105 ci/ci.yml
     126 java/build.gradle
      19 java/settings.gradle
      35 java/gradle.properties
    3931 total
[0m
[0m→ [0mRead scripts/editions.py
[0m→ [0mRead scripts/test_editions.py
[0m→ [0mRead scripts/build_java_assets.py
[0m→ [0mRead generated/tick.mcfunction
[0m→ [0mRead generated/live.mcfunction
[0m→ [0mRead generated/build.mcfunction
[0m→ [0mRead generated/open.mcfunction
[0m
[0m$ [0mgrep -ohE '@[a-z](\[[^]]*\])?' generated/*.mcfunction | sed -E 's/\[[^]]*\]//' | sort | uniq -c; echo '--- selector keys ---'; grep -ohE '@[a-z]\[[^]]*\]' generated/*.mcfunction | tr -d '@'[a-z] 2>/dev/null | head -1; grep -ohE '@[a-z]\[[^]]*\]' generated/*.mcfunction | grep -oE '[a-z_]+=' | sort | uniq -c
87 @a
 189 @e
   3 @p
 264 @s
--- selector keys ---
zsh:1: no matches found: @[a-z]
  61 dx=
  61 dy=
  61 dz=
 186 limit=
 188 name=
  71 tag=
 189 type=
[0m
[0m$ [0mecho '=== verbs ==='; grep -ohE '^[a-z]+| run [a-z]+' generated/*.mcfunction | sed 's/ run //' | sort | uniq -c; echo '=== suspicious ==='; grep -nE 'type=!|c=-|\br=|\brm=|\bm=|\blm=|\bl=|family=|rider|clone|structure|setblock .* [a-z]+$' generated/*.mcfunction | head -30
=== verbs ===
   1 adds
   2 effect
 230 execute
  19 fill
  91 function
   2 gamemode
   1 gamerule
   1 kill
   5 particle
   1 schedule
  89 scoreboard
  85 setblock
   3 spawnpoint
   3 summon
  38 tag
  10 tellraw
   9 title
   2 tp
   1 weather
=== suspicious ===
generated/build.mcfunction:15:execute at @s run setblock ~ ~-1 ~ stone
generated/far_01.mcfunction:9:setblock ~7 ~1 ~61 air
generated/far_01.mcfunction:10:setblock ~7 ~2 ~61 air
generated/far_01.mcfunction:12:setblock ~8 ~1 ~61 air
generated/far_01.mcfunction:13:setblock ~8 ~2 ~61 air
generated/far_01.mcfunction:19:setblock ~7 ~2 ~60 air
generated/far_01.mcfunction:20:setblock ~7 ~3 ~60 air
generated/far_01.mcfunction:22:setblock ~8 ~2 ~60 air
generated/far_01.mcfunction:23:setblock ~8 ~3 ~60 air
generated/far_01.mcfunction:29:setblock ~7 ~3 ~59 air
generated/far_01.mcfunction:30:setblock ~7 ~4 ~59 air
generated/far_01.mcfunction:32:setblock ~8 ~3 ~59 air
generated/far_01.mcfunction:33:setblock ~8 ~4 ~59 air
generated/far_01.mcfunction:39:setblock ~7 ~4 ~58 air
generated/far_01.mcfunction:40:setblock ~7 ~5 ~58 air
generated/far_01.mcfunction:42:setblock ~8 ~4 ~58 air
generated/far_01.mcfunction:43:setblock ~8 ~5 ~58 air
generated/far_01.mcfunction:49:setblock ~7 ~5 ~57 air
generated/far_01.mcfunction:50:setblock ~7 ~6 ~57 air
generated/stage_01.mcfunction:14:setblock ~7 ~1 ~61 air
generated/stage_01.mcfunction:15:setblock ~7 ~2 ~61 air
generated/stage_01.mcfunction:17:setblock ~8 ~1 ~61 air
generated/stage_01.mcfunction:18:setblock ~8 ~2 ~61 air
generated/stage_01.mcfunction:24:setblock ~7 ~2 ~60 air
generated/stage_01.mcfunction:25:setblock ~7 ~3 ~60 air
generated/stage_01.mcfunction:27:setblock ~8 ~2 ~60 air
generated/stage_01.mcfunction:28:setblock ~8 ~3 ~60 air
generated/stage_01.mcfunction:34:setblock ~7 ~3 ~59 air
generated/stage_01.mcfunction:35:setblock ~7 ~4 ~59 air
generated/stage_01.mcfunction:37:setblock ~8 ~3 ~59 air
[0m
[0m$ [0mcat -n generated/tick.json generated/run_start.mcfunction generated/summon_dragon.mcfunction generated/stage_01.mcfunction
1	{
     2	  "values": [
     3	    "basgiath:tick"
     4	  ]
     5	}
     1	scoreboard players set @s run_tick 0
     2	scoreboard players set @s run_sec 0
     3	tag @s add timed_run
     4	title @s actionbar {"text":"§bCourse 0s"}
     1	execute unless entity @e[type=basgiath:dragon] as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run summon basgiath:dragon ~43 ~-1 ~117
     2	execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] run tellraw @a {"text":"A dragon waits on the moss pad. Mount it and fly."}
     3	execute unless entity @e[type=minecraft:armor_stand,name="build_anchor"] run tellraw @s {"text":"Raise the college first. Run /function basgiath/build"}
     1	fill ~ ~-2 ~ ~48 ~-2 ~48 stone
     2	fill ~ ~-2 ~49 ~48 ~-2 ~150 stone
     3	fill ~49 ~-2 ~ ~170 ~-2 ~48 stone
     4	fill ~49 ~-2 ~49 ~170 ~-2 ~150 stone
     5	fill ~ ~-1 ~ ~48 ~-1 ~48 grass_block
     6	fill ~ ~-1 ~49 ~48 ~-1 ~150 grass_block
     7	fill ~49 ~-1 ~ ~170 ~-1 ~48 grass_block
     8	fill ~49 ~-1 ~49 ~170 ~-1 ~150 grass_block
     9	fill ~15 ~-1 ~12 ~48 ~1 ~28 stone_bricks
    10	fill ~49 ~-1 ~12 ~77 ~1 ~28 stone_bricks
    11	fill ~2 ~-1 ~12 ~14 ~32 ~28 stone_bricks
    12	fill ~3 ~ ~13 ~13 ~31 ~27 air
    13	setblock ~7 ~ ~61 sea_lantern
    14	setblock ~7 ~1 ~61 air
    15	setblock ~7 ~2 ~61 air
    16	setblock ~8 ~ ~61 sea_lantern
    17	setblock ~8 ~1 ~61 air
    18	setblock ~8 ~2 ~61 air
    19	setblock ~6 ~ ~61 stone_bricks
    20	setblock ~6 ~1 ~61 sea_lantern
    21	setblock ~9 ~ ~61 stone_bricks
    22	setblock ~9 ~1 ~61 sea_lantern
    23	setblock ~7 ~1 ~60 sea_lantern
    24	setblock ~7 ~2 ~60 air
    25	setblock ~7 ~3 ~60 air
    26	setblock ~8 ~1 ~60 sea_lantern
    27	setblock ~8 ~2 ~60 air
    28	setblock ~8 ~3 ~60 air
    29	setblock ~6 ~1 ~60 stone_bricks
    30	setblock ~6 ~2 ~60 sea_lantern
    31	setblock ~9 ~1 ~60 stone_bricks
    32	setblock ~9 ~2 ~60 sea_lantern
    33	setblock ~7 ~2 ~59 sea_lantern
    34	setblock ~7 ~3 ~59 air
    35	setblock ~7 ~4 ~59 air
    36	setblock ~8 ~2 ~59 sea_lantern
    37	setblock ~8 ~3 ~59 air
    38	setblock ~8 ~4 ~59 air
    39	setblock ~6 ~2 ~59 stone_bricks
    40	setblock ~6 ~3 ~59 sea_lantern
    41	setblock ~9 ~2 ~59 stone_bricks
    42	setblock ~9 ~3 ~59 sea_lantern
    43	setblock ~7 ~3 ~58 sea_lantern
    44	setblock ~7 ~4 ~58 air
    45	setblock ~7 ~5 ~58 air
    46	setblock ~8 ~3 ~58 sea_lantern
    47	setblock ~8 ~4 ~58 air
    48	setblock ~8 ~5 ~58 air
    49	setblock ~6 ~3 ~58 stone_bricks
    50	setblock ~6 ~4 ~58 sea_lantern
[0m
[0m→ [0mRead generated/far_01.mcfunction
[0m→ [0mRead java/com/basgiath/Basgiath.java
[0m→ [0mRead java/com/basgiath/BasgiathContent.java
[0m→ [0mRead java/com/basgiath/BasgiathEvents.java
[0m→ [0mRead java/com/basgiath/DragonEntity.java
[0m→ [0mRead java/com/basgiath/BasgiathSmokeTest.java
[0m→ [0mRead java/com/basgiath/BasgiathCommands.java
[0m→ [0mRead java/com/basgiath/Keepers.java
[0m→ [0mRead java/com/basgiath/Signets.java
[0m
[0m$ [0mls /Users/claudiobarone/Projects/dragon-rider-map/ && ls /Users/claudiobarone/Projects/dragon-rider-map/scripts/ 2>/dev/null | head -30
addon
briefs
BUILD_CHECKLIST.md
DESIGN.md
dist
DISTRIBUTION.md
docs
java
README.md
reports
scripts
tests
__pycache__
bench_bds.sh
bench_gametest.sh
bench_static.py
bench_worlddb.sh
build_dragon_model.py
build_gametest_structure.py
build_gametest_world.py
build_java_assets.py
build_map.py
build_textures.py
build_world.py
check_hud.mjs
check_voxel_consistency.py
editions.py
leveldb_le.py
migrate_schema.py
nbt_le.py
package.sh
run_audit.py
test_editions.py
test_release.py
validate_manifests.py
validate.sh
voxel_consistency.py
zones
[0m
[0m→ [0mRead ci/ci.yml
[0m
[0m$ [0mls -la scripts/zones/ && wc -l scripts/build_map.py scripts/zones/*.py
total 144
-rw-r--r--@  1 claudiobarone  staff    368 Oct  4 19:08 __init__.py
drwxr-xr-x@ 10 claudiobarone  staff    320 Oct  6 18:27 __pycache__
drwxr-xr-x@ 12 claudiobarone  staff    384 Oct  6 10:35 .
drwxr-xr-x@ 29 claudiobarone  staff    928 Oct  6 19:05 ..
-rw-r--r--@  1 claudiobarone  staff  10182 Oct  6 10:35 dorms.py
-rw-------@  1 claudiobarone  staff   7435 Oct  6 09:59 flight.py
-rw-------@  1 claudiobarone  staff  14790 Oct  6 10:04 gauntlet.py
-rw-r--r--@  1 claudiobarone  staff   4416 Oct  4 23:07 parapet.py
-rw-r--r--@  1 claudiobarone  staff   5638 Oct  4 20:16 quad.py
-rw-r--r--@  1 claudiobarone  staff   3197 Oct  6 10:04 README.md
-rw-------@  1 claudiobarone  staff    646 Oct  4 19:14 signet.py
-rw-r--r--@  1 claudiobarone  staff   7274 Oct  6 10:04 valley.py
     722 scripts/build_map.py
       9 scripts/zones/__init__.py
     274 scripts/zones/dorms.py
     210 scripts/zones/flight.py
     368 scripts/zones/gauntlet.py
     121 scripts/zones/parapet.py
     153 scripts/zones/quad.py
      19 scripts/zones/signet.py
     205 scripts/zones/valley.py
    2081 total
[0m
[0m$ [0mls java/src/main/resources/data/basgiath/function/ | head -80; echo '---count---'; ls java/src/main/resources/data/basgiath/function/ | wc -l; echo '--- tags ---'; ls -R java/src/main/resources/data/minecraft/
build.mcfunction
far_01.mcfunction
far_02.mcfunction
far_03.mcfunction
far_04.mcfunction
far_05.mcfunction
far_06.mcfunction
far_07.mcfunction
far_08.mcfunction
far_09.mcfunction
far_10.mcfunction
far_11.mcfunction
far_12.mcfunction
far_13.mcfunction
far_14.mcfunction
far_15.mcfunction
far_16.mcfunction
far_17.mcfunction
far_18.mcfunction
far_19.mcfunction
far_20.mcfunction
far_21.mcfunction
far_22.mcfunction
far_23.mcfunction
far_24.mcfunction
far_25.mcfunction
far_26.mcfunction
fill_far.mcfunction
live.mcfunction
open.mcfunction
raise.mcfunction
run_start.mcfunction
run_stop.mcfunction
stage_01.mcfunction
stage_02.mcfunction
stage_03.mcfunction
stage_04.mcfunction
stage_05.mcfunction
stage_06.mcfunction
stage_07.mcfunction
stage_08.mcfunction
stage_09.mcfunction
stage_10.mcfunction
stage_11.mcfunction
stage_12.mcfunction
stage_13.mcfunction
stage_14.mcfunction
stage_15.mcfunction
stage_16.mcfunction
stage_17.mcfunction
stage_18.mcfunction
stage_19.mcfunction
stage_20.mcfunction
stage_21.mcfunction
stage_22.mcfunction
stage_23.mcfunction
stage_24.mcfunction
stage_25.mcfunction
stage_26.mcfunction
stage_27.mcfunction
stage_28.mcfunction
stage_29.mcfunction
stage_30.mcfunction
stage_31.mcfunction
stage_32.mcfunction
summon_dragon.mcfunction
tick.mcfunction
---count---
      67
--- tags ---
tags

java/src/main/resources/data/minecraft//tags:
function

java/src/main/resources/data/minecraft//tags/function:
tick.json
[0m
[0m$ [0mls addon/behavior_pack/functions/ | head; echo ---; ls addon/behavior_pack/functions/ | wc -l; echo '=== bedrock tick/live heads ==='; ls addon/behavior_pack/functions/
basgiath
README.md
tick.json
---
       3
=== bedrock tick/live heads ===
basgiath
README.md
tick.json
[0m
[0m$ [0mgrep -rhoE '^\s*(execute )?[a-z]+' java/src/main/resources/data/basgiath/function/*.mcfunction | sort | uniq -c | sort -rn; echo '=== all verbs incl run ==='; grep -rhoE ' run [a-z]+' java/src/main/resources/data/basgiath/function/*.mcfunction | sort | uniq -c
2135 setblock
 645 fill
 174 execute as
  74 execute if
  41 execute unless
  39 summon
  24 scoreboard
   8 tellraw
   8 gamerule
   7 execute at
   5 title
   2 tag
   2 schedule
   2 effect
   1 weather
   1 time
   1 spawnpoint
   1 kill
   1 gamemode
=== all verbs incl run ===
   1  run adds
   2  run effect
 117  run function
   1  run gamemode
   5  run particle
  67  run scoreboard
   4  run setblock
   3  run spawnpoint
  42  run summon
  37  run tag
   9  run tellraw
   5  run title
   3  run tp
   1  run weather
[0m
[0m$ [0mpython3 - <<'EOF'
import re, glob, collections
pat = collections.Counter()
files = sorted(glob.glob('java/src/main/resources/data/basgiath/function/*.mcfunction'))
for f in files:
    for line in open(f):
        line=line.rstrip('\n')
        if not line: continue
        s = re.sub(r'"[^"]*"', 'Q', line)
        s = re.sub(r'~?-?\d+(\.\d+)?', '#', s)
        s = re.sub(r'\b[a-z_]+=[^,\]]+', lambda m: m.group(0).split('=')[0]+'=K', s)
        pat[s]+=1
for k,v in pat.most_common(200):
    print(v, '|', k)
EOF
572 | setblock # # # sea_lantern
460 | setblock # # # air
309 | setblock # # # stone_bricks
282 | setblock # # # glass
174 | fill # # # # # # oak_leaves
132 | fill # # # # # # stone_bricks
130 | setblock # ~ # short_grass
58 | fill # # # # # # oak_log
52 | execute as @e[type=K,name=K,limit=K] at @s run function basgiath:far_#
44 | setblock # # # short_grass
42 | setblock # # # red_wool
38 | execute unless entity @e[type=K,name=K] run summon minecraft:armor_stand # # # {CustomName:'{Q:Q}'}
38 | summon minecraft:armor_stand # # # {CustomName:'{Q:Q}'}
36 | fill # # # # # # chain
32 | execute as @e[type=K,name=K,limit=K] at @s run function basgiath:stage_#
32 | setblock # # # lantern
32 | setblock # # # stone_brick_wall
32 | execute if score bg_now map_state matches # as @e[type=K,name=K,limit=K] at @s run function basgiath:stage_#
32 | execute if score bg_now map_state matches # run scoreboard players set bg_stage map_state #
31 | fill # ~ # # # # air
26 | fill # ~ # # # # stone_bricks
24 | setblock # ~ # stone_bricks
24 | fill # # # # # # air
21 | setblock # # # chiseled_stone_bricks
20 | fill # # # # # # cobblestone
18 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K] run scoreboard players add @s gate_pen #
18 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # run tag @a[dx=K,dy=K,dz=K] add rope_touch
16 | setblock # # # lectern[facing=K]
14 | fill # ~ # # # # stone
14 | setblock # # # azure_bluet
14 | setblock # # # dandelion
14 | setblock # # # oxeye_daisy
12 | fill # # # # # # polished_andesite
12 | setblock # # # stone_brick_stairs
12 | setblock # # # poppy
12 | setblock # # # lily_of_the_valley
12 | setblock # # # cornflower
10 | fill # # # # # # smooth_stone
10 | setblock # # # allium
8 | fill # # # # # # stone
8 | setblock # ~ # sea_lantern
8 | fill # ~ # # ~ # stone_bricks
8 | fill # ~ # # # # orange_wool
8 | setblock # ~ # lantern
8 | fill # # # # # # granite
8 | setblock # # # ladder
8 | fill # # # # # # oak_stairs
8 | fill # # # # ~ # stone_bricks
7 | tellraw @a {Q:Q}
6 | fill # # # # # # grass_block
6 | setblock # # # ladder[facing=K]
6 | fill # # # # # # oak_planks
5 | setblock # # # stone_pressure_plate
4 | setblock # ~ # chiseled_stone_bricks
4 | fill # ~ # # # # purple_wool
4 | setblock # # # lectern
4 | fill # ~ # # # # black_wool
4 | setblock # # # cobblestone
4 | fill # # # # # # light_blue_stained_glass
4 | setblock # ~ # allium
4 | setblock # ~ # cornflower
4 | execute as @e[type=K,name=K,limit=K] at @s run particle minecraft:smoke # # # # # # # # normal
3 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K] run spawnpoint @s # # #
3 | execute as @e[type=K,name=K,limit=K] at @s as @a[tag=K,tag=K] run tellraw @s {Q:Q}
2 | execute at @s run setblock # # # sea_lantern
2 | gamerule sendCommandFeedback false
2 | scoreboard players set bg_done map_state #
2 | scoreboard players set bg_pass map_state #
2 | fill ~ # # # # # stone
2 | fill # # ~ # # # stone
2 | fill ~ # # # # # grass_block
2 | fill # # ~ # # # grass_block
2 | fill # # # # # # sea_lantern
2 | fill # ~ # # # # cyan_wool
2 | fill # ~ # # # # light_gray_wool
2 | setblock # # # bell
2 | fill # ~ # # ~ # stone
2 | fill # # # # # # oak_wood
2 | fill # # # # # # dirt_path
2 | fill # ~ # # ~ # smooth_stone
2 | fill # ~ # # # # white_wool
2 | fill # ~ # # # # yellow_wool
2 | fill # ~ # # # # lime_wool
2 | fill # ~ # # # # light_blue_wool
2 | fill # ~ # # # # light_blue_stained_glass
2 | setblock # ~ # oxeye_daisy
2 | setblock # ~ # azure_bluet
2 | setblock # ~ # poppy
2 | fill # # # # # # moss_block
2 | setblock # # # lodestone
2 | setblock # ~ # air
2 | setblock # ~ # stone_pressure_plate
2 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K,tag=K] run tellraw @s {Q:Q}
2 | title @s actionbar {Q:Q}
2 | setblock # # # polished_blackstone
1 | title @s times # # #
1 | title @s title {Q:Q}
1 | title @s subtitle {Q:Q}
1 | scoreboard objectives add map_state dummy
1 | scoreboard objectives add gate_time dummy
1 | scoreboard objectives add gate_sec dummy
1 | scoreboard objectives add gate_start dummy
1 | scoreboard objectives add gate_pen dummy
1 | scoreboard objectives add gate_best dummy
1 | scoreboard objectives add run_tick dummy
1 | scoreboard objectives add run_sec dummy
1 | scoreboard players set bg_twenty map_state #
1 | scoreboard objectives setdisplay sidebar gate_sec
1 | kill @e[type=K,name=K]
1 | execute at @s run setblock ~ # ~ stone
1 | execute at @s run setblock ~ # # sea_lantern
1 | execute at @s run summon minecraft:armor_stand ~ ~ ~ {CustomName:'{Q:Q}'}
1 | execute at @s run effect give @e[type=K,name=K,limit=K] minecraft:invisibility # # true
1 | execute at @s run effect give @e[type=K,name=K,limit=K] minecraft:resistance # # true
1 | gamemode adventure @a
1 | schedule function basgiath:raise #t
1 | scoreboard players set bg_stage map_state #
1 | tellraw @s {Q:Q}
1 | execute unless entity @e[type=K,name=K] run summon minecraft:armor_stand # ~ # {CustomName:'{Q:Q}'}
1 | scoreboard players add bg_wind map_state #
1 | execute if score bg_wind map_state matches #.. run scoreboard players set bg_wind map_state #
1 | execute if score bg_wind map_state matches # as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K] at @s run tp @s ~ ~ #
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K] run tellraw @s {Q:Q}
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # run tag @a[dx=K,dy=K,dz=K] add cp_west
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # run tag @a[dx=K,dy=K,dz=K] add cp_east
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # run tag @a[dx=K,dy=K,dz=K] add cp_quad
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # run tag @a[dx=K,dy=K,dz=K] add cp_valley
1 | scoreboard players add bg_storm map_state #
1 | execute if score bg_storm map_state matches #.. run scoreboard players set bg_storm map_state #
1 | execute if score bg_storm map_state matches # as @e[type=K,name=K,limit=K] run weather thunder #
1 | scoreboard players add @a[tag=K] run_tick #
1 | execute as @a[tag=K] run scoreboard players operation @s run_sec = @s run_tick
1 | scoreboard players operation @a[tag=K] run_sec /= bg_twenty map_state
1 | execute as @a[tag=K] run title @s actionbar [{Q:Q},{Q:{Q:Q,Q:Q}},{Q:Q}]
1 | execute as @e[type=K,name=K,limit=K] at @s run scoreboard players add bg_clock map_state #
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K] run tag @s add gate_run
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K] run tag @s remove gate_done
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K] run scoreboard players operation @s gate_start = bg_clock map_state
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K] run scoreboard players set @s gate_pen #
1 | execute as @e[type=K,name=K,limit=K] at @s as @a[tag=K] run scoreboard players operation @s gate_time = bg_clock map_state
1 | execute as @e[type=K,name=K,limit=K] at @s as @a[tag=K] run scoreboard players operation @s gate_time -= @s gate_start
1 | execute as @e[type=K,name=K,limit=K] at @s as @a[tag=K] run scoreboard players operation @s gate_time += @s gate_pen
1 | execute as @e[type=K,name=K,limit=K] at @s as @a[tag=K] run scoreboard players operation @s gate_sec = @s gate_time
1 | execute as @e[type=K,name=K,limit=K] at @s as @a[tag=K] run scoreboard players operation @s gate_sec /= bg_twenty map_state
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K] run tag @s remove gate_run
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K] run tag @s add gate_done
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K] unless score @s gate_best matches #.. run scoreboard players set @s gate_best #
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K] if score @s gate_best matches # run scoreboard players operation @s gate_best = @s gate_time
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K] if score @s gate_best matches #.. run scoreboard players operation @s gate_best < @s gate_time
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K] run title @s title [{Q:Q},{Q:{Q:Q,Q:Q}},{Q:Q}]
1 | execute as @e[type=K,name=K,limit=K] at @s run tag @a[tag=K] add rope_cool
1 | execute as @e[type=K,name=K,limit=K] at @s run tag @a[tag=K] remove rope_cool
1 | execute as @e[type=K,name=K,limit=K] at @s run tag @a[tag=K] remove rope_told
1 | execute as @e[type=K,name=K,limit=K] at @s as @a[tag=K,tag=K] run title @s actionbar {Q:Q}
1 | execute as @e[type=K,name=K,limit=K] at @s run tag @a[tag=K] add rope_told
1 | execute as @e[type=K,name=K,limit=K] at @s run scoreboard players add bg_spinline map_state #
1 | execute as @e[type=K,name=K,limit=K] at @s if score bg_spinline map_state matches #.. run scoreboard players set bg_spinline map_state #
1 | execute as @e[type=K,name=K,limit=K] at @s if score bg_spinline map_state matches # run particle minecraft:smoke # # # # # # # # normal
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K] run tag @s add crossed
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K,tag=K] run tag @s add bonded
1 | execute as @e[type=K,name=K,limit=K] at @s as @a[tag=K,tag=K] at @s run summon basgiath:dragon # ~ ~
1 | execute as @e[type=K,name=K,limit=K] at @s as @a[tag=K,tag=K] run scoreboard players set bg_bond map_state #
1 | execute as @e[type=K,name=K,limit=K] at @s as @a[tag=K,tag=K] run tag @s add bondcall
1 | execute as @e[type=K,name=K,limit=K] at @s as @a[tag=K,tag=K] run tag @s add relic
1 | execute as @e[type=K,name=K,limit=K] at @s as @a[tag=K,tag=K] run tag @s add trial
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K,tag=K] run tag @s add flew
1 | execute as @e[type=K,name=K,limit=K] at @s positioned # # # as @a[dx=K,dy=K,dz=K,tag=K,tag=K] run tag @s add named
1 | execute if score bg_done map_state matches # run gamemode adventure @a
1 | execute if score bg_done map_state matches # as @e[type=K,name=K,limit=K] at @s run title @p title {Q:Q}
1 | execute if score bg_done map_state matches # as @e[type=K,name=K,limit=K] at @s run title @p subtitle {Q:Q}
1 | execute if score bg_done map_state matches # as @e[type=K,name=K,limit=K] at @s run tellraw @a {Q:Q}
1 | execute if score bg_done map_state matches # as @e[type=K,name=K,limit=K] at @s run tp @p # # # # #
1 | effect give @p minecraft:slow_falling # # true
1 | effect give @p minecraft:resistance # # true
1 | execute as @e[type=K,name=K,limit=K] at @s run tp @p # # #
1 | schedule function basgiath:open #t
1 | scoreboard players set @s run_tick #
1 | scoreboard players set @s run_sec #
1 | tag @s add timed_run
1 | tag @s remove timed_run
1 | scoreboard players reset @s run_tick
1 | scoreboard players reset @s run_sec
1 | fill ~ # ~ # # # stone
1 | fill ~ # ~ # # # grass_block
1 | summon minecraft:armor_stand # ~ # {CustomName:'{Q:Q}'}
1 | time set night
1 | weather thunder #
1 | gamerule doDaylightCycle false
1 | gamerule doWeatherCycle false
1 | gamerule doMobSpawning false
1 | gamerule keepInventory true
1 | gamerule commandBlockOutput false
1 | gamerule doImmediateRespawn true
1 | spawnpoint @p # # #
1 | execute unless entity @e[type=K] as @e[type=K,name=K,limit=K] at @s run summon basgiath:dragon # # #
1 | execute as @e[type=K,name=K,limit=K] run tellraw @a {Q:Q}
1 | execute unless entity @e[type=K,name=K] run tellraw @s {Q:Q}
1 | scoreboard players operation bg_now map_state = bg_stage map_state
1 | execute if score bg_now map_state matches # run function basgiath:live
[0m
[0m$ [0mls addon/behavior_pack/functions/basgiath/ | head -70; echo '=== count ==='; ls addon/behavior_pack/functions/basgiath/ | wc -l; echo '=== open (bedrock) ==='; cat -n addon/behavior_pack/functions/basgiath/open.mcfunction
build.mcfunction
far_01.mcfunction
far_02.mcfunction
far_03.mcfunction
far_04.mcfunction
far_05.mcfunction
far_06.mcfunction
far_07.mcfunction
far_08.mcfunction
far_09.mcfunction
far_10.mcfunction
far_11.mcfunction
far_12.mcfunction
far_13.mcfunction
far_14.mcfunction
far_15.mcfunction
far_16.mcfunction
far_17.mcfunction
far_18.mcfunction
far_19.mcfunction
far_20.mcfunction
far_21.mcfunction
far_22.mcfunction
far_23.mcfunction
far_24.mcfunction
far_25.mcfunction
far_26.mcfunction
fill_far.mcfunction
live.mcfunction
open.mcfunction
raise.mcfunction
run_start.mcfunction
run_stop.mcfunction
stage_01.mcfunction
stage_02.mcfunction
stage_03.mcfunction
stage_04.mcfunction
stage_05.mcfunction
stage_06.mcfunction
stage_07.mcfunction
stage_08.mcfunction
stage_09.mcfunction
stage_10.mcfunction
stage_11.mcfunction
stage_12.mcfunction
stage_13.mcfunction
stage_14.mcfunction
stage_15.mcfunction
stage_16.mcfunction
stage_17.mcfunction
stage_18.mcfunction
stage_19.mcfunction
stage_20.mcfunction
stage_21.mcfunction
stage_22.mcfunction
stage_23.mcfunction
stage_24.mcfunction
stage_25.mcfunction
stage_26.mcfunction
stage_27.mcfunction
stage_28.mcfunction
stage_29.mcfunction
stage_30.mcfunction
stage_31.mcfunction
stage_32.mcfunction
summon_dragon.mcfunction
tick.mcfunction
=== count ===
      67
=== open (bedrock) ===
     1	scoreboard players set bg_pass map_state 2
     2	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_01
     3	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_02
     4	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_03
     5	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_04
     6	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_05
     7	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_06
     8	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_07
     9	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_08
    10	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_09
    11	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_10
    12	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_11
    13	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_12
    14	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_13
    15	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_14
    16	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_15
    17	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_16
    18	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_17
    19	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_18
    20	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_19
    21	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_20
    22	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_21
    23	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_22
    24	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_23
    25	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_24
    26	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_25
    27	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_26
    28	execute if score bg_done map_state matches 0 run gamemode adventure @a
    29	execute if score bg_done map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s run titleraw @p title {"rawtext":[{"text":"Welcome, candidate"}]}
    30	execute if score bg_done map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s run titleraw @p subtitle {"rawtext":[{"text":"Cross the Parapet"}]}
    31	execute if score bg_done map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s run tellraw @a {"rawtext":[{"text":"Fan-made. Not official. Not affiliated with any publisher. The glowing stairs are in front of you. A fall from the span sends you back here. Cross the Parapet. The signet stone waits in the dell, after a dragon chooses you."}]}
    32	execute if score bg_done map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s run tp @p ~8 ~0 ~66 180 0
    33	scoreboard players set bg_done map_state 1
[0m
[0m$ [0mfor f in run_start run_stop summon_dragon build raise fill_far; do echo "=== $f (bedrock) ==="; cat -n addon/behavior_pack/functions/basgiath/$f.mcfunction; done
=== run_start (bedrock) ===
     1	scoreboard players set @s run_tick 0
     2	scoreboard players set @s run_sec 0
     3	tag @s add timed_run
     4	titleraw @s actionbar {"rawtext":[{"text":"§bCourse 0s"}]}
=== run_stop (bedrock) ===
     1	tag @s remove timed_run
     2	scoreboard players reset @s run_tick
     3	scoreboard players reset @s run_sec
     4	titleraw @s actionbar {"rawtext":[{"text":"§7Course clock stopped."}]}
=== summon_dragon (bedrock) ===
     1	execute unless entity @e[type=dragon_rider:dragon] as @e[type=armor_stand,name="build_anchor",c=1] at @s run summon dragon_rider:dragon ~43 ~-1 ~117
     2	execute as @e[type=armor_stand,name="build_anchor",c=1] run tellraw @a {"rawtext":[{"text":"A dragon waits on the moss pad. Mount it and fly."}]}
     3	execute unless entity @e[type=armor_stand,name="build_anchor"] run tellraw @s {"rawtext":[{"text":"Raise the college first. Run /function basgiath/build"}]}
=== build (bedrock) ===
     1	titleraw @s times 0 80 10
     2	titleraw @s title {"rawtext":[{"text":"Building"}]}
     3	titleraw @s subtitle {"rawtext":[{"text":"Stay still"}]}
     4	scoreboard objectives add map_state dummy
     5	scoreboard objectives add gate_time dummy
     6	scoreboard objectives add gate_sec dummy
     7	scoreboard objectives add gate_start dummy
     8	scoreboard objectives add gate_pen dummy
     9	scoreboard objectives add gate_best dummy
    10	scoreboard objectives add run_tick dummy
    11	scoreboard objectives add run_sec dummy
    12	scoreboard players set bg_twenty map_state 20
    13	scoreboard objectives setdisplay sidebar gate_sec
    14	kill @e[type=armor_stand,name="build_anchor"]
    15	execute at @s run setblock ~ ~-1 ~ stone
    16	execute at @s run setblock ~ ~-1 ~-1 sea_lantern
    17	execute at @s run setblock ~1 ~-1 ~-1 sea_lantern
    18	execute at @s run setblock ~-1 ~-1 ~-1 sea_lantern
    19	execute at @s run summon armor_stand "build_anchor" ~ ~ ~
    20	execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] invisibility 999999 1 true
    21	execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] resistance 999999 255 true
    22	gamerule sendcommandfeedback false
    23	gamemode adventure @a
    24	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea remove college_a
    25	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea add circle ~40 ~32 ~40 4 college_a true
    26	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea remove college_b
    27	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea add circle ~120 ~32 ~40 4 college_b true
    28	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea remove college_c
    29	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea add circle ~40 ~32 ~110 4 college_c true
    30	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea remove college_d
    31	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea add circle ~120 ~32 ~110 4 college_d true
    32	scoreboard players set bg_done map_state 0
    33	scoreboard players set bg_pass map_state 1
    34	schedule on_area_loaded add tickingarea college_b basgiath/fill_far
    35	schedule on_area_loaded add tickingarea college_d basgiath/fill_far
    36	schedule delay add basgiath/raise 300
    37	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_01
    38	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_02
    39	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_03
    40	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_04
    41	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_05
    42	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_06
    43	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_07
    44	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_08
    45	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_09
    46	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_10
    47	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_11
    48	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_12
    49	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_13
    50	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_14
    51	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_15
    52	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_16
    53	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_17
    54	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_18
    55	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_19
    56	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_20
    57	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_21
    58	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_22
    59	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_23
    60	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_24
    61	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_25
    62	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_26
    63	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_27
    64	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_28
    65	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_29
    66	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_30
    67	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_31
    68	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_32
    69	scoreboard players set bg_stage map_state 0
    70	tellraw @s {"rawtext":[{"text":"The college is rising. Stay still for 15 seconds. Fan-made. Not official. Not affiliated with any publisher."}]}
=== raise (bedrock) ===
     1	effect @p slow_falling 8 0 true
     2	effect @p resistance 8 5 true
     3	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tp @p ~120 ~8 ~40
     4	schedule delay add basgiath/open 80
=== fill_far (bedrock) ===
     1	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_01
     2	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_02
     3	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_03
     4	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_04
     5	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_05
     6	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_06
     7	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_07
     8	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_08
     9	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_09
    10	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_10
    11	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_11
    12	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_12
    13	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_13
    14	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_14
    15	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_15
    16	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_16
    17	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_17
    18	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_18
    19	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_19
    20	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_20
    21	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_21
    22	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_22
    23	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_23
    24	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_24
    25	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_25
    26	execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_26
[0m
[0m$ [0mgrep -rn "time set\|weather thunder\|doDaylightCycle\|spawnpoint\|effect give\|run_start\|run_stop" java/src/main/resources/data/basgiath/function/*.mcfunction | head -40
java/src/main/resources/data/basgiath/function/build.mcfunction:20:execute at @s run effect give @e[type=minecraft:armor_stand,name="build_anchor",limit=1] minecraft:invisibility 999999 1 true
java/src/main/resources/data/basgiath/function/build.mcfunction:21:execute at @s run effect give @e[type=minecraft:armor_stand,name="build_anchor",limit=1] minecraft:resistance 999999 255 true
java/src/main/resources/data/basgiath/function/live.mcfunction:9:execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~78 ~32 ~14 as @a[dx=12,dy=3,dz=14,tag=!cp_east] run spawnpoint @s ~84 ~33 ~20
java/src/main/resources/data/basgiath/function/live.mcfunction:11:execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~124 ~0 ~44 as @a[dx=10,dy=3,dz=8,tag=!cp_quad] run spawnpoint @s ~128 ~0 ~48
java/src/main/resources/data/basgiath/function/live.mcfunction:13:execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~38 ~-2 ~112 as @a[dx=12,dy=4,dz=12,tag=!cp_valley] run spawnpoint @s ~43 ~-1 ~117
java/src/main/resources/data/basgiath/function/live.mcfunction:17:execute if score bg_storm map_state matches 0 as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] run weather thunder 999999
java/src/main/resources/data/basgiath/function/raise.mcfunction:1:effect give @p minecraft:slow_falling 8 0 true
java/src/main/resources/data/basgiath/function/raise.mcfunction:2:effect give @p minecraft:resistance 8 5 true
java/src/main/resources/data/basgiath/function/stage_32.mcfunction:36:time set night
java/src/main/resources/data/basgiath/function/stage_32.mcfunction:37:weather thunder 999999
java/src/main/resources/data/basgiath/function/stage_32.mcfunction:38:gamerule doDaylightCycle false
java/src/main/resources/data/basgiath/function/stage_32.mcfunction:45:spawnpoint @p ~8 ~0 ~66
[0m
[0m$ [0mgrep -rn "time set\|weather\|gamerule\|spawnpoint\|effect \|schedule\|function basgiath" scripts/build_map.py | head -60
scripts/build_map.py:8:A player then runs /function basgiath/build in a flat world.
scripts/build_map.py:164:    ctx.add("time set night")
scripts/build_map.py:165:    ctx.add("weather thunder 999999")
scripts/build_map.py:166:    ctx.add("gamerule dodaylightcycle false")
scripts/build_map.py:167:    ctx.add("gamerule doweathercycle false")
scripts/build_map.py:168:    ctx.add("gamerule domobspawning false")
scripts/build_map.py:169:    ctx.add("gamerule keepinventory true")
scripts/build_map.py:170:    ctx.add("gamerule sendcommandfeedback false")
scripts/build_map.py:171:    ctx.add("gamerule commandblockoutput false")
scripts/build_map.py:172:    ctx.add("gamerule doimmediaterespawn true")
scripts/build_map.py:174:    ctx.add(f"spawnpoint @p ~{sx} ~{sy} ~{sz}")
scripts/build_map.py:218:            f'execute if score bg_now map_state matches {index} as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/{name}'
scripts/build_map.py:223:    lines.append('execute if score bg_now map_state matches 0 run function basgiath/live')
scripts/build_map.py:289:    return [at_anchor(f"function basgiath/{prefix}_{index:02d}") for index in range(1, count + 1)]
scripts/build_map.py:421:        'execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] invisibility 999999 1 true',
scripts/build_map.py:422:        'execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] resistance 999999 255 true',
scripts/build_map.py:423:        "gamerule sendcommandfeedback false",
scripts/build_map.py:428:        "schedule on_area_loaded add tickingarea college_b basgiath/fill_far",
scripts/build_map.py:429:        "schedule on_area_loaded add tickingarea college_d basgiath/fill_far",
scripts/build_map.py:430:        "schedule delay add basgiath/raise 300",
scripts/build_map.py:460:        "effect @p slow_falling 8 0 true",
scripts/build_map.py:461:        "effect @p resistance 8 5 true",
scripts/build_map.py:463:        "schedule delay add basgiath/open 80",
scripts/build_map.py:475:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~78,y=~32,z=~14,dx=12,dy=3,dz=14,tag=!cp_east] run spawnpoint @s ~84 ~33 ~20
scripts/build_map.py:477:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~124,y=~0,z=~44,dx=10,dy=3,dz=8,tag=!cp_quad] run spawnpoint @s ~128 ~0 ~48
scripts/build_map.py:479:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~38,y=~-2,z=~112,dx=12,dy=4,dz=12,tag=!cp_valley] run spawnpoint @s ~43 ~-1 ~117
scripts/build_map.py:483:execute if score bg_storm map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] run weather thunder 999999
scripts/build_map.py:520:execute unless entity @e[type=armor_stand,name="build_anchor"] run tellraw @s {"rawtext":[{"text":"Raise the college first. Run /function basgiath/build"}]}
scripts/build_map.py:525:`/function basgiath/build` raises the college around an armor stand named `build_anchor`.
scripts/build_map.py:529:`/function basgiath/summon_dragon` summons `dragon_rider:dragon` on the valley pad.
scripts/build_map.py:535:`/function basgiath/run_start` starts a timed run, and `/function basgiath/run_stop` ends it.
[0m
[0m→ [0mRead /Users/claudiobarone/Projects/dragon-rider-map/scripts/build_map.py
[0m
[0m$ [0mgrep -rhoE '(ctx\.add\(|add\()"[^"]*"' scripts/zones/*.py | sed -E 's/.*\(\s*"//' | awk '{print $1}' | sort | uniq -c; echo '=== all raw command-ish strings ==='; grep -rnE '"(execute|tellraw|titleraw|summon|effect|tag |scoreboard|particle|playsound|gamerule|tp |spawnpoint|weather|time|kill|gamemode|schedule|function|setblock|fill|clone|xp|enchant|give|clear|team|team |attribute|item )' scripts/zones/*.py | head -60
=== all raw command-ish strings ===
[0m
[0m$ [0mgrep -rhoE 'ctx\.add\(f?"[^"]+"' scripts/zones/*.py | sed -E 's/ctx\.add\(f?"//' | sed -E 's/"$//' | awk '{print $1}' | sort | uniq -c; echo '=== helpers used in zones ==='; grep -rhoE 'ctx\.[a-z]+\(' scripts/zones/*.py | sort | uniq -c; echo '=== tellraw/titleraw/effect/summon/tag lines ==='; grep -rn 'tellraw\|titleraw\|effect\|summon\|particle\|playsound' scripts/zones/*.py | head -40
=== helpers used in zones ===
   6 ctx.add(
  88 ctx.fill(
  75 ctx.setblock(
   7 ctx.shell(
   7 ctx.take(
=== tellraw/titleraw/effect/summon/tag lines ===
scripts/zones/dorms.py:194:        'summon armor_stand "A rider kneels and the dragon decides." '
scripts/zones/flight.py:16:Nothing in this zone summons a dragon and nothing here offers a choice. The
scripts/zones/flight.py:163:    """Six wool posts. A line for the eye, not a menu and not a summon."""
scripts/zones/flight.py:210:    return f'tellraw @a {{"rawtext":[{{"text":"{text}"}}]}}'
scripts/zones/gauntlet.py:28:# Every live line hangs from the anchor that build_map.py summons.
scripts/zones/gauntlet.py:190:    # The time, inline. The `titleraw` score component used to be withheld
scripts/zones/gauntlet.py:195:        + f"{finish} run titleraw @s title "
scripts/zones/gauntlet.py:217:        + "as @a[tag=rope_touch,tag=!rope_told] run titleraw @s actionbar "
scripts/zones/gauntlet.py:229:        ANCHOR + "run particle minecraft:basic_smoke_particle ~152 ~3 ~83"
scripts/zones/gauntlet.py:233:        + "if score bg_spinline map_state matches 5 run particle minecraft:basic_smoke_particle ~152 ~3 ~82"
scripts/zones/gauntlet.py:368:    ctx.add('summon armor_stand "Gauntlet timekeeper" ~165 ~27 ~110')
scripts/zones/quad.py:14:No summoning stone is placed in this file. That stone moves to the valley.
scripts/zones/quad.py:18:tellraw lines run once from build(). The death roll line names no person.
scripts/zones/quad.py:151:            ctx.add(f'summon armor_stand "{name}" ~{x} ~1 ~{z}')
scripts/zones/quad.py:153:        ctx.add('tellraw @a {"rawtext":[{"text":"' + text + '"}]}')
scripts/zones/valley.py:27:# The clear landing pad. The old summon still aims at 43, -1, 117.
scripts/zones/valley.py:143:    ctx.add(f'summon armor_stand "Roll-keeper" ~{kx} ~{ky} ~{kz}')
scripts/zones/valley.py:148:    return f'tellraw @s {{"rawtext":[{{"text":"{text}"}}]}}'
scripts/zones/valley.py:170:        ANCHOR + fresh + "at @s run summon dragon_rider:dragon ~1 ~ ~",
[0m
[0m→ [0mRead /Users/claudiobarone/Projects/dragon-rider-map/scripts/zones/quad.py
[0m→ [0mRead /Users/claudiobarone/Projects/dragon-rider-map/scripts/zones/valley.py
[0m→ [0mRead /Users/claudiobarone/Projects/dragon-rider-map/scripts/zones/dorms.py
[0m→ [0mRead /Users/claudiobarone/Projects/dragon-rider-map/scripts/zones/parapet.py
[0m→ [0mRead java/com/basgiath/FlightHud.java
[0m→ [0mRead java/com/basgiath/BasgiathData.java
[0m
[0m$ [0mgrep -rn "lodestone" scripts/*.py scripts/zones/*.py java/src/main/resources/data/basgiath/function/*.mcfunction | head -20; echo '=== SIGNET/lectern/armor stand offsets in java ==='; grep -rn "setblock ~50\|setblock ~51\|setblock ~49\|setblock ~52\|setblock ~48" java/src/main/resources/data/basgiath/function/*.mcfunction | head -20
scripts/bench_static.py:317:    if blocks.get(LODESTONE) != "lodestone":
scripts/bench_static.py:318:        fail(f"lodestone at {LODESTONE} is {blocks.get(LODESTONE)!r}")
scripts/build_map.py:671:    if not any("lodestone" in line for line in far):
scripts/build_map.py:672:        raise SystemExit("far retry missed the lodestone")
scripts/editions.py:47:    "light_gray_wool", "lily_of_the_valley", "lime_wool", "lodestone",
scripts/test_release.py:427:        "lodestone",
scripts/test_release.py:585:    lodestone the build places, the form never opens anywhere; if a quiz choice
scripts/test_release.py:605:        if len(parts) >= 5 and parts[0] == "setblock" and parts[4] == "lodestone"
scripts/test_release.py:608:        fail(f"the build places a lodestone at {len(placed)} cells: {sorted(placed)}")
scripts/zones/signet.py:7:once a dragon has chosen the rider. The plaza lodestone stays as it is;
scripts/zones/signet.py:17:    ctx.setblock(50, -1, 130, "lodestone")
scripts/zones/valley.py:31:# The courtyard agent drops a lodestone here. Keep it free of trees.
java/src/main/resources/data/basgiath/function/far_26.mcfunction:22:setblock ~50 ~-1 ~130 lodestone
java/src/main/resources/data/basgiath/function/stage_32.mcfunction:24:setblock ~50 ~-1 ~130 lodestone
=== SIGNET/lectern/armor stand offsets in java ===
java/src/main/resources/data/basgiath/function/far_11.mcfunction:11:setblock ~49 ~32 ~20 stone_bricks
java/src/main/resources/data/basgiath/function/far_11.mcfunction:12:setblock ~50 ~32 ~20 stone_bricks
java/src/main/resources/data/basgiath/function/far_11.mcfunction:13:setblock ~51 ~32 ~20 chiseled_stone_bricks
java/src/main/resources/data/basgiath/function/far_11.mcfunction:14:setblock ~52 ~32 ~20 stone_bricks
java/src/main/resources/data/basgiath/function/far_25.mcfunction:41:setblock ~48 ~-1 ~95 dandelion
java/src/main/resources/data/basgiath/function/far_25.mcfunction:42:setblock ~49 ~-1 ~100 lily_of_the_valley
java/src/main/resources/data/basgiath/function/far_25.mcfunction:43:setblock ~50 ~-1 ~134 poppy
java/src/main/resources/data/basgiath/function/far_25.mcfunction:44:setblock ~51 ~-1 ~139 short_grass
java/src/main/resources/data/basgiath/function/far_26.mcfunction:19:setblock ~50 ~-2 ~124 stone_bricks
java/src/main/resources/data/basgiath/function/far_26.mcfunction:21:setblock ~50 ~-1 ~123 lectern
java/src/main/resources/data/basgiath/function/far_26.mcfunction:22:setblock ~50 ~-1 ~130 lodestone
java/src/main/resources/data/basgiath/function/far_26.mcfunction:23:setblock ~50 ~ ~130 air
java/src/main/resources/data/basgiath/function/stage_17.mcfunction:5:setblock ~48 ~32 ~20 stone_bricks
java/src/main/resources/data/basgiath/function/stage_17.mcfunction:6:setblock ~49 ~32 ~20 stone_bricks
java/src/main/resources/data/basgiath/function/stage_17.mcfunction:7:setblock ~50 ~32 ~20 stone_bricks
java/src/main/resources/data/basgiath/function/stage_17.mcfunction:8:setblock ~51 ~32 ~20 chiseled_stone_bricks
java/src/main/resources/data/basgiath/function/stage_17.mcfunction:9:setblock ~52 ~32 ~20 stone_bricks
java/src/main/resources/data/basgiath/function/stage_31.mcfunction:43:setblock ~48 ~-1 ~95 dandelion
java/src/main/resources/data/basgiath/function/stage_31.mcfunction:44:setblock ~49 ~-1 ~100 lily_of_the_valley
java/src/main/resources/data/basgiath/function/stage_31.mcfunction:45:setblock ~50 ~-1 ~134 poppy
[0m
[0m$ [0mgrep -rn "lodestone\|LODESTONE" scripts/zones/*.py scripts/*.py | head -20; echo '=== java code refs ==='; grep -rn "SIGNET_STONE\|lodestone\|LODESTONE" java/com/basgiath/*.java
scripts/zones/signet.py:7:once a dragon has chosen the rider. The plaza lodestone stays as it is;
scripts/zones/signet.py:17:    ctx.setblock(50, -1, 130, "lodestone")
scripts/zones/valley.py:31:# The courtyard agent drops a lodestone here. Keep it free of trees.
scripts/zones/valley.py:32:LODESTONE_X0, LODESTONE_X1 = 48, 52
scripts/zones/valley.py:33:LODESTONE_Z0, LODESTONE_Z1 = 128, 132
scripts/zones/valley.py:115:    if LODESTONE_X0 <= x <= LODESTONE_X1 and LODESTONE_Z0 <= z <= LODESTONE_Z1:
scripts/bench_static.py:38:LODESTONE = (50, -1, 130)
scripts/bench_static.py:317:    if blocks.get(LODESTONE) != "lodestone":
scripts/bench_static.py:318:        fail(f"lodestone at {LODESTONE} is {blocks.get(LODESTONE)!r}")
scripts/build_map.py:671:    if not any("lodestone" in line for line in far):
scripts/build_map.py:672:        raise SystemExit("far retry missed the lodestone")
scripts/editions.py:47:    "light_gray_wool", "lily_of_the_valley", "lime_wool", "lodestone",
scripts/test_release.py:427:        "lodestone",
scripts/test_release.py:585:    lodestone the build places, the form never opens anywhere; if a quiz choice
scripts/test_release.py:605:        if len(parts) >= 5 and parts[0] == "setblock" and parts[4] == "lodestone"
scripts/test_release.py:608:        fail(f"the build places a lodestone at {len(placed)} cells: {sorted(placed)}")
=== java code refs ===
zsh:1: no matches found: java/com/basgiath/*.java
[0m
[0m$ [0mls java/src/main/java/com/basgiath/ 2>/dev/null; echo '=== diff pack vs repo ==='; for f in reports/audit/pack-free-basgiath-java/java/com/basgiath/*.java; do b=$(basename $f); if [ -f java/src/main/java/com/basgiath/$b ]; then diff -q "$f" "java/src/main/java/com/basgiath/$b" || true; else echo "MISSING in repo: $b"; fi; done; echo '=== repo-only files ==='; for f in java/src/main/java/com/basgiath/*.java; do b=$(basename $f); [ -f "reports/audit/pack-free-basgiath-java/java/com/basgiath/$b" ] || echo "repo only: $b"; done; echo '=== diff editions.py ==='; diff -q scripts/editions.py reports/audit/pack-free-basgiath-java/scripts/editions.py; diff -q scripts/test_editions.py reports/audit/pack-free-basgiath-java/scripts/test_editions.py; diff -q ci/ci.yml reports/audit/pack-free-basgiath-java/ci/ci.yml
Basgiath.java
BasgiathClient.java
BasgiathCommands.java
BasgiathContent.java
BasgiathData.java
BasgiathEvents.java
BasgiathForms.java
BasgiathNetwork.java
BasgiathSmokeTest.java
Codices.java
DragonEntity.java
DragonModel.java
FlightHud.java
Keepers.java
Signets.java
Vault.java
=== diff pack vs repo ===
=== repo-only files ===
=== diff editions.py ===
diff: ci/ci.yml: No such file or directory
[0m
[0m→ [0mRead java/com/basgiath/BasgiathNetwork.java
[0m→ [0mRead java/com/basgiath/BasgiathClient.java
[0m→ [0mRead java/com/basgiath/Codices.java
[0m→ [0mRead /Users/claudiobarone/Projects/dragon-rider-map/scripts/zones/gauntlet.py
[0m
[0m$ [0mpython3 - <<'EOF'
import re, glob
bad=[]
for f in sorted(glob.glob('java/src/main/resources/data/basgiath/function/*.mcfunction')):
    for n,line in enumerate(open(f),1):
        line=line.rstrip('\n')
        if 'positioned' not in line: continue
        # split run
        head, sep, run = line.rpartition(' run ')
        if not sep: continue
        # does the run part carry relative coordinates?
        if re.search(r'(?<![\w:"])~-?\d|(?<![\w:"])~(?=\s|$)', run):
            # is the position reset between the last positioned and run?
            tail = head.rsplit('positioned',1)[-1]
            resets = ' at ' in (' '+tail) or 'positioned' in tail.split(' as ')[0]
            # crude: check if an 'at' appears after the LAST positioned
            last_pos = head.rfind('positioned')
            after = head[last_pos:]
            has_at = re.search(r'\bat\s+@\w', after) is not None
            bad.append((f,n,has_at,line))
for f,n,has_at,line in bad:
    print(('OK-reset ' if has_at else 'BROKEN  '), f.split('/')[-1], n, '|', line)
print(len(bad),'lines with positioned + relative run coords')
EOF
OK-reset  live.mcfunction 3 | execute if score bg_wind map_state matches 0 as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~15 ~33 ~19 as @a[dx=63,dy=2,dz=2] at @s run tp @s ~ ~ ~0.18
BROKEN   live.mcfunction 9 | execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~78 ~32 ~14 as @a[dx=12,dy=3,dz=14,tag=!cp_east] run spawnpoint @s ~84 ~33 ~20
BROKEN   live.mcfunction 11 | execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~124 ~0 ~44 as @a[dx=10,dy=3,dz=8,tag=!cp_quad] run spawnpoint @s ~128 ~0 ~48
BROKEN   live.mcfunction 13 | execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~38 ~-2 ~112 as @a[dx=12,dy=4,dz=12,tag=!cp_valley] run spawnpoint @s ~43 ~-1 ~117
4 lines with positioned + relative run coords
[0m
## Objective
- Perform a readonly `code-debug` audit per `reports/audit/pack-free-basgiath-java/audit_prompt.md`: find where the Bedrock→Java port of the Basgiath map will "silently do nothing" (unknown block/entity/selector → line never runs or function fails to load at startup), find "the third one" beyond `grass_path`→`dirt_path` and `@a[x=~4]` selector coords.
- Output a findings table (Severity | Finding | Evidence file:line | Fix), plus Root cause, Confidence, and Unique angle sections.

## Important Details
- Mode constraints: readonly, markdown report only; no edits; no secrets; no client-modification/anticheat suggestions (free fan-made release). Every finding needs file + line.
- Do not re-report: relative selector coords hoist (unless shown wrong somewhere specific), `grass_path`→`dirt_path` mapping, dropped `tickingarea`/`schedule on_area_loaded`, Bedrock byte-identity test.
- Target: Minecraft 1.21.1, NeoForge 21.1.256, official mappings; Bedrock 26.x / `@minecraft/server` 2.x; Java 1.21.1 has no dialogs (custom screens).
- `scripts/editions.py::to_java()` must be strict — any non-strict path is a finding.
- Pack `generated/` is a **subset** (8 of 67 functions); full tree lives at repo root `/Users/claudiobarone/Projects/dragon-rider-map` (identical `editions.py`, `test_editions.py`, and `java/src/main/java/com/basgiath/*.java` vs pack copies; pack `ci/ci.yml` not present at that repo path).
- Verified clean so far: all block ids in `SAME_BLOCK`/`BLOCK_RENAME` exist in Java 1.21.1; selector keys used across full output are only `dx,dy,dz,limit,name,tag,type` (all valid Java); entity types `minecraft:armor_stand`, `basgiath:dragon` OK; effect/particle/gamerule/function ids OK; lodestone at `(50,-1,130)` matches `BasgiathEvents.SIGNET_STONE`; keepers' lectern offsets `(128,1,34)` and `(50,-1,123)` match zones; all 67 functions + `raise`, `fill_far`, `run_stop` exist in real tree.

## Work State
### Completed
- Listed pack and read: `audit_prompt.md`, `scripts/editions.py`, `scripts/test_editions.py`, `scripts/build_java_assets.py`, all pack `generated/*.mcfunction` + `tick.json`, `ci/ci.yml`, and Java files `Basgiath.java`, `BasgiathContent.java`, `BasgiathEvents.java`, `DragonEntity.java`, `BasgiathSmokeTest.java`, `BasgiathCommands.java`, `Keepers.java`, `Signets.java`, `FlightHud.java`, `BasgiathData.java`, `BasgiathNetwork.java`, `BasgiathClient.java`, `Codices.java`.
- Enumerated selector keys, verbs, and normalized command shapes from the full 67-function Java tree (`java/src/main/resources/data/basgiath/function/`).
- Read generator source at repo root: `scripts/build_map.py` (722 lines), `scripts/zones/{quad,valley,dorms,parapet}.py` (full/partial), grepped `scripts/zones/*.py` command emission and `scripts/zones/{gauntlet,flight,signet}.py` for `tellraw/titleraw/effect/summon/particle`.
- Diffed pack vs repo: identical; repo-only source files confirmed present.

### Active
- Narrowing candidate findings for the report; open candidate list:
  1. `_effect` boolean semantics: Bedrock `particles` (show) vs Java `hideParticles` (hide) — emitted lines like `effect give @p minecraft:slow_falling 8 0 true` (`generated`/`raise.mcfunction:1-2`, `build.mcfunction:20-21`); needs wiki verification.
  2. `to_java` strictness holes: `_split` truncates `setblock` args beyond index 3 (`editions.py` ~line 362) and `fill` beyond index 7 (~line 366) instead of raising; `_java_selectors` does not rewrite Bedrock `r=/rm=/l=/lm=/m=` or `type=!...` (latent, no current evidence); `_hoist_in_chain` only handles `as|at` prefixes, not `if/unless entity @x[x=~...]`.
  3. `_summon` builds `CustomName:'{"text":...}'` — unescaped apostrophe in a name would break SNBT at function load (latent; no current names contain `'`).
  4. Cosmetic/state seam: `STATE_MAP` `direction` (lectern) and `facing_direction` (ladder) value tables in `editions.py` — verify Bedrock `direction` 0..3 compass mapping and ladder attach direction.
  5. Anchor armor stand summoned without `NoGravity` in `generated/build.mcfunction:19` (smoke test adds `NoGravity:1b` explicitly) — gravity/coordinate-space concern.
  6. Possible wrong-facing/appearance defaults: armor stand `CustomName` visibility on Java vs Bedrock for text-plaque armor stands (`quad.py:151`, `dorms.py:194`).
- Remaining unread pack files: `java/com/basgiath/BasgiathForms.java`, `Vault.java`, `DragonModel.java` (and pack `java/build.gradle`, `settings.gradle`, `gradle.properties`).
- Remaining unread repo source: `scripts/zones/gauntlet.py`, `flight.py`, `signet.py`, `signet.py` (full), `scripts/test_release.py` (Java-related checks), `scripts/bench_static.py`.

### Blocked
- Web/wiki verification not yet done for: Java 1.21.1 `/effect give` `hideParticles` default/meaning vs Bedrock `/effect` `particles` flag; Bedrock `/summon` argument order (nameTag vs pos); Bedrock lectern `direction` value table; ladder `facing_direction` semantics.
- Cannot run `scripts/build_map.py` (would rewrite files — violates readonly); in-memory translation only via `PYTHONDONTWRITEBYTECODE=1` python if needed.

## Next Move
1. Read remaining pack files: `java/com/basgiath/BasgiathForms.java`, `Vault.java`, `DragonModel.java`, `java/build.gradle`, `settings.gradle`, `gradle.properties`.
2. Read `scripts/zones/gauntlet.py`, `flight.py`, `signet.py` and the remainder of `scripts/editions.py` (lines 40-581 were truncated) to confirm exact line numbers for `_split`/`_java_selectors`/`_summon`/`STATE_MAP` findings; then do targeted web checks for the effect/summon/state semantics and write the findings table + Root cause / Confidence / Unique angle sections.

## Relevant Files
- `reports/audit/pack-free-basgiath-java/audit_prompt.md`: the audit brief, severity/table format, do-not-repeat list.
- `reports/audit/pack-free-basgiath-java/scripts/editions.py`: whole Bedrock→Java translation (`to_java`, `_java_selectors`, `_split_relative_box`, `_summon`, `_effect`, `_particle`, `STATE_MAP`, `ENTITY_MAP`, `SAME_BLOCK`, `write_java_functions`) — primary finding surface; read was truncated at line ~40.
- `reports/audit/pack-free-basgiath-java/scripts/test_editions.py`: existing guards (loud-stop tests, Bedrock byte-identity).
- `reports/audit/pack-free-basgiath-java/generated/*.mcfunction`: emitted Java datapack sample (8 of 67 functions).
- `/Users/claudiobarone/Projects/dragon-rider-map/java/src/main/resources/data/basgiath/function/`: full 67-function Java output (authoritative for evidence).
- `/Users/claudiobarone/Projects/dragon-rider-map/addon/behavior_pack/functions/basgiath/`: Bedrock source dialect output for comparison.
- `/Users/claudiobarone/Projects/dragon-rider-map/scripts/build_map.py`: command emitter (geometry, `finish()`, `write_java`, `retry_line`, `is_far`).
- `/Users/claudiobarone/Projects/dragon-rider-map/scripts/zones/*.py`: zone command sources (`dorms.py` lectern/ladder states, `quad.py`, `valley.py`, `gauntlet.py`, `flight.py`, `signet.py`, `parapet.py`).
- `reports/audit/pack-free-basgiath-java/java/com/basgiath/*.java`: NeoForge mod half (coordinates shared with datapack: `BasgiathEvents.SIGNET_STONE`, `Keepers` offsets).
- `reports/audit/pack-free-basgiath-java/ci/ci.yml`: CI jobs (Java + Bedrock chains).
- `/Users/claudiobarone/Projects/dragon-rider-map/scripts/test_release.py`, `scripts/bench_static.py`: existing tests that already cover lodestone/form wiring.
Continue if you have next steps, or stop and ask for clarification if you are unsure how to proceed.
[0m$ [0mgrep -n "build_anchor\|summon armor_stand\|positioned\|spawnpoint" scripts/build_map.py | head -40; echo ---; grep -rn "build_anchor" scripts/*.py | head
174:    ctx.add(f"spawnpoint @p ~{sx} ~{sy} ~{sz}")
218:            f'execute if score bg_now map_state matches {index} as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/{name}'
284:        'execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run ' + command
415:        'kill @e[type=armor_stand,name="build_anchor"]',
420:        'execute at @s run summon armor_stand "build_anchor" ~ ~ ~',
421:        'execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] invisibility 999999 1 true',
422:        'execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] resistance 999999 255 true',
441:    once = "execute if score bg_done map_state matches 0 as @e[type=armor_stand,name=\"build_anchor\",c=1] at @s run "
469:execute if score bg_wind map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s positioned ~15 ~33 ~19 as @a[dx=63,dy=2,dz=2] at @s run tp @s ~ ~ ~0.18
470:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~20 ~34 ~20
471:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~40 ~34 ~20
472:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~55 ~34 ~20
473:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~4,y=~32,z=~14,dx=10,dy=3,dz=14,tag=!cp_west] run tellraw @s {"rawtext":[{"text":"The span is one block wide. A fall sends you back to the ground."}]}
474:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~4,y=~32,z=~14,dx=10,dy=3,dz=14] add cp_west
475:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~78,y=~32,z=~14,dx=12,dy=3,dz=14,tag=!cp_east] run spawnpoint @s ~84 ~33 ~20
476:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~78,y=~32,z=~14,dx=12,dy=3,dz=14] add cp_east
477:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~124,y=~0,z=~44,dx=10,dy=3,dz=8,tag=!cp_quad] run spawnpoint @s ~128 ~0 ~48
478:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~124,y=~0,z=~44,dx=10,dy=3,dz=8] add cp_quad
479:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~38,y=~-2,z=~112,dx=12,dy=4,dz=12,tag=!cp_valley] run spawnpoint @s ~43 ~-1 ~117
480:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~38,y=~-2,z=~112,dx=12,dy=4,dz=12] add cp_valley
483:execute if score bg_storm map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] run weather thunder 999999
518:SUMMON = """execute unless entity @e[type=dragon_rider:dragon] as @e[type=armor_stand,name="build_anchor",c=1] at @s run summon dragon_rider:dragon ~43 ~-1 ~117
519:execute as @e[type=armor_stand,name="build_anchor",c=1] run tellraw @a {"rawtext":[{"text":"A dragon waits on the moss pad. Mount it and fly."}]}
520:execute unless entity @e[type=armor_stand,name="build_anchor"] run tellraw @s {"rawtext":[{"text":"Raise the college first. Run /function basgiath/build"}]}
525:`/function basgiath/build` raises the college around an armor stand named `build_anchor`.
---
scripts/bench_static.py:548:        'execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run '
scripts/bench_static.py:580:  entity: { nameTag: "build_anchor", location: ANCHOR },
scripts/bench_static.py:743:  anchor.entity = { nameTag: "build_anchor", location: MOVED };
scripts/bench_static.py:755:  anchor.entity = { nameTag: "build_anchor", location: ANCHOR };
scripts/build_map.py:218:            f'execute if score bg_now map_state matches {index} as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/{name}'
scripts/build_map.py:284:        'execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run ' + command
scripts/build_map.py:415:        'kill @e[type=armor_stand,name="build_anchor"]',
scripts/build_map.py:420:        'execute at @s run summon armor_stand "build_anchor" ~ ~ ~',
scripts/build_map.py:421:        'execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] invisibility 999999 1 true',
scripts/build_map.py:422:        'execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] resistance 999999 255 true',
[0m
[0m$ [0mgrep -n "def _hoist_in_chain\|def _split\|def _java_selectors\|def _summon\|def _effect\|def _particle\|STATE_MAP\|def to_java\|def _inner\|def _extract_from_command\|_join" scripts/editions.py | head -40; echo "=== total lines ==="; wc -l scripts/editions.py
94:STATE_MAP: dict[str, tuple[str, dict[str, str] | None]] = {
134:def _join(tokens: list[str]) -> str:
138:def _split_relative_box(token: str) -> tuple[str | None, str]:
187:def _hoist_in_chain(prefix: str) -> str:
206:def _extract_from_command(command: str) -> tuple[str, str | None]:
225:def _java_selectors(text: str) -> str:
269:        if key not in STATE_MAP:
272:                "Add it to STATE_MAP in scripts/editions.py."
274:        java_key, value_map = STATE_MAP[key]
279:                    "Add it to STATE_MAP in scripts/editions.py."
331:def _inner(line: str) -> tuple[str, str]:
343:            return _join(tokens[1:index]), _join(tokens[index + 1 :])
347:def to_java(line: str) -> str | None:
362:            out = _join([verb, *args[:3], _java_block(args[3])])
366:            out = _join([verb, *args[:6], _java_block(args[6])])
379:        out = _join([verb, args[0], _java_text(_join(args[1:]))])
393:        out = _join([verb, key, args[1]])
396:        out = _join([verb, _java_function(args[0])])
433:def _summon(line: str, args: list[str]) -> str:
455:    return _join(["summon", *parts])
466:        return _join(["title", target, "times", *args[2:]])
469:    return _join(["title", target, mode, _java_text(_join(args[2:]))])
472:def _particle(line: str, args: list[str]) -> str:
482:    return _join(["particle", name, *args[1:4], "0", "0", "0", "0", "1", "normal"])
485:def _effect(line: str, args: list[str]) -> str:
495:    return _join(["effect", "give", args[0], name, *args[2:]])
506:        return _join(["schedule", "function", _java_function(args[2]), f"{args[3]}t"])
=== total lines ===
     581 scripts/editions.py
[0m
[0m→ [0mRead audit_prompt.md
[0m
[0m$ [0msed -n 440,530p scripts/build_map.py
sx, sy, sz = START
    once = "execute if score bg_done map_state matches 0 as @e[type=armor_stand,name=\"build_anchor\",c=1] at @s run "
    return [
        'execute if score bg_done map_state matches 0 run gamemode adventure @a',
        once + 'titleraw @p title {"rawtext":[{"text":"Welcome, candidate"}]}',
        once + 'titleraw @p subtitle {"rawtext":[{"text":"Cross the Parapet"}]}',
        once
        + 'tellraw @a {"rawtext":[{"text":"Fan-made. Not official. Not affiliated with any publisher. The glowing stairs are in front of you. A fall from the span sends you back here. Cross the Parapet. The signet stone waits in the dell, after a dragon chooses you."}]}',
        once + f"tp @p ~{sx} ~{sy} ~{sz} 180 0",
        "scoreboard players set bg_done map_state 1",
    ]


def raise_text() -> str:
    """Move the player onto the plaza so the phone loads those chunks.

    The move is 8 blocks up. Slow falling keeps a miss from killing them.
    The blocks are placed 4 seconds later, then the player returns to the start.
    """
    lines = [
        "effect @p slow_falling 8 0 true",
        "effect @p resistance 8 5 true",
        at_anchor("tp @p ~120 ~8 ~40"),
        "schedule delay add basgiath/open 80",
    ]
    return "\n".join(lines) + "\n"

LIVE = """scoreboard players add bg_wind map_state 1
execute if score bg_wind map_state matches 4.. run scoreboard players set bg_wind map_state 0
execute if score bg_wind map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s positioned ~15 ~33 ~19 as @a[dx=63,dy=2,dz=2] at @s run tp @s ~ ~ ~0.18
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~20 ~34 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~40 ~34 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~55 ~34 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~4,y=~32,z=~14,dx=10,dy=3,dz=14,tag=!cp_west] run tellraw @s {"rawtext":[{"text":"The span is one block wide. A fall sends you back to the ground."}]}
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~4,y=~32,z=~14,dx=10,dy=3,dz=14] add cp_west
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~78,y=~32,z=~14,dx=12,dy=3,dz=14,tag=!cp_east] run spawnpoint @s ~84 ~33 ~20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~78,y=~32,z=~14,dx=12,dy=3,dz=14] add cp_east
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~124,y=~0,z=~44,dx=10,dy=3,dz=8,tag=!cp_quad] run spawnpoint @s ~128 ~0 ~48
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~124,y=~0,z=~44,dx=10,dy=3,dz=8] add cp_quad
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~38,y=~-2,z=~112,dx=12,dy=4,dz=12,tag=!cp_valley] run spawnpoint @s ~43 ~-1 ~117
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~38,y=~-2,z=~112,dx=12,dy=4,dz=12] add cp_valley
scoreboard players add bg_storm map_state 1
execute if score bg_storm map_state matches 200.. run scoreboard players set bg_storm map_state 0
execute if score bg_storm map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] run weather thunder 999999
scoreboard players add @a[tag=timed_run] run_tick 1
execute as @a[tag=timed_run] run scoreboard players operation @s run_sec = @s run_tick
scoreboard players operation @a[tag=timed_run] run_sec /= bg_twenty map_state
execute as @a[tag=timed_run] run titleraw @s actionbar {"rawtext":[{"text":"§bCourse  "},{"score":{"name":"@s","objective":"run_sec"}},{"text":"s"}]}
"""

# A cadet course clock: an on-screen timer for a timed run. No experimental
# flag is involved; the clock is a scoreboard and a titleraw line, so it works
# on a phone. The flight readout stands down while a cadet has the tag, because
# both draw to the action bar and only one can own it.
RUN_START = """scoreboard players set @s run_tick 0
scoreboard players set @s run_sec 0
tag @s add timed_run
titleraw @s actionbar {"rawtext":[{"text":"§bCourse 0s"}]}
"""

RUN_STOP = """tag @s remove timed_run
scoreboard players reset @s run_tick
scoreboard players reset @s run_sec
titleraw @s actionbar {"rawtext":[{"text":"§7Course clock stopped."}]}
"""


def live_text() -> str:
    """The tick body: the existing wind, checkpoints, and storm first.

    Then the Gauntlet ropes and the Threshing event. ``zones.flight`` has no
    live lines. Every line below already carries its own execute-at-anchor.
    """
    lines = [LIVE.rstrip("\n")]
    lines.extend(build_gauntlet_live())
    lines.extend(build_valley_live())
    return "\n".join(lines) + "\n"

SUMMON = """execute unless entity @e[type=dragon_rider:dragon] as @e[type=armor_stand,name="build_anchor",c=1] at @s run summon dragon_rider:dragon ~43 ~-1 ~117
execute as @e[type=armor_stand,name="build_anchor",c=1] run tellraw @a {"rawtext":[{"text":"A dragon waits on the moss pad. Mount it and fly."}]}
execute unless entity @e[type=armor_stand,name="build_anchor"] run tellraw @s {"rawtext":[{"text":"Raise the college first. Run /function basgiath/build"}]}
"""

README = """# Functions

`/function basgiath/build` raises the college around an armor stand named `build_anchor`.

The stand is the origin. Every later command is relative to it. The build stays at your feet. The screen says "Building" at once. It places one stone under the stand, then gives that stand invisibility and resistance. The stone keeps the stand from falling. The same command places every stage. About 15 seconds later the game moves you onto the plaza for a few seconds, places the stairs, then returns you to the start. Close chat. Do not walk until the screen says "Welcome, candidate".

`/function basgiath/summon_dragon` summons `dragon_rider:dragon` on the valley pad.
[0m
[0m$ [0mpython3 - <<'EOF'
import re, glob
tot=0
for f in sorted(glob.glob('java/src/main/resources/data/basgiath/function/*.mcfunction')):
    for n,line in enumerate(open(f),1):
        line=line.rstrip('\n')
        head,sep,run = line.rpartition(' run ')
        if not sep: 
            run = line if ' ~' in line or line.endswith('~') else ''
        if re.search(r'(?<![\w:"\'\]])~-?\d', run) or re.search(r'(?<![\w:"\'\]])~(?=\s|$)', run):
            tot+=1
            print(f.split('/')[-1], n, '|', run.strip()[:110])
print('total run-parts with ~:', tot)
EOF
...output truncated...

Full output saved to: /Users/claudiobarone/.local/share/opencode/tool-output/tool_1138b1ec00010AUnAmqcagvLUs

stage_16.mcfunction 11 | setblock ~122 ~2 ~19 sea_lantern
stage_16.mcfunction 12 | setblock ~122 ~1 ~22 stone_bricks
stage_16.mcfunction 13 | setblock ~122 ~2 ~22 sea_lantern
stage_16.mcfunction 14 | setblock ~123 ~ ~20 sea_lantern
stage_16.mcfunction 15 | setblock ~123 ~1 ~20 air
stage_16.mcfunction 16 | setblock ~123 ~2 ~20 air
stage_16.mcfunction 17 | setblock ~123 ~ ~21 sea_lantern
stage_16.mcfunction 18 | setblock ~123 ~1 ~21 air
stage_16.mcfunction 19 | setblock ~123 ~2 ~21 air
stage_16.mcfunction 20 | setblock ~123 ~ ~19 stone_bricks
stage_16.mcfunction 21 | setblock ~123 ~1 ~19 sea_lantern
stage_16.mcfunction 22 | setblock ~123 ~ ~22 stone_bricks
stage_16.mcfunction 23 | setblock ~123 ~1 ~22 sea_lantern
stage_16.mcfunction 24 | setblock ~15 ~32 ~20 sea_lantern
stage_16.mcfunction 25 | setblock ~16 ~32 ~20 sea_lantern
stage_16.mcfunction 26 | setblock ~17 ~32 ~20 sea_lantern
stage_16.mcfunction 27 | setblock ~18 ~32 ~20 sea_lantern
stage_16.mcfunction 28 | setblock ~19 ~32 ~20 chiseled_stone_bricks
stage_16.mcfunction 29 | setblock ~20 ~32 ~20 stone_bricks
stage_16.mcfunction 30 | setblock ~21 ~32 ~20 stone_bricks
stage_16.mcfunction 31 | setblock ~22 ~32 ~20 stone_bricks
stage_16.mcfunction 32 | setblock ~23 ~32 ~20 chiseled_stone_bricks
stage_16.mcfunction 33 | setblock ~24 ~32 ~20 stone_bricks
stage_16.mcfunction 34 | setblock ~25 ~32 ~20 stone_bricks
stage_16.mcfunction 35 | setblock ~26 ~32 ~20 stone_bricks
stage_16.mcfunction 36 | setblock ~27 ~32 ~20 chiseled_stone_bricks
stage_16.mcfunction 37 | setblock ~28 ~32 ~20 stone_bricks
stage_16.mcfunction 38 | setblock ~29 ~32 ~20 stone_bricks
stage_16.mcfunction 39 | setblock ~30 ~32 ~20 stone_bricks
stage_16.mcfunction 40 | setblock ~31 ~32 ~20 chiseled_stone_bricks
stage_16.mcfunction 41 | setblock ~32 ~32 ~20 stone_bricks
stage_16.mcfunction 42 | setblock ~33 ~32 ~20 stone_bricks
stage_16.mcfunction 43 | setblock ~34 ~32 ~20 stone_bricks
stage_16.mcfunction 44 | setblock ~35 ~32 ~20 chiseled_stone_bricks
stage_16.mcfunction 45 | setblock ~36 ~32 ~20 stone_bricks
stage_16.mcfunction 46 | setblock ~37 ~32 ~20 stone_bricks
stage_16.mcfunction 47 | setblock ~38 ~32 ~20 stone_bricks
stage_16.mcfunction 48 | setblock ~39 ~32 ~20 chiseled_stone_bricks
stage_16.mcfunction 49 | setblock ~40 ~32 ~20 stone_bricks
stage_16.mcfunction 50 | setblock ~41 ~32 ~20 stone_bricks
stage_17.mcfunction 1 | setblock ~42 ~32 ~20 stone_bricks
stage_17.mcfunction 2 | setblock ~43 ~32 ~20 chiseled_stone_bricks
stage_17.mcfunction 3 | setblock ~44 ~32 ~20 polished_blackstone
stage_17.mcfunction 4 | setblock ~47 ~32 ~20 polished_blackstone
stage_17.mcfunction 5 | setblock ~48 ~32 ~20 stone_bricks
stage_17.mcfunction 6 | setblock ~49 ~32 ~20 stone_bricks
stage_17.mcfunction 7 | setblock ~50 ~32 ~20 stone_bricks
stage_17.mcfunction 8 | setblock ~51 ~32 ~20 chiseled_stone_bricks
stage_17.mcfunction 9 | setblock ~52 ~32 ~20 stone_bricks
stage_17.mcfunction 10 | setblock ~53 ~32 ~20 stone_bricks
stage_17.mcfunction 11 | setblock ~54 ~32 ~20 stone_bricks
stage_17.mcfunction 12 | setblock ~55 ~32 ~20 chiseled_stone_bricks
stage_17.mcfunction 13 | setblock ~56 ~32 ~20 stone_bricks
stage_17.mcfunction 14 | setblock ~57 ~32 ~20 stone_bricks
stage_17.mcfunction 15 | setblock ~58 ~32 ~20 stone_bricks
stage_17.mcfunction 16 | setblock ~59 ~32 ~20 chiseled_stone_bricks
stage_17.mcfunction 17 | setblock ~60 ~32 ~20 stone_bricks
stage_17.mcfunction 18 | setblock ~61 ~32 ~20 stone_bricks
stage_17.mcfunction 19 | setblock ~62 ~32 ~20 stone_bricks
stage_17.mcfunction 20 | setblock ~63 ~32 ~20 chiseled_stone_bricks
stage_17.mcfunction 21 | setblock ~64 ~32 ~20 stone_bricks
stage_17.mcfunction 22 | setblock ~65 ~32 ~20 stone_bricks
stage_17.mcfunction 23 | setblock ~66 ~32 ~20 stone_bricks
stage_17.mcfunction 24 | setblock ~67 ~32 ~20 chiseled_stone_bricks
stage_17.mcfunction 25 | setblock ~68 ~32 ~20 stone_bricks
stage_17.mcfunction 26 | setblock ~69 ~32 ~20 stone_bricks
stage_17.mcfunction 27 | setblock ~70 ~32 ~20 stone_bricks
stage_17.mcfunction 28 | setblock ~71 ~32 ~20 chiseled_stone_bricks
stage_17.mcfunction 29 | setblock ~72 ~32 ~20 stone_bricks
stage_17.mcfunction 30 | setblock ~73 ~32 ~20 stone_bricks
stage_17.mcfunction 31 | setblock ~74 ~32 ~20 stone_bricks
stage_17.mcfunction 32 | setblock ~75 ~32 ~20 chiseled_stone_bricks
stage_17.mcfunction 33 | setblock ~76 ~32 ~20 stone_bricks
stage_17.mcfunction 34 | setblock ~77 ~32 ~20 stone_bricks
stage_17.mcfunction 35 | fill ~96 ~-1 ~4 ~168 ~-1 ~48 stone_bricks
stage_17.mcfunction 36 | fill ~96 ~-1 ~49 ~168 ~-1 ~78 stone_bricks
stage_17.mcfunction 37 | fill ~96 ~ ~4 ~168 ~7 ~13 stone_bricks
stage_17.mcfunction 38 | fill ~96 ~ ~69 ~168 ~7 ~78 stone_bricks
stage_17.mcfunction 39 | fill ~96 ~ ~14 ~105 ~7 ~17 stone_bricks
stage_17.mcfunction 40 | fill ~96 ~ ~27 ~105 ~7 ~48 stone_bricks
stage_17.mcfunction 41 | fill ~96 ~ ~49 ~105 ~7 ~68 stone_bricks
stage_17.mcfunction 42 | fill ~96 ~ ~18 ~105 ~7 ~26 air
stage_17.mcfunction 43 | fill ~159 ~ ~14 ~168 ~7 ~48 stone_bricks
stage_17.mcfunction 44 | fill ~159 ~ ~49 ~168 ~7 ~68 stone_bricks
stage_17.mcfunction 45 | fill ~124 ~ ~36 ~132 ~ ~44 stone_bricks
stage_17.mcfunction 46 | setblock ~128 ~ ~40 chiseled_stone_bricks
stage_17.mcfunction 47 | setblock ~124 ~-1 ~20 sea_lantern
stage_17.mcfunction 48 | setblock ~124 ~-1 ~21 sea_lantern
stage_17.mcfunction 49 | setblock ~124 ~-1 ~22 sea_lantern
stage_17.mcfunction 50 | setblock ~124 ~-1 ~23 sea_lantern
stage_18.mcfunction 1 | setblock ~124 ~-1 ~24 sea_lantern
stage_18.mcfunction 2 | setblock ~124 ~-1 ~25 sea_lantern
stage_18.mcfunction 3 | setblock ~124 ~-1 ~26 sea_lantern
stage_18.mcfunction 4 | setblock ~124 ~-1 ~27 sea_lantern
stage_18.mcfunction 5 | setblock ~124 ~-1 ~28 sea_lantern
stage_18.mcfunction 6 | setblock ~124 ~-1 ~29 sea_lantern
stage_18.mcfunction 7 | setblock ~124 ~-1 ~30 sea_lantern
stage_18.mcfunction 8 | setblock ~124 ~-1 ~31 sea_lantern
stage_18.mcfunction 9 | setblock ~124 ~-1 ~32 sea_lantern
stage_18.mcfunction 10 | setblock ~124 ~-1 ~33 sea_lantern
stage_18.mcfunction 11 | setblock ~124 ~-1 ~34 sea_lantern
stage_18.mcfunction 12 | setblock ~124 ~-1 ~35 sea_lantern
stage_18.mcfunction 13 | fill ~108 ~ ~14 ~156 ~3 ~14 stone_bricks
stage_18.mcfunction 14 | fill ~108 ~ ~68 ~156 ~3 ~68 stone_bricks
stage_18.mcfunction 15 | fill ~108 ~ ~15 ~156 ~2 ~15 stone_bricks
stage_18.mcfunction 16 | fill ~108 ~ ~67 ~156 ~2 ~67 stone_bricks
stage_18.mcfunction 17 | fill ~108 ~ ~16 ~156 ~1 ~16 stone_bricks
stage_18.mcfunction 18 | fill ~108 ~ ~66 ~156 ~1 ~66 stone_bricks
stage_18.mcfunction 19 | fill ~108 ~ ~17 ~156 ~ ~17 stone_bricks
stage_18.mcfunction 20 | fill ~108 ~ ~65 ~156 ~ ~65 stone_bricks
stage_18.mcfunction 21 | fill ~122 ~ ~34 ~122 ~4 ~34 cyan_wool
stage_18.mcfunction 22 | fill ~134 ~ ~34 ~134 ~4 ~34 purple_wool
stage_18.mcfunction 23 | fill ~122 ~ ~46 ~122 ~4 ~46 orange_wool
stage_18.mcfunction 24 | fill ~134 ~ ~46 ~134 ~4 ~46 light_gray_wool
stage_18.mcfunction 25 | setblock ~110 ~ ~20 stone_bricks
stage_18.mcfunction 26 | setblock ~110 ~1 ~20 lantern
stage_18.mcfunction 27 | setblock ~110 ~ ~60 stone_bricks
stage_18.mcfunction 28 | setblock ~110 ~1 ~60 lantern
stage_18.mcfunction 29 | setblock ~116 ~ ~20 stone_bricks
stage_18.mcfunction 30 | setblock ~116 ~1 ~20 lantern
stage_18.mcfunction 31 | setblock ~116 ~ ~60 stone_bricks
stage_18.mcfunction 32 | setblock ~116 ~1 ~60 lantern
stage_18.mcfunction 33 | setblock ~140 ~ ~20 stone_bricks
stage_18.mcfunction 34 | setblock ~140 ~1 ~20 lantern
stage_18.mcfunction 35 | setblock ~140 ~ ~60 stone_bricks
stage_18.mcfunction 36 | setblock ~140 ~1 ~60 lantern
stage_18.mcfunction 37 | setblock ~152 ~ ~20 stone_bricks
stage_18.mcfunction 38 | setblock ~152 ~1 ~20 lantern
stage_18.mcfunction 39 | setblock ~152 ~ ~60 stone_bricks
stage_18.mcfunction 40 | setblock ~152 ~1 ~60 lantern
stage_18.mcfunction 41 | fill ~144 ~-1 ~20 ~150 ~16 ~26 stone_bricks
stage_18.mcfunction 42 | fill ~145 ~ ~21 ~149 ~15 ~25 air
stage_18.mcfunction 43 | setblock ~147 ~15 ~23 bell
stage_18.mcfunction 44 | setblock ~147 ~16 ~23 sea_lantern
stage_18.mcfunction 45 | setblock ~128 ~ ~34 chiseled_stone_bricks
stage_18.mcfunction 46 | setblock ~128 ~1 ~34 lectern
stage_18.mcfunction 47 | summon minecraft:armor_stand ~124 ~1 ~36 {CustomName:'{"text":"wing1_flame_squad1"}'}
stage_18.mcfunction 48 | summon minecraft:armor_stand ~125 ~1 ~36 {CustomName:'{"text":"wing1_flame_squad2"}'}
stage_18.mcfunction 49 | summon minecraft:armor_stand ~126 ~1 ~36 {CustomName:'{"text":"wing1_flame_squad3"}'}
stage_18.mcfunction 50 | summon minecraft:armor_stand ~127 ~1 ~36 {CustomName:'{"text":"wing1_claw_squad1"}'}
stage_19.mcfunction 1 | summon minecraft:armor_stand ~128 ~1 ~36 {CustomName:'{"text":"wing1_claw_squad2"}'}
stage_19.mcfunction 2 | summon minecraft:armor_stand ~129 ~1 ~36 {CustomName:'{"text":"wing1_claw_squad3"}'}
stage_19.mcfunction 3 | summon minecraft:armor_stand ~130 ~1 ~36 {CustomName:'{"text":"wing1_tail_squad1"}'}
stage_19.mcfunction 4 | summon minecraft:armor_stand ~131 ~1 ~36 {CustomName:'{"text":"wing1_tail_squad2"}'}
stage_19.mcfunction 5 | summon minecraft:armor_stand ~132 ~1 ~36 {CustomName:'{"text":"wing1_tail_squad3"}'}
stage_19.mcfunction 6 | summon minecraft:armor_stand ~124 ~1 ~38 {CustomName:'{"text":"wing2_flame_squad1"}'}
stage_19.mcfunction 7 | summon minecraft:armor_stand ~125 ~1 ~38 {CustomName:'{"text":"wing2_flame_squad2"}'}
stage_19.mcfunction 8 | summon minecraft:armor_stand ~126 ~1 ~38 {CustomName:'{"text":"wing2_flame_squad3"}'}
stage_19.mcfunction 9 | summon minecraft:armor_stand ~127 ~1 ~38 {CustomName:'{"text":"wing2_claw_squad1"}'}
stage_19.mcfunction 10 | summon minecraft:armor_stand ~128 ~1 ~38 {CustomName:'{"text":"wing2_claw_squad2"}'}
stage_19.mcfunction 11 | summon minecraft:armor_stand ~129 ~1 ~38 {CustomName:'{"text":"wing2_claw_squad3"}'}
stage_19.mcfunction 12 | summon minecraft:armor_stand ~130 ~1 ~38 {CustomName:'{"text":"wing2_tail_squad1"}'}
stage_19.mcfunction 13 | summon minecraft:armor_stand ~131 ~1 ~38 {CustomName:'{"text":"wing2_tail_squad2"}'}
stage_19.mcfunction 14 | summon minecraft:armor_stand ~132 ~1 ~38 {CustomName:'{"text":"wing2_tail_squad3"}'}
stage_19.mcfunction 15 | summon minecraft:armor_stand ~124 ~1 ~40 {CustomName:'{"text":"wing3_flame_squad1"}'}
stage_19.mcfunction 16 | summon minecraft:armor_stand ~125 ~1 ~40 {CustomName:'{"text":"wing3_flame_squad2"}'}
stage_19.mcfunction 17 | summon minecraft:armor_stand ~126 ~1 ~40 {CustomName:'{"text":"wing3_flame_squad3"}'}
stage_19.mcfunction 18 | summon minecraft:armor_stand ~127 ~1 ~40 {CustomName:'{"text":"wing3_claw_squad1"}'}
stage_19.mcfunction 19 | summon minecraft:armor_stand ~128 ~1 ~40 {CustomName:'{"text":"wing3_claw_squad2"}'}
stage_19.mcfunction 20 | summon minecraft:armor_stand ~129 ~1 ~40 {CustomName:'{"text":"wing3_claw_squad3"}'}
stage_19.mcfunction 21 | summon minecraft:armor_stand ~130 ~1 ~40 {CustomName:'{"text":"wing3_tail_squad1"}'}
stage_19.mcfunction 22 | summon minecraft:armor_stand ~131 ~1 ~40 {CustomName:'{"text":"wing3_tail_squad2"}'}
stage_19.mcfunction 23 | summon minecraft:armor_stand ~132 ~1 ~40 {CustomName:'{"text":"wing3_tail_squad3"}'}
stage_19.mcfunction 24 | summon minecraft:armor_stand ~124 ~1 ~42 {CustomName:'{"text":"wing4_flame_squad1"}'}
stage_19.mcfunction 25 | summon minecraft:armor_stand ~125 ~1 ~42 {CustomName:'{"text":"wing4_flame_squad2"}'}
stage_19.mcfunction 26 | summon minecraft:armor_stand ~126 ~1 ~42 {CustomName:'{"text":"wing4_flame_squad3"}'}
stage_19.mcfunction 27 | summon minecraft:armor_stand ~127 ~1 ~42 {CustomName:'{"text":"wing4_claw_squad1"}'}
stage_19.mcfunction 28 | summon minecraft:armor_stand ~128 ~1 ~42 {CustomName:'{"text":"wing4_claw_squad2"}'}
stage_19.mcfunction 29 | summon minecraft:armor_stand ~129 ~1 ~42 {CustomName:'{"text":"wing4_claw_squad3"}'}
stage_19.mcfunction 30 | summon minecraft:armor_stand ~130 ~1 ~42 {CustomName:'{"text":"wing4_tail_squad1"}'}
stage_19.mcfunction 31 | summon minecraft:armor_stand ~131 ~1 ~42 {CustomName:'{"text":"wing4_tail_squad2"}'}
stage_19.mcfunction 32 | summon minecraft:armor_stand ~132 ~1 ~42 {CustomName:'{"text":"wing4_tail_squad3"}'}
stage_19.mcfunction 39 | fill ~96 ~-1 ~80 ~145 ~-1 ~122 stone_bricks
stage_19.mcfunction 40 | fill ~100 ~-1 ~88 ~120 ~7 ~108 stone_bricks
stage_19.mcfunction 41 | fill ~101 ~ ~89 ~119 ~6 ~107 air
stage_19.mcfunction 42 | fill ~107 ~-1 ~88 ~113 ~-1 ~91 smooth_stone
stage_19.mcfunction 43 | fill ~107 ~ ~88 ~113 ~1 ~91 air
stage_19.mcfunction 44 | fill ~107 ~-1 ~105 ~113 ~-1 ~108 smooth_stone
stage_19.mcfunction 45 | fill ~107 ~ ~105 ~113 ~1 ~108 air
stage_19.mcfunction 46 | fill ~100 ~-1 ~97 ~102 ~-1 ~99 smooth_stone
stage_19.mcfunction 47 | fill ~100 ~ ~97 ~102 ~1 ~99 air
stage_19.mcfunction 48 | fill ~118 ~-1 ~97 ~120 ~-1 ~99 smooth_stone
stage_19.mcfunction 49 | fill ~118 ~ ~97 ~120 ~1 ~99 air
stage_19.mcfunction 50 | fill ~107 ~-1 ~109 ~113 ~-1 ~112 smooth_stone
stage_20.mcfunction 1 | fill ~107 ~ ~109 ~113 ~3 ~112 air
stage_20.mcfunction 2 | fill ~101 ~2 ~89 ~119 ~2 ~107 polished_andesite
stage_20.mcfunction 3 | fill ~109 ~2 ~97 ~111 ~2 ~99 air
stage_20.mcfunction 4 | fill ~101 ~5 ~89 ~119 ~5 ~107 polished_andesite
stage_20.mcfunction 5 | fill ~109 ~5 ~97 ~111 ~5 ~99 air
stage_20.mcfunction 6 | fill ~109 ~-1 ~97 ~111 ~-1 ~99 polished_andesite
stage_20.mcfunction 7 | setblock ~110 ~ ~102 lantern
stage_20.mcfunction 8 | setblock ~105 ~ ~98 lantern
stage_20.mcfunction 9 | setblock ~115 ~ ~98 lantern
stage_20.mcfunction 10 | setblock ~101 ~7 ~98 glass
stage_20.mcfunction 11 | setblock ~102 ~7 ~94 glass
stage_20.mcfunction 12 | setblock ~102 ~7 ~95 glass
stage_20.mcfunction 13 | setblock ~102 ~7 ~96 glass
stage_20.mcfunction 14 | setblock ~102 ~7 ~97 glass
stage_20.mcfunction 15 | setblock ~102 ~7 ~99 glass
stage_20.mcfunction 16 | setblock ~102 ~7 ~100 glass
stage_20.mcfunction 17 | setblock ~102 ~7 ~101 glass
stage_20.mcfunction 18 | setblock ~102 ~7 ~102 glass
stage_20.mcfunction 19 | setblock ~103 ~7 ~93 glass
stage_20.mcfunction 20 | setblock ~103 ~7 ~103 glass
stage_20.mcfunction 21 | setblock ~104 ~7 ~92 glass
stage_20.mcfunction 22 | setblock ~104 ~7 ~104 glass
stage_20.mcfunction 23 | setblock ~105 ~7 ~91 glass
stage_20.mcfunction 24 | setblock ~105 ~7 ~105 glass
stage_20.mcfunction 25 | setblock ~106 ~7 ~90 glass
stage_20.mcfunction 26 | setblock ~106 ~7 ~106 glass
stage_20.mcfunction 27 | setblock ~107 ~7 ~90 glass
stage_20.mcfunction 28 | setblock ~107 ~7 ~106 glass
stage_20.mcfunction 29 | setblock ~108 ~7 ~90 glass
stage_20.mcfunction 30 | setblock ~108 ~7 ~106 glass
stage_20.mcfunction 31 | setblock ~109 ~7 ~90 glass
stage_20.mcfunction 32 | setblock ~109 ~7 ~106 glass
stage_20.mcfunction 33 | setblock ~110 ~7 ~89 glass
stage_20.mcfunction 34 | setblock ~110 ~7 ~107 glass
stage_20.mcfunction 35 | setblock ~111 ~7 ~90 glass
stage_20.mcfunction 36 | setblock ~111 ~7 ~106 glass
stage_20.mcfunction 37 | setblock ~112 ~7 ~90 glass
stage_20.mcfunction 38 | setblock ~112 ~7 ~106 glass
stage_20.mcfunction 39 | setblock ~113 ~7 ~90 glass
stage_20.mcfunction 40 | setblock ~113 ~7 ~106 glass
stage_20.mcfunction 41 | setblock ~114 ~7 ~90 glass
stage_20.mcfunction 42 | setblock ~114 ~7 ~106 glass
stage_20.mcfunction 43 | setblock ~115 ~7 ~91 glass
stage_20.mcfunction 44 | setblock ~115 ~7 ~105 glass
stage_20.mcfunction 45 | setblock ~116 ~7 ~92 glass
stage_20.mcfunction 46 | setblock ~116 ~7 ~104 glass
stage_20.mcfunction 47 | setblock ~117 ~7 ~93 glass
stage_20.mcfunction 48 | setblock ~117 ~7 ~103 glass
stage_20.mcfunction 49 | setblock ~118 ~7 ~94 glass
stage_20.mcfunction 50 | setblock ~118 ~7 ~95 glass
stage_21.mcfunction 1 | setblock ~118 ~7 ~96 glass
stage_21.mcfunction 2 | setblock ~118 ~7 ~97 glass
stage_21.mcfunction 3 | setblock ~118 ~7 ~99 glass
stage_21.mcfunction 4 | setblock ~118 ~7 ~100 glass
stage_21.mcfunction 5 | setblock ~118 ~7 ~101 glass
stage_21.mcfunction 6 | setblock ~118 ~7 ~102 glass
stage_21.mcfunction 7 | setblock ~119 ~7 ~98 glass
stage_21.mcfunction 8 | setblock ~103 ~8 ~98 glass
stage_21.mcfunction 9 | setblock ~104 ~8 ~95 glass
stage_21.mcfunction 10 | setblock ~104 ~8 ~96 glass
stage_21.mcfunction 11 | setblock ~104 ~8 ~97 glass
stage_21.mcfunction 12 | setblock ~104 ~8 ~99 glass
stage_21.mcfunction 13 | setblock ~104 ~8 ~100 glass
stage_21.mcfunction 14 | setblock ~104 ~8 ~101 glass
stage_21.mcfunction 15 | setblock ~105 ~8 ~94 glass
stage_21.mcfunction 16 | setblock ~105 ~8 ~102 glass
stage_21.mcfunction 17 | setblock ~106 ~8 ~93 glass
stage_21.mcfunction 18 | setblock ~106 ~8 ~103 glass
stage_21.mcfunction 19 | setblock ~107 ~8 ~92 glass
stage_21.mcfunction 20 | setblock ~107 ~8 ~104 glass
stage_21.mcfunction 21 | setblock ~108 ~8 ~92 glass
stage_21.mcfunction 22 | setblock ~108 ~8 ~104 glass
stage_21.mcfunction 23 | setblock ~109 ~8 ~92 glass
stage_21.mcfunction 24 | setblock ~109 ~8 ~104 glass
stage_21.mcfunction 25 | setblock ~110 ~8 ~91 glass
stage_21.mcfunction 26 | setblock ~110 ~8 ~105 glass
stage_21.mcfunction 27 | setblock ~111 ~8 ~92 glass
stage_21.mcfunction 28 | setblock ~111 ~8 ~104 glass
stage_21.mcfunction 29 | setblock ~112 ~8 ~92 glass
stage_21.mcfunction 30 | setblock ~112 ~8 ~104 glass
stage_21.mcfunction 31 | setblock ~113 ~8 ~92 glass
stage_21.mcfunction 32 | setblock ~113 ~8 ~104 glass
stage_21.mcfunction 33 | setblock ~114 ~8 ~93 glass
stage_21.mcfunction 34 | setblock ~114 ~8 ~103 glass
stage_21.mcfunction 35 | setblock ~115 ~8 ~94 glass
stage_21.mcfunction 36 | setblock ~115 ~8 ~102 glass
stage_21.mcfunction 37 | setblock ~116 ~8 ~95 glass
stage_21.mcfunction 38 | setblock ~116 ~8 ~96 glass
stage_21.mcfunction 39 | setblock ~116 ~8 ~97 glass
stage_21.mcfunction 40 | setblock ~116 ~8 ~99 glass
stage_21.mcfunction 41 | setblock ~116 ~8 ~100 glass
stage_21.mcfunction 42 | setblock ~116 ~8 ~101 glass
stage_21.mcfunction 43 | setblock ~117 ~8 ~98 glass
stage_21.mcfunction 44 | setblock ~105 ~9 ~98 glass
stage_21.mcfunction 45 | setblock ~106 ~9 ~95 glass
stage_21.mcfunction 46 | setblock ~106 ~9 ~96 glass
stage_21.mcfunction 47 | setblock ~106 ~9 ~97 glass
stage_21.mcfunction 48 | setblock ~106 ~9 ~99 glass
stage_21.mcfunction 49 | setblock ~106 ~9 ~100 glass
stage_21.mcfunction 50 | setblock ~106 ~9 ~101 glass
stage_22.mcfunction 1 | setblock ~107 ~9 ~94 glass
stage_22.mcfunction 2 | setblock ~107 ~9 ~102 glass
stage_22.mcfunction 3 | setblock ~108 ~9 ~94 glass
stage_22.mcfunction 4 | setblock ~108 ~9 ~102 glass
stage_22.mcfunction 5 | setblock ~109 ~9 ~94 glass
stage_22.mcfunction 6 | setblock ~109 ~9 ~102 glass
stage_22.mcfunction 7 | setblock ~110 ~9 ~93 glass
stage_22.mcfunction 8 | setblock ~110 ~9 ~103 glass
stage_22.mcfunction 9 | setblock ~111 ~9 ~94 glass
stage_22.mcfunction 10 | setblock ~111 ~9 ~102 glass
stage_22.mcfunction 11 | setblock ~112 ~9 ~94 glass
stage_22.mcfunction 12 | setblock ~112 ~9 ~102 glass
stage_22.mcfunction 13 | setblock ~113 ~9 ~94 glass
stage_22.mcfunction 14 | setblock ~113 ~9 ~102 glass
stage_22.mcfunction 15 | setblock ~114 ~9 ~95 glass
stage_22.mcfunction 16 | setblock ~114 ~9 ~96 glass
stage_22.mcfunction 17 | setblock ~114 ~9 ~97 glass
stage_22.mcfunction 18 | setblock ~114 ~9 ~99 glass
stage_22.mcfunction 19 | setblock ~114 ~9 ~100 glass
stage_22.mcfunction 20 | setblock ~114 ~9 ~101 glass
stage_22.mcfunction 21 | setblock ~115 ~9 ~98 glass
stage_22.mcfunction 22 | setblock ~107 ~10 ~98 glass
stage_22.mcfunction 23 | setblock ~108 ~10 ~96 glass
stage_22.mcfunction 24 | setblock ~108 ~10 ~97 glass
stage_22.mcfunction 25 | setblock ~108 ~10 ~99 glass
stage_22.mcfunction 26 | setblock ~108 ~10 ~100 glass
stage_22.mcfunction 27 | setblock ~109 ~10 ~96 glass
stage_22.mcfunction 28 | setblock ~109 ~10 ~100 glass
stage_22.mcfunction 29 | setblock ~110 ~10 ~95 glass
stage_22.mcfunction 30 | setblock ~110 ~10 ~101 glass
stage_22.mcfunction 31 | setblock ~111 ~10 ~96 glass
stage_22.mcfunction 32 | setblock ~111 ~10 ~100 glass
stage_22.mcfunction 33 | setblock ~112 ~10 ~96 glass
stage_22.mcfunction 34 | setblock ~112 ~10 ~97 glass
stage_22.mcfunction 35 | setblock ~112 ~10 ~99 glass
stage_22.mcfunction 36 | setblock ~112 ~10 ~100 glass
stage_22.mcfunction 37 | setblock ~113 ~10 ~98 glass
stage_22.mcfunction 38 | setblock ~108 ~11 ~98 glass
stage_22.mcfunction 39 | setblock ~109 ~11 ~97 glass
stage_22.mcfunction 40 | setblock ~109 ~11 ~99 glass
stage_22.mcfunction 41 | setblock ~110 ~11 ~96 glass
stage_22.mcfunction 42 | setblock ~110 ~11 ~100 glass
stage_22.mcfunction 43 | setblock ~111 ~11 ~97 glass
stage_22.mcfunction 44 | setblock ~111 ~11 ~99 glass
stage_22.mcfunction 45 | setblock ~112 ~11 ~98 glass
stage_22.mcfunction 46 | setblock ~109 ~12 ~98 glass
stage_22.mcfunction 47 | setblock ~110 ~12 ~97 glass
stage_22.mcfunction 48 | setblock ~110 ~12 ~99 glass
stage_22.mcfunction 49 | setblock ~111 ~12 ~98 glass
stage_22.mcfunction 50 | setblock ~110 ~13 ~98 glass
stage_23.mcfunction 1 | fill ~108 ~ ~89 ~108 ~7 ~89 orange_wool
stage_23.mcfunction 2 | fill ~112 ~ ~89 ~112 ~7 ~89 black_wool
stage_23.mcfunction 3 | fill ~108 ~ ~107 ~108 ~7 ~107 orange_wool
stage_23.mcfunction 4 | fill ~112 ~ ~107 ~112 ~7 ~107 black_wool
stage_23.mcfunction 5 | fill ~126 ~-1 ~100 ~140 ~8 ~110 stone_bricks
stage_23.mcfunction 6 | fill ~127 ~ ~101 ~139 ~7 ~109 air
stage_23.mcfunction 7 | fill ~127 ~-1 ~101 ~139 ~-1 ~109 polished_andesite
stage_23.mcfunction 8 | fill ~126 ~-1 ~104 ~126 ~1 ~105 air
stage_23.mcfunction 9 | setblock ~126 ~2 ~104 stone_brick_stairs
stage_23.mcfunction 10 | setblock ~126 ~2 ~105 stone_brick_stairs
stage_23.mcfunction 11 | setblock ~126 ~3 ~104 stone_bricks
stage_23.mcfunction 12 | setblock ~126 ~3 ~105 stone_bricks
stage_23.mcfunction 13 | setblock ~126 ~2 ~103 stone_bricks
stage_23.mcfunction 14 | setblock ~126 ~2 ~106 stone_bricks
stage_23.mcfunction 15 | setblock ~126 ~3 ~103 stone_bricks
stage_23.mcfunction 16 | setblock ~126 ~3 ~106 stone_bricks
stage_23.mcfunction 17 | setblock ~128 ~2 ~102 lantern
stage_23.mcfunction 18 | setblock ~138 ~2 ~108 lantern
stage_23.mcfunction 19 | summon minecraft:armor_stand ~130 ~ ~105 {CustomName:'{"text":"A rider kneels and the dragon decides."}'}
stage_23.mcfunction 20 | fill ~126 ~-1 ~84 ~140 ~9 ~92 stone_bricks
stage_23.mcfunction 21 | fill ~127 ~ ~85 ~139 ~8 ~91 air
stage_23.mcfunction 22 | fill ~127 ~-1 ~85 ~139 ~-1 ~91 polished_andesite
stage_23.mcfunction 23 | fill ~127 ~2 ~85 ~139 ~2 ~91 stone_bricks
stage_23.mcfunction 24 | fill ~127 ~5 ~85 ~139 ~5 ~91 stone_bricks
stage_23.mcfunction 25 | fill ~132 ~-1 ~84 ~133 ~1 ~84 air
stage_23.mcfunction 26 | setblock ~131 ~2 ~84 stone_brick_stairs
stage_23.mcfunction 27 | setblock ~134 ~2 ~84 stone_brick_stairs
stage_23.mcfunction 28 | setblock ~127 ~2 ~85 air
stage_23.mcfunction 29 | setblock ~127 ~1 ~85 ladder[facing=north]
stage_23.mcfunction 30 | setblock ~127 ~5 ~85 air
stage_23.mcfunction 31 | setblock ~127 ~4 ~85 ladder[facing=north]
stage_23.mcfunction 32 | setblock ~127 ~-1 ~85 ladder[facing=north]
stage_23.mcfunction 33 | fill ~140 ~-1 ~90 ~140 ~1 ~90 air
stage_23.mcfunction 34 | setblock ~129 ~-1 ~86 red_wool
stage_23.mcfunction 35 | setblock ~131 ~-1 ~86 red_wool
stage_23.mcfunction 36 | setblock ~133 ~-1 ~86 red_wool
stage_23.mcfunction 37 | setblock ~135 ~-1 ~86 red_wool
stage_23.mcfunction 38 | setblock ~137 ~-1 ~86 red_wool
stage_23.mcfunction 39 | setblock ~129 ~-1 ~88 red_wool
stage_23.mcfunction 40 | setblock ~131 ~-1 ~88 red_wool
stage_23.mcfunction 41 | setblock ~133 ~-1 ~88 red_wool
stage_23.mcfunction 42 | setblock ~135 ~-1 ~88 red_wool
stage_23.mcfunction 43 | setblock ~137 ~-1 ~88 red_wool
stage_23.mcfunction 44 | setblock ~129 ~-1 ~90 red_wool
stage_23.mcfunction 45 | setblock ~131 ~-1 ~90 red_wool
stage_23.mcfunction 46 | setblock ~133 ~-1 ~90 red_wool
stage_23.mcfunction 47 | setblock ~135 ~-1 ~90 red_wool
stage_23.mcfunction 48 | setblock ~137 ~-1 ~90 red_wool
stage_23.mcfunction 49 | setblock ~129 ~-1 ~92 red_wool
stage_23.mcfunction 50 | setblock ~131 ~-1 ~92 red_wool
stage_24.mcfunction 1 | setblock ~133 ~-1 ~92 red_wool
stage_24.mcfunction 2 | setblock ~135 ~-1 ~92 red_wool
stage_24.mcfunction 3 | setblock ~137 ~-1 ~92 red_wool
stage_24.mcfunction 4 | setblock ~127 ~2 ~87 lantern
stage_24.mcfunction 5 | fill ~142 ~-1 ~87 ~144 ~4 ~93 stone_bricks
stage_24.mcfunction 6 | fill ~143 ~ ~88 ~143 ~3 ~92 air
stage_24.mcfunction 7 | fill ~142 ~-1 ~90 ~142 ~1 ~90 air
stage_24.mcfunction 8 | setblock ~143 ~-1 ~88 red_wool
stage_24.mcfunction 9 | setblock ~143 ~ ~92 lantern
stage_24.mcfunction 10 | fill ~102 ~-1 ~112 ~122 ~5 ~120 stone_bricks
stage_24.mcfunction 11 | fill ~103 ~ ~113 ~121 ~4 ~119 air
stage_24.mcfunction 12 | fill ~103 ~-1 ~113 ~121 ~-1 ~119 polished_andesite
stage_24.mcfunction 13 | fill ~102 ~-1 ~116 ~102 ~1 ~117 air
stage_24.mcfunction 14 | setblock ~102 ~2 ~116 stone_brick_stairs
stage_24.mcfunction 15 | setblock ~102 ~2 ~117 stone_brick_stairs
stage_24.mcfunction 16 | setblock ~106 ~1 ~115 lectern[facing=east]
stage_24.mcfunction 17 | setblock ~110 ~1 ~115 lectern[facing=east]
stage_24.mcfunction 18 | setblock ~114 ~1 ~115 lectern[facing=east]
stage_24.mcfunction 19 | setblock ~108 ~1 ~118 lectern[facing=south]
stage_24.mcfunction 20 | setblock ~112 ~1 ~118 lectern[facing=south]
stage_24.mcfunction 21 | setblock ~106 ~1 ~118 lectern[facing=west]
stage_24.mcfunction 22 | setblock ~116 ~1 ~118 lectern[facing=west]
stage_24.mcfunction 23 | setblock ~118 ~1 ~117 lectern[facing=north]
stage_24.mcfunction 24 | setblock ~118 ~2 ~114 lantern
stage_24.mcfunction 25 | setblock ~104 ~2 ~118 lantern
stage_24.mcfunction 26 | fill ~146 ~ ~80 ~168 ~ ~81 stone
stage_24.mcfunction 27 | fill ~146 ~ ~82 ~168 ~1 ~84 stone
stage_24.mcfunction 28 | fill ~146 ~ ~85 ~168 ~5 ~88 stone
stage_24.mcfunction 29 | fill ~146 ~ ~89 ~168 ~9 ~92 stone
stage_24.mcfunction 30 | fill ~146 ~ ~93 ~168 ~13 ~96 stone
stage_24.mcfunction 31 | fill ~146 ~ ~97 ~168 ~17 ~100 stone
stage_24.mcfunction 32 | fill ~146 ~ ~101 ~168 ~21 ~104 stone
stage_24.mcfunction 33 | fill ~146 ~ ~105 ~168 ~25 ~140 stone
stage_24.mcfunction 34 | fill ~146 ~1 ~82 ~168 ~1 ~82 cobblestone
stage_24.mcfunction 35 | fill ~146 ~2 ~85 ~168 ~5 ~85 cobblestone
stage_24.mcfunction 36 | fill ~146 ~6 ~89 ~168 ~9 ~89 cobblestone
stage_24.mcfunction 37 | fill ~146 ~10 ~93 ~168 ~13 ~93 cobblestone
stage_24.mcfunction 38 | fill ~146 ~14 ~97 ~168 ~17 ~97 cobblestone
stage_24.mcfunction 39 | fill ~146 ~18 ~101 ~168 ~21 ~101 cobblestone
stage_24.mcfunction 40 | fill ~146 ~22 ~105 ~168 ~25 ~105 cobblestone
stage_24.mcfunction 41 | fill ~147 ~1 ~82 ~166 ~1 ~84 stone_bricks
stage_24.mcfunction 42 | fill ~147 ~5 ~85 ~166 ~5 ~87 stone_bricks
stage_24.mcfunction 43 | fill ~147 ~9 ~89 ~166 ~9 ~91 stone_bricks
stage_24.mcfunction 44 | fill ~147 ~13 ~93 ~166 ~13 ~95 stone_bricks
stage_24.mcfunction 45 | fill ~147 ~17 ~97 ~166 ~17 ~99 stone_bricks
stage_24.mcfunction 46 | fill ~147 ~21 ~101 ~166 ~21 ~103 stone_bricks
stage_24.mcfunction 47 | fill ~147 ~25 ~105 ~166 ~25 ~107 stone_bricks
stage_24.mcfunction 48 | fill ~146 ~ ~80 ~168 ~ ~81 stone_bricks
stage_24.mcfunction 49 | fill ~146 ~25 ~105 ~150 ~25 ~140 stone_bricks
stage_24.mcfunction 50 | fill ~161 ~2 ~82 ~161 ~2 ~84 stone_bricks
stage_25.mcfunction 1 | fill ~162 ~2 ~82 ~162 ~3 ~84 stone_bricks
stage_25.mcfunction 2 | fill ~163 ~2 ~82 ~163 ~4 ~84 stone_bricks
stage_25.mcfunction 3 | fill ~164 ~2 ~82 ~164 ~5 ~84 stone_bricks
stage_25.mcfunction 4 | fill ~151 ~6 ~85 ~151 ~6 ~88 stone_bricks
stage_25.mcfunction 5 | fill ~150 ~6 ~85 ~150 ~7 ~88 stone_bricks
stage_25.mcfunction 6 | fill ~149 ~6 ~85 ~149 ~8 ~88 stone_bricks
stage_25.mcfunction 7 | fill ~148 ~6 ~85 ~148 ~9 ~88 stone_bricks
stage_25.mcfunction 8 | fill ~161 ~10 ~89 ~161 ~10 ~92 stone_bricks
stage_25.mcfunction 9 | fill ~162 ~10 ~89 ~162 ~11 ~92 stone_bricks
stage_25.mcfunction 10 | fill ~163 ~10 ~89 ~163 ~12 ~92 stone_bricks
stage_25.mcfunction 11 | fill ~164 ~10 ~89 ~164 ~13 ~92 stone_bricks
stage_25.mcfunction 12 | fill ~151 ~14 ~93 ~151 ~14 ~96 stone_bricks
stage_25.mcfunction 13 | fill ~150 ~14 ~93 ~150 ~15 ~96 stone_bricks
stage_25.mcfunction 14 | fill ~149 ~14 ~93 ~149 ~16 ~96 stone_bricks
stage_25.mcfunction 15 | fill ~148 ~14 ~93 ~148 ~17 ~96 stone_bricks
stage_25.mcfunction 16 | fill ~152 ~2 ~82 ~152 ~2 ~84 oak_wood
stage_25.mcfunction 17 | fill ~159 ~6 ~85 ~159 ~6 ~88 granite
stage_25.mcfunction 18 | fill ~157 ~6 ~85 ~157 ~7 ~88 granite
stage_25.mcfunction 19 | fill ~155 ~6 ~85 ~155 ~8 ~88 granite
stage_25.mcfunction 20 | fill ~153 ~6 ~85 ~153 ~9 ~88 granite
stage_25.mcfunction 21 | fill ~157 ~10 ~89 ~157 ~10 ~92 stone_bricks
stage_25.mcfunction 22 | fill ~157 ~14 ~89 ~157 ~14 ~92 stone_bricks
stage_25.mcfunction 23 | fill ~157 ~11 ~89 ~157 ~13 ~89 stone_bricks
stage_25.mcfunction 24 | fill ~157 ~11 ~92 ~157 ~13 ~92 stone_bricks
stage_25.mcfunction 25 | setblock ~157 ~14 ~91 air
stage_25.mcfunction 26 | fill ~160 ~14 ~93 ~161 ~14 ~96 cobblestone
stage_25.mcfunction 27 | fill ~157 ~14 ~93 ~158 ~15 ~96 cobblestone
stage_25.mcfunction 28 | fill ~154 ~14 ~93 ~155 ~14 ~96 cobblestone
stage_25.mcfunction 29 | setblock ~162 ~14 ~94 cobblestone
stage_25.mcfunction 30 | setblock ~152 ~14 ~95 cobblestone
stage_25.mcfunction 31 | fill ~161 ~18 ~97 ~164 ~21 ~100 stone_bricks
stage_25.mcfunction 32 | fill ~162 ~18 ~98 ~162 ~21 ~98 air
stage_25.mcfunction 33 | fill ~161 ~18 ~98 ~161 ~19 ~98 air
stage_25.mcfunction 34 | setblock ~162 ~18 ~98 ladder
stage_25.mcfunction 35 | setblock ~162 ~19 ~98 ladder
stage_25.mcfunction 36 | setblock ~162 ~20 ~98 ladder
stage_25.mcfunction 37 | setblock ~162 ~21 ~98 ladder
stage_25.mcfunction 38 | fill ~151 ~22 ~101 ~151 ~22 ~104 oak_stairs
stage_25.mcfunction 39 | fill ~150 ~22 ~101 ~150 ~22 ~104 oak_planks
stage_25.mcfunction 40 | fill ~150 ~23 ~101 ~150 ~23 ~104 oak_stairs
stage_25.mcfunction 41 | fill ~149 ~22 ~101 ~149 ~23 ~104 oak_planks
stage_25.mcfunction 42 | fill ~149 ~24 ~101 ~149 ~24 ~104 oak_stairs
stage_25.mcfunction 43 | fill ~148 ~22 ~101 ~148 ~24 ~104 oak_planks
stage_25.mcfunction 44 | fill ~148 ~25 ~101 ~148 ~25 ~104 oak_stairs
stage_25.mcfunction 45 | fill ~148 ~3 ~81 ~148 ~4 ~81 chain
stage_25.mcfunction 46 | fill ~154 ~3 ~81 ~154 ~4 ~81 chain
stage_25.mcfunction 47 | fill ~160 ~3 ~81 ~160 ~4 ~81 chain
stage_25.mcfunction 48 | fill ~148 ~4 ~84 ~148 ~8 ~84 chain
stage_25.mcfunction 49 | fill ~154 ~4 ~84 ~154 ~8 ~84 chain
stage_25.mcfunction 50 | fill ~160 ~4 ~84 ~160 ~8 ~84 chain
stage_26.mcfunction 1 | fill ~148 ~8 ~88 ~148 ~12 ~88 chain
stage_26.mcfunction 2 | fill ~154 ~8 ~88 ~154 ~12 ~88 chain
stage_26.mcfunction 3 | fill ~160 ~8 ~88 ~160 ~12 ~88 chain
stage_26.mcfunction 4 | fill ~148 ~12 ~92 ~148 ~16 ~92 chain
stage_26.mcfunction 5 | fill ~154 ~12 ~92 ~154 ~16 ~92 chain
stage_26.mcfunction 6 | fill ~160 ~12 ~92 ~160 ~16 ~92 chain
stage_26.mcfunction 7 | fill ~148 ~16 ~96 ~148 ~20 ~96 chain
stage_26.mcfunction 8 | fill ~154 ~16 ~96 ~154 ~20 ~96 chain
stage_26.mcfunction 9 | fill ~160 ~16 ~96 ~160 ~20 ~96 chain
stage_26.mcfunction 10 | fill ~148 ~20 ~100 ~148 ~24 ~100 chain
stage_26.mcfunction 11 | fill ~154 ~20 ~100 ~154 ~24 ~100 chain
stage_26.mcfunction 12 | fill ~160 ~20 ~100 ~160 ~24 ~100 chain
stage_26.mcfunction 13 | fill ~146 ~26 ~140 ~168 ~26 ~140 stone_bricks
stage_26.mcfunction 14 | fill ~168 ~26 ~105 ~168 ~26 ~140 stone_bricks
stage_26.mcfunction 15 | fill ~163 ~26 ~108 ~167 ~30 ~112 stone_bricks
stage_26.mcfunction 16 | fill ~164 ~27 ~109 ~166 ~29 ~111 air
stage_26.mcfunction 17 | setblock ~163 ~27 ~110 air
stage_26.mcfunction 18 | setblock ~163 ~28 ~110 air
stage_26.mcfunction 19 | setblock ~165 ~31 ~110 lantern
stage_26.mcfunction 20 | summon minecraft:armor_stand ~165 ~27 ~110 {CustomName:'{"text":"Gauntlet timekeeper"}'}
stage_26.mcfunction 21 | fill ~100 ~-1 ~124 ~101 ~31 ~148 stone
stage_26.mcfunction 22 | fill ~144 ~-1 ~124 ~145 ~31 ~148 stone
stage_26.mcfunction 23 | fill ~100 ~-1 ~147 ~145 ~31 ~148 stone
stage_26.mcfunction 24 | fill ~100 ~32 ~124 ~101 ~32 ~148 stone_bricks
stage_26.mcfunction 25 | fill ~144 ~32 ~124 ~145 ~32 ~148 stone_bricks
stage_26.mcfunction 26 | fill ~100 ~32 ~147 ~145 ~32 ~147 stone_bricks
stage_26.mcfunction 27 | fill ~101 ~-1 ~124 ~101 ~ ~148 stone_bricks
stage_26.mcfunction 28 | fill ~144 ~-1 ~124 ~144 ~ ~148 stone_bricks
stage_26.mcfunction 29 | fill ~100 ~-1 ~147 ~145 ~ ~147 stone_bricks
stage_26.mcfunction 30 | fill ~117 ~-1 ~124 ~119 ~3 ~126 stone_bricks
stage_26.mcfunction 31 | fill ~118 ~ ~125 ~118 ~2 ~125 air
stage_26.mcfunction 32 | fill ~125 ~-1 ~124 ~127 ~3 ~126 stone_bricks
stage_26.mcfunction 33 | fill ~126 ~ ~125 ~126 ~2 ~125 air
stage_26.mcfunction 34 | fill ~117 ~4 ~124 ~127 ~4 ~126 stone_bricks
stage_26.mcfunction 35 | fill ~118 ~-1 ~124 ~126 ~-1 ~124 stone_bricks
stage_26.mcfunction 36 | fill ~121 ~-1 ~125 ~123 ~-1 ~144 dirt_path
stage_26.mcfunction 37 | fill ~102 ~-1 ~126 ~102 ~3 ~144 stone_bricks
stage_26.mcfunction 38 | fill ~103 ~-1 ~126 ~103 ~2 ~144 stone_bricks
stage_26.mcfunction 39 | fill ~104 ~-1 ~126 ~104 ~1 ~144 stone_bricks
stage_26.mcfunction 40 | fill ~105 ~-1 ~126 ~105 ~ ~144 stone_bricks
stage_26.mcfunction 41 | fill ~114 ~ ~145 ~130 ~ ~146 smooth_stone
stage_26.mcfunction 42 | setblock ~114 ~1 ~146 stone_bricks
stage_26.mcfunction 43 | setblock ~114 ~2 ~146 lantern
stage_26.mcfunction 44 | setblock ~130 ~1 ~146 stone_bricks
stage_26.mcfunction 45 | setblock ~130 ~2 ~146 lantern
stage_26.mcfunction 46 | setblock ~141 ~-1 ~126 stone_bricks
stage_26.mcfunction 47 | fill ~141 ~ ~126 ~141 ~2 ~126 white_wool
stage_26.mcfunction 48 | setblock ~141 ~-1 ~130 stone_bricks
stage_26.mcfunction 49 | fill ~141 ~ ~130 ~141 ~2 ~130 orange_wool
stage_26.mcfunction 50 | setblock ~141 ~-1 ~134 stone_bricks
stage_27.mcfunction 1 | fill ~141 ~ ~134 ~141 ~2 ~134 yellow_wool
stage_27.mcfunction 2 | setblock ~141 ~-1 ~138 stone_bricks
stage_27.mcfunction 3 | fill ~141 ~ ~138 ~141 ~2 ~138 lime_wool
stage_27.mcfunction 4 | setblock ~141 ~-1 ~142 stone_bricks
stage_27.mcfunction 5 | fill ~141 ~ ~142 ~141 ~2 ~142 light_blue_wool
stage_27.mcfunction 6 | setblock ~141 ~-1 ~146 stone_bricks
stage_27.mcfunction 7 | fill ~141 ~ ~146 ~141 ~2 ~146 purple_wool
stage_27.mcfunction 8 | fill ~105 ~ ~147 ~107 ~31 ~147 light_blue_stained_glass
stage_27.mcfunction 9 | fill ~105 ~32 ~147 ~107 ~32 ~147 light_blue_stained_glass
stage_27.mcfunction 10 | fill ~105 ~-1 ~145 ~107 ~-1 ~146 light_blue_stained_glass
stage_27.mcfunction 11 | setblock ~106 ~ ~126 short_grass
stage_27.mcfunction 12 | setblock ~106 ~ ~137 short_grass
stage_27.mcfunction 13 | setblock ~106 ~ ~143 short_grass
stage_27.mcfunction 14 | setblock ~107 ~ ~141 short_grass
stage_27.mcfunction 15 | setblock ~108 ~ ~128 short_grass
stage_27.mcfunction 16 | setblock ~108 ~ ~139 short_grass
stage_27.mcfunction 17 | setblock ~108 ~ ~145 short_grass
stage_27.mcfunction 18 | setblock ~109 ~ ~126 short_grass
stage_27.mcfunction 19 | setblock ~109 ~ ~143 short_grass
stage_27.mcfunction 20 | setblock ~110 ~ ~130 short_grass
stage_27.mcfunction 21 | setblock ~110 ~ ~141 allium
stage_27.mcfunction 22 | setblock ~111 ~ ~128 short_grass
stage_27.mcfunction 23 | setblock ~111 ~ ~134 short_grass
stage_27.mcfunction 24 | setblock ~111 ~ ~145 short_grass
stage_27.mcfunction 25 | setblock ~112 ~ ~126 short_grass
stage_27.mcfunction 26 | setblock ~112 ~ ~132 short_grass
stage_27.mcfunction 27 | setblock ~113 ~ ~130 short_grass
stage_27.mcfunction 28 | setblock ~113 ~ ~136 short_grass
stage_27.mcfunction 29 | setblock ~114 ~ ~128 cornflower
stage_27.mcfunction 30 | setblock ~114 ~ ~134 short_grass
stage_27.mcfunction 31 | setblock ~115 ~ ~132 short_grass
stage_27.mcfunction 32 | setblock ~115 ~ ~138 short_grass
stage_27.mcfunction 33 | setblock ~116 ~ ~136 short_grass
stage_27.mcfunction 34 | setblock ~116 ~ ~142 short_grass
stage_27.mcfunction 35 | setblock ~117 ~ ~134 short_grass
stage_27.mcfunction 36 | setblock ~117 ~ ~140 short_grass
stage_27.mcfunction 37 | setblock ~118 ~ ~138 short_grass
stage_27.mcfunction 38 | setblock ~118 ~ ~144 short_grass
stage_27.mcfunction 39 | setblock ~119 ~ ~136 oxeye_daisy
stage_27.mcfunction 40 | setblock ~119 ~ ~142 short_grass
stage_27.mcfunction 41 | setblock ~120 ~ ~129 short_grass
stage_27.mcfunction 42 | setblock ~120 ~ ~140 short_grass
stage_27.mcfunction 43 | setblock ~124 ~ ~127 short_grass
stage_27.mcfunction 44 | setblock ~124 ~ ~133 short_grass
stage_27.mcfunction 45 | setblock ~124 ~ ~144 azure_bluet
stage_27.mcfunction 46 | setblock ~125 ~ ~131 short_grass
stage_27.mcfunction 47 | setblock ~125 ~ ~137 short_grass
stage_27.mcfunction 48 | setblock ~126 ~ ~129 short_grass
stage_27.mcfunction 49 | setblock ~126 ~ ~135 short_grass
stage_27.mcfunction 50 | setblock ~127 ~ ~133 short_grass
stage_28.mcfunction 1 | setblock ~127 ~ ~139 short_grass
stage_28.mcfunction 2 | setblock ~128 ~ ~131 poppy
stage_28.mcfunction 3 | setblock ~128 ~ ~137 short_grass
stage_28.mcfunction 4 | setblock ~129 ~ ~135 short_grass
stage_28.mcfunction 5 | setblock ~129 ~ ~141 short_grass
stage_28.mcfunction 6 | setblock ~130 ~ ~139 short_grass
stage_28.mcfunction 7 | setblock ~131 ~ ~126 short_grass
stage_28.mcfunction 8 | setblock ~131 ~ ~137 short_grass
stage_28.mcfunction 9 | setblock ~131 ~ ~143 short_grass
stage_28.mcfunction 10 | setblock ~132 ~ ~141 short_grass
stage_28.mcfunction 11 | setblock ~133 ~ ~128 short_grass
stage_28.mcfunction 12 | setblock ~133 ~ ~139 cornflower
stage_28.mcfunction 13 | setblock ~133 ~ ~145 short_grass
stage_28.mcfunction 14 | setblock ~134 ~ ~126 short_grass
stage_28.mcfunction 15 | setblock ~134 ~ ~132 short_grass
stage_28.mcfunction 16 | setblock ~134 ~ ~143 short_grass
stage_28.mcfunction 17 | setblock ~135 ~ ~130 short_grass
stage_28.mcfunction 18 | setblock ~136 ~ ~128 short_grass
stage_28.mcfunction 19 | setblock ~136 ~ ~134 short_grass
stage_28.mcfunction 20 | setblock ~136 ~ ~145 short_grass
stage_28.mcfunction 21 | setblock ~137 ~ ~126 allium
stage_28.mcfunction 22 | setblock ~137 ~ ~132 short_grass
stage_28.mcfunction 23 | setblock ~138 ~ ~130 short_grass
stage_28.mcfunction 24 | setblock ~138 ~ ~136 short_grass
stage_28.mcfunction 25 | setblock ~139 ~ ~134 short_grass
stage_28.mcfunction 26 | setblock ~139 ~ ~140 short_grass
stage_28.mcfunction 27 | setblock ~140 ~ ~132 short_grass
stage_28.mcfunction 28 | setblock ~141 ~ ~136 short_grass
stage_28.mcfunction 29 | setblock ~142 ~ ~140 short_grass
stage_28.mcfunction 30 | setblock ~143 ~ ~127 short_grass
stage_28.mcfunction 31 | setblock ~143 ~ ~138 short_grass
stage_28.mcfunction 32 | setblock ~143 ~ ~144 short_grass
stage_28.mcfunction 34 | fill ~16 ~-2 ~94 ~48 ~-2 ~140 grass_block
stage_28.mcfunction 35 | fill ~49 ~-2 ~94 ~70 ~-2 ~140 grass_block
stage_28.mcfunction 36 | fill ~16 ~-1 ~94 ~48 ~-1 ~140 air
stage_28.mcfunction 37 | fill ~49 ~-1 ~94 ~70 ~-1 ~140 air
stage_28.mcfunction 38 | fill ~42 ~-2 ~116 ~44 ~-2 ~118 moss_block
stage_28.mcfunction 39 | fill ~19 ~-1 ~97 ~19 ~1 ~97 oak_log
stage_28.mcfunction 40 | fill ~18 ~2 ~96 ~20 ~2 ~98 oak_leaves
stage_28.mcfunction 41 | fill ~18 ~3 ~97 ~20 ~3 ~97 oak_leaves
stage_28.mcfunction 42 | fill ~19 ~3 ~96 ~19 ~3 ~98 oak_leaves
stage_28.mcfunction 43 | fill ~26 ~-1 ~99 ~26 ~1 ~99 oak_log
stage_28.mcfunction 44 | fill ~25 ~2 ~98 ~27 ~2 ~100 oak_leaves
stage_28.mcfunction 45 | fill ~25 ~3 ~99 ~27 ~3 ~99 oak_leaves
stage_28.mcfunction 46 | fill ~26 ~3 ~98 ~26 ~3 ~100 oak_leaves
stage_28.mcfunction 47 | fill ~33 ~-1 ~97 ~33 ~1 ~97 oak_log
stage_28.mcfunction 48 | fill ~32 ~2 ~96 ~34 ~2 ~98 oak_leaves
stage_28.mcfunction 49 | fill ~32 ~3 ~97 ~34 ~3 ~97 oak_leaves
stage_28.mcfunction 50 | fill ~33 ~3 ~96 ~33 ~3 ~98 oak_leaves
stage_29.mcfunction 1 | fill ~40 ~-1 ~99 ~40 ~1 ~99 oak_log
stage_29.mcfunction 2 | fill ~39 ~2 ~98 ~41 ~2 ~100 oak_leaves
stage_29.mcfunction 3 | fill ~39 ~3 ~99 ~41 ~3 ~99 oak_leaves
stage_29.mcfunction 4 | fill ~40 ~3 ~98 ~40 ~3 ~100 oak_leaves
stage_29.mcfunction 5 | fill ~47 ~-1 ~97 ~47 ~1 ~97 oak_log
stage_29.mcfunction 6 | fill ~46 ~2 ~96 ~48 ~2 ~98 oak_leaves
stage_29.mcfunction 7 | fill ~46 ~3 ~97 ~48 ~3 ~97 oak_leaves
stage_29.mcfunction 8 | fill ~47 ~3 ~96 ~47 ~3 ~98 oak_leaves
stage_29.mcfunction 9 | fill ~54 ~-1 ~99 ~54 ~1 ~99 oak_log
stage_29.mcfunction 10 | fill ~53 ~2 ~98 ~55 ~2 ~100 oak_leaves
stage_29.mcfunction 11 | fill ~53 ~3 ~99 ~55 ~3 ~99 oak_leaves
stage_29.mcfunction 12 | fill ~54 ~3 ~98 ~54 ~3 ~100 oak_leaves
stage_29.mcfunction 13 | fill ~61 ~-1 ~97 ~61 ~1 ~97 oak_log
stage_29.mcfunction 14 | fill ~60 ~2 ~96 ~62 ~2 ~98 oak_leaves
stage_29.mcfunction 15 | fill ~60 ~3 ~97 ~62 ~3 ~97 oak_leaves
stage_29.mcfunction 16 | fill ~61 ~3 ~96 ~61 ~3 ~98 oak_leaves
stage_29.mcfunction 17 | fill ~68 ~-1 ~99 ~68 ~1 ~99 oak_log
stage_29.mcfunction 18 | fill ~67 ~2 ~98 ~69 ~2 ~100 oak_leaves
stage_29.mcfunction 19 | fill ~67 ~3 ~99 ~69 ~3 ~99 oak_leaves
stage_29.mcfunction 20 | fill ~68 ~3 ~98 ~68 ~3 ~100 oak_leaves
stage_29.mcfunction 21 | fill ~22 ~-1 ~105 ~22 ~1 ~105 oak_log
stage_29.mcfunction 22 | fill ~21 ~2 ~104 ~23 ~2 ~106 oak_leaves
stage_29.mcfunction 23 | fill ~21 ~3 ~105 ~23 ~3 ~105 oak_leaves
stage_29.mcfunction 24 | fill ~22 ~3 ~104 ~22 ~3 ~106 oak_leaves
stage_29.mcfunction 25 | fill ~36 ~-1 ~105 ~36 ~1 ~105 oak_log
stage_29.mcfunction 26 | fill ~35 ~2 ~104 ~37 ~2 ~106 oak_leaves
stage_29.mcfunction 27 | fill ~35 ~3 ~105 ~37 ~3 ~105 oak_leaves
stage_29.mcfunction 28 | fill ~36 ~3 ~104 ~36 ~3 ~106 oak_leaves
stage_29.mcfunction 29 | fill ~50 ~-1 ~105 ~50 ~1 ~105 oak_log
stage_29.mcfunction 30 | fill ~49 ~2 ~104 ~51 ~2 ~106 oak_leaves
stage_29.mcfunction 31 | fill ~49 ~3 ~105 ~51 ~3 ~105 oak_leaves
stage_29.mcfunction 32 | fill ~50 ~3 ~104 ~50 ~3 ~106 oak_leaves
stage_29.mcfunction 33 | fill ~64 ~-1 ~105 ~64 ~1 ~105 oak_log
stage_29.mcfunction 34 | fill ~63 ~2 ~104 ~65 ~2 ~106 oak_leaves
stage_29.mcfunction 35 | fill ~63 ~3 ~105 ~65 ~3 ~105 oak_leaves
stage_29.mcfunction 36 | fill ~64 ~3 ~104 ~64 ~3 ~106 oak_leaves
stage_29.mcfunction 37 | fill ~18 ~-1 ~114 ~18 ~1 ~114 oak_log
stage_29.mcfunction 38 | fill ~17 ~2 ~113 ~19 ~2 ~115 oak_leaves
stage_29.mcfunction 39 | fill ~17 ~3 ~114 ~19 ~3 ~114 oak_leaves
stage_29.mcfunction 40 | fill ~18 ~3 ~113 ~18 ~3 ~115 oak_leaves
stage_29.mcfunction 41 | fill ~20 ~-1 ~122 ~20 ~1 ~122 oak_log
stage_29.mcfunction 42 | fill ~19 ~2 ~121 ~21 ~2 ~123 oak_leaves
stage_29.mcfunction 43 | fill ~19 ~3 ~122 ~21 ~3 ~122 oak_leaves
stage_29.mcfunction 44 | fill ~20 ~3 ~121 ~20 ~3 ~123 oak_leaves
stage_29.mcfunction 45 | fill ~18 ~-1 ~130 ~18 ~1 ~130 oak_log
stage_29.mcfunction 46 | fill ~17 ~2 ~129 ~19 ~2 ~131 oak_leaves
stage_29.mcfunction 47 | fill ~17 ~3 ~130 ~19 ~3 ~130 oak_leaves
stage_29.mcfunction 48 | fill ~18 ~3 ~129 ~18 ~3 ~131 oak_leaves
stage_29.mcfunction 49 | fill ~21 ~-1 ~138 ~21 ~1 ~138 oak_log
stage_29.mcfunction 50 | fill ~20 ~2 ~137 ~22 ~2 ~139 oak_leaves
stage_30.mcfunction 1 | fill ~20 ~3 ~138 ~22 ~3 ~138 oak_leaves
stage_30.mcfunction 2 | fill ~21 ~3 ~137 ~21 ~3 ~139 oak_leaves
stage_30.mcfunction 3 | fill ~68 ~-1 ~112 ~68 ~1 ~112 oak_log
stage_30.mcfunction 4 | fill ~67 ~2 ~111 ~69 ~2 ~113 oak_leaves
stage_30.mcfunction 5 | fill ~67 ~3 ~112 ~69 ~3 ~112 oak_leaves
stage_30.mcfunction 6 | fill ~68 ~3 ~111 ~68 ~3 ~113 oak_leaves
stage_30.mcfunction 7 | fill ~66 ~-1 ~120 ~66 ~1 ~120 oak_log
stage_30.mcfunction 8 | fill ~65 ~2 ~119 ~67 ~2 ~121 oak_leaves
stage_30.mcfunction 9 | fill ~65 ~3 ~120 ~67 ~3 ~120 oak_leaves
stage_30.mcfunction 10 | fill ~66 ~3 ~119 ~66 ~3 ~121 oak_leaves
stage_30.mcfunction 11 | fill ~69 ~-1 ~129 ~69 ~1 ~129 oak_log
stage_30.mcfunction 12 | fill ~68 ~2 ~128 ~70 ~2 ~130 oak_leaves
stage_30.mcfunction 13 | fill ~68 ~3 ~129 ~70 ~3 ~129 oak_leaves
stage_30.mcfunction 14 | fill ~69 ~3 ~128 ~69 ~3 ~130 oak_leaves
stage_30.mcfunction 15 | fill ~67 ~-1 ~137 ~67 ~1 ~137 oak_log
stage_30.mcfunction 16 | fill ~66 ~2 ~136 ~68 ~2 ~138 oak_leaves
stage_30.mcfunction 17 | fill ~66 ~3 ~137 ~68 ~3 ~137 oak_leaves
stage_30.mcfunction 18 | fill ~67 ~3 ~136 ~67 ~3 ~138 oak_leaves
stage_30.mcfunction 19 | fill ~24 ~-1 ~133 ~24 ~1 ~133 oak_log
stage_30.mcfunction 20 | fill ~23 ~2 ~132 ~25 ~2 ~134 oak_leaves
stage_30.mcfunction 21 | fill ~23 ~3 ~133 ~25 ~3 ~133 oak_leaves
stage_30.mcfunction 22 | fill ~24 ~3 ~132 ~24 ~3 ~134 oak_leaves
stage_30.mcfunction 23 | fill ~31 ~-1 ~136 ~31 ~1 ~136 oak_log
stage_30.mcfunction 24 | fill ~30 ~2 ~135 ~32 ~2 ~137 oak_leaves
stage_30.mcfunction 25 | fill ~30 ~3 ~136 ~32 ~3 ~136 oak_leaves
stage_30.mcfunction 26 | fill ~31 ~3 ~135 ~31 ~3 ~137 oak_leaves
stage_30.mcfunction 27 | fill ~38 ~-1 ~134 ~38 ~1 ~134 oak_log
stage_30.mcfunction 28 | fill ~37 ~2 ~133 ~39 ~2 ~135 oak_leaves
stage_30.mcfunction 29 | fill ~37 ~3 ~134 ~39 ~3 ~134 oak_leaves
stage_30.mcfunction 30 | fill ~38 ~3 ~133 ~38 ~3 ~135 oak_leaves
stage_30.mcfunction 31 | fill ~45 ~-1 ~137 ~45 ~1 ~137 oak_log
stage_30.mcfunction 32 | fill ~44 ~2 ~136 ~46 ~2 ~138 oak_leaves
stage_30.mcfunction 33 | fill ~44 ~3 ~137 ~46 ~3 ~137 oak_leaves
stage_30.mcfunction 34 | fill ~45 ~3 ~136 ~45 ~3 ~138 oak_leaves
stage_30.mcfunction 35 | fill ~58 ~-1 ~133 ~58 ~1 ~133 oak_log
stage_30.mcfunction 36 | fill ~57 ~2 ~132 ~59 ~2 ~134 oak_leaves
stage_30.mcfunction 37 | fill ~57 ~3 ~133 ~59 ~3 ~133 oak_leaves
stage_30.mcfunction 38 | fill ~58 ~3 ~132 ~58 ~3 ~134 oak_leaves
stage_30.mcfunction 39 | fill ~65 ~-1 ~137 ~65 ~1 ~137 oak_log
stage_30.mcfunction 40 | fill ~64 ~2 ~136 ~66 ~2 ~138 oak_leaves
stage_30.mcfunction 41 | fill ~64 ~3 ~137 ~66 ~3 ~137 oak_leaves
stage_30.mcfunction 42 | fill ~65 ~3 ~136 ~65 ~3 ~138 oak_leaves
stage_30.mcfunction 43 | fill ~28 ~-1 ~139 ~28 ~1 ~139 oak_log
stage_30.mcfunction 44 | fill ~27 ~2 ~138 ~29 ~2 ~140 oak_leaves
stage_30.mcfunction 45 | fill ~27 ~3 ~139 ~29 ~3 ~139 oak_leaves
stage_30.mcfunction 46 | fill ~28 ~3 ~138 ~28 ~3 ~140 oak_leaves
stage_30.mcfunction 47 | fill ~42 ~-1 ~139 ~42 ~1 ~139 oak_log
stage_30.mcfunction 48 | fill ~41 ~2 ~138 ~43 ~2 ~140 oak_leaves
stage_30.mcfunction 49 | fill ~41 ~3 ~139 ~43 ~3 ~139 oak_leaves
stage_30.mcfunction 50 | fill ~42 ~3 ~138 ~42 ~3 ~140 oak_leaves
stage_31.mcfunction 1 | fill ~56 ~-1 ~139 ~56 ~1 ~139 oak_log
stage_31.mcfunction 2 | fill ~55 ~2 ~138 ~57 ~2 ~140 oak_leaves
stage_31.mcfunction 3 | fill ~55 ~3 ~139 ~57 ~3 ~139 oak_leaves
stage_31.mcfunction 4 | fill ~56 ~3 ~138 ~56 ~3 ~140 oak_leaves
stage_31.mcfunction 5 | setblock ~17 ~-1 ~114 short_grass
stage_31.mcfunction 6 | setblock ~18 ~-1 ~119 azure_bluet
stage_31.mcfunction 7 | setblock ~19 ~-1 ~95 poppy
stage_31.mcfunction 8 | setblock ~19 ~-1 ~124 dandelion
stage_31.mcfunction 9 | setblock ~20 ~-1 ~100 short_grass
stage_31.mcfunction 10 | setblock ~20 ~-1 ~129 lily_of_the_valley
stage_31.mcfunction 11 | setblock ~21 ~-1 ~105 oxeye_daisy
stage_31.mcfunction 12 | setblock ~21 ~-1 ~134 cornflower
stage_31.mcfunction 13 | setblock ~22 ~-1 ~110 short_grass
stage_31.mcfunction 14 | setblock ~22 ~-1 ~139 short_grass
stage_31.mcfunction 15 | setblock ~23 ~-1 ~115 allium
stage_31.mcfunction 16 | setblock ~24 ~-1 ~120 poppy
stage_31.mcfunction 17 | setblock ~25 ~-1 ~96 short_grass
stage_31.mcfunction 18 | setblock ~25 ~-1 ~125 short_grass
stage_31.mcfunction 19 | setblock ~26 ~-1 ~101 azure_bluet
stage_31.mcfunction 20 | setblock ~26 ~-1 ~130 oxeye_daisy
stage_31.mcfunction 21 | setblock ~27 ~-1 ~106 dandelion
stage_31.mcfunction 22 | setblock ~27 ~-1 ~135 short_grass
stage_31.mcfunction 23 | setblock ~28 ~-1 ~111 lily_of_the_valley
stage_31.mcfunction 24 | setblock ~29 ~-1 ~116 cornflower
stage_31.mcfunction 25 | setblock ~30 ~-1 ~121 short_grass
stage_31.mcfunction 26 | setblock ~31 ~-1 ~97 allium
stage_31.mcfunction 27 | setblock ~31 ~-1 ~126 azure_bluet
stage_31.mcfunction 28 | setblock ~32 ~-1 ~102 poppy
stage_31.mcfunction 29 | setblock ~32 ~-1 ~131 dandelion
stage_31.mcfunction 30 | setblock ~33 ~-1 ~107 short_grass
stage_31.mcfunction 31 | setblock ~33 ~-1 ~136 lily_of_the_valley
stage_31.mcfunction 32 | setblock ~34 ~-1 ~112 oxeye_daisy
stage_31.mcfunction 33 | setblock ~37 ~-1 ~98 cornflower
stage_31.mcfunction 34 | setblock ~38 ~-1 ~103 short_grass
stage_31.mcfunction 35 | setblock ~38 ~-1 ~132 short_grass
stage_31.mcfunction 36 | setblock ~39 ~-1 ~108 azure_bluet
stage_31.mcfunction 37 | setblock ~39 ~-1 ~137 oxeye_daisy
stage_31.mcfunction 38 | setblock ~43 ~-1 ~99 short_grass
stage_31.mcfunction 39 | setblock ~43 ~-1 ~128 short_grass
stage_31.mcfunction 40 | setblock ~44 ~-1 ~104 allium
stage_31.mcfunction 41 | setblock ~44 ~-1 ~133 azure_bluet
stage_31.mcfunction 42 | setblock ~45 ~-1 ~138 dandelion
stage_31.mcfunction 43 | setblock ~48 ~-1 ~95 dandelion
stage_31.mcfunction 44 | setblock ~49 ~-1 ~100 lily_of_the_valley
stage_31.mcfunction 45 | setblock ~50 ~-1 ~134 poppy
stage_31.mcfunction 46 | setblock ~51 ~-1 ~139 short_grass
stage_31.mcfunction 47 | setblock ~54 ~-1 ~96 short_grass
stage_31.mcfunction 48 | setblock ~55 ~-1 ~101 oxeye_daisy
stage_31.mcfunction 49 | setblock ~55 ~-1 ~130 cornflower
stage_31.mcfunction 50 | setblock ~56 ~-1 ~106 short_grass
stage_32.mcfunction 1 | setblock ~56 ~-1 ~135 short_grass
stage_32.mcfunction 2 | setblock ~57 ~-1 ~111 allium
stage_32.mcfunction 3 | setblock ~58 ~-1 ~116 poppy
stage_32.mcfunction 4 | setblock ~59 ~-1 ~121 short_grass
stage_32.mcfunction 5 | setblock ~60 ~-1 ~97 azure_bluet
stage_32.mcfunction 6 | setblock ~60 ~-1 ~126 oxeye_daisy
stage_32.mcfunction 7 | setblock ~61 ~-1 ~102 dandelion
stage_32.mcfunction 8 | setblock ~61 ~-1 ~131 short_grass
stage_32.mcfunction 9 | setblock ~62 ~-1 ~107 lily_of_the_valley
stage_32.mcfunction 10 | setblock ~62 ~-1 ~136 allium
stage_32.mcfunction 11 | setblock ~63 ~-1 ~112 cornflower
stage_32.mcfunction 12 | setblock ~64 ~-1 ~117 short_grass
stage_32.mcfunction 13 | setblock ~65 ~-1 ~122 azure_bluet
stage_32.mcfunction 14 | setblock ~66 ~-1 ~98 poppy
stage_32.mcfunction 15 | setblock ~66 ~-1 ~127 dandelion
stage_32.mcfunction 16 | setblock ~67 ~-1 ~103 short_grass
stage_32.mcfunction 17 | setblock ~67 ~-1 ~132 lily_of_the_valley
stage_32.mcfunction 18 | setblock ~68 ~-1 ~108 oxeye_daisy
stage_32.mcfunction 19 | setblock ~68 ~-1 ~137 cornflower
stage_32.mcfunction 20 | setblock ~69 ~-1 ~113 short_grass
stage_32.mcfunction 21 | setblock ~50 ~-2 ~124 stone_bricks
stage_32.mcfunction 22 | summon minecraft:armor_stand ~50 ~-1 ~124 {CustomName:'{"text":"Roll-keeper"}'}
stage_32.mcfunction 23 | setblock ~50 ~-1 ~123 lectern
stage_32.mcfunction 24 | setblock ~50 ~-1 ~130 lodestone
stage_32.mcfunction 25 | setblock ~50 ~ ~130 air
stage_32.mcfunction 26 | fill ~90 ~-1 ~18 ~96 ~-1 ~22 stone_bricks
stage_32.mcfunction 27 | fill ~92 ~-1 ~23 ~95 ~-1 ~48 stone_bricks
stage_32.mcfunction 28 | fill ~92 ~-1 ~49 ~95 ~-1 ~79 stone_bricks
stage_32.mcfunction 29 | fill ~71 ~-1 ~116 ~98 ~-1 ~120 stone_bricks
stage_32.mcfunction 30 | setblock ~45 ~32 ~20 air
stage_32.mcfunction 31 | setblock ~46 ~32 ~20 air
stage_32.mcfunction 32 | setblock ~5 ~33 ~20 stone_pressure_plate
stage_32.mcfunction 33 | setblock ~86 ~33 ~20 stone_pressure_plate
stage_32.mcfunction 34 | setblock ~128 ~ ~46 stone_pressure_plate
stage_32.mcfunction 35 | setblock ~43 ~-1 ~115 stone_pressure_plate
stage_32.mcfunction 45 | spawnpoint @p ~8 ~0 ~66
summon_dragon.mcfunction 1 | summon basgiath:dragon ~43 ~-1 ~117
total run-parts with ~: 2877
[0m
[0m$ [0mwc -l java/com/basgiath/*.java java/build.gradle java/settings.gradle java/gradle.properties; echo ---; grep -rn "spawnpoint\|cp_east\|cp_quad\|cp_valley" java/com/basgiath/*.java scripts/*.py | head -20
zsh:1: no matches found: java/com/basgiath/*.java
zsh:1: no matches found: java/com/basgiath/*.java
---
[0m
[0m$ [0mgrep -rc "positioned" java/src/main/resources/data/basgiath/function/*.mcfunction | grep -v ':0' ; echo "=== spawnpoint lines ==="; grep -rn "spawnpoint" java/src/main/resources/data/basgiath/function/ addon/behavior_pack/functions/basgiath/ 2>/dev/null; echo "=== tests referencing spawnpoint/hoist ==="; grep -rn "spawnpoint\|positioned" scripts/test_editions.py scripts/test_release.py 2>/dev/null | head -30
java/src/main/resources/data/basgiath/function/live.mcfunction:61
=== spawnpoint lines ===
java/src/main/resources/data/basgiath/function/stage_32.mcfunction:45:spawnpoint @p ~8 ~0 ~66
java/src/main/resources/data/basgiath/function/live.mcfunction:9:execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~78 ~32 ~14 as @a[dx=12,dy=3,dz=14,tag=!cp_east] run spawnpoint @s ~84 ~33 ~20
java/src/main/resources/data/basgiath/function/live.mcfunction:11:execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~124 ~0 ~44 as @a[dx=10,dy=3,dz=8,tag=!cp_quad] run spawnpoint @s ~128 ~0 ~48
java/src/main/resources/data/basgiath/function/live.mcfunction:13:execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~38 ~-2 ~112 as @a[dx=12,dy=4,dz=12,tag=!cp_valley] run spawnpoint @s ~43 ~-1 ~117
addon/behavior_pack/functions/basgiath/stage_32.mcfunction:45:spawnpoint @p ~8 ~0 ~66
addon/behavior_pack/functions/basgiath/live.mcfunction:9:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~78,y=~32,z=~14,dx=12,dy=3,dz=14,tag=!cp_east] run spawnpoint @s ~84 ~33 ~20
addon/behavior_pack/functions/basgiath/live.mcfunction:11:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~124,y=~0,z=~44,dx=10,dy=3,dz=8,tag=!cp_quad] run spawnpoint @s ~128 ~0 ~48
addon/behavior_pack/functions/basgiath/live.mcfunction:13:execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~38,y=~-2,z=~112,dx=12,dy=4,dz=12,tag=!cp_valley] run spawnpoint @s ~43 ~-1 ~117
=== tests referencing spawnpoint/hoist ===
scripts/test_editions.py:147:# parse takes its whole function down with it. The offset moves into `positioned`.
scripts/test_editions.py:150:    "a relative box in the chain becomes a positioned",
scripts/test_editions.py:152:    'execute as @e[type=minecraft:armor_stand,name="a",limit=1] at @s positioned ~4 ~32 ~14'
scripts/test_editions.py:156:    "a relative box in the run command hangs the positioned on the chain",
scripts/test_editions.py:158:    'execute as @e[name="a"] at @s positioned ~4 ~32 ~14'
scripts/test_release.py:321:    for needle in ("spawnpoint", "cp_west", "cp_east", "cp_quad", "cp_valley", "~0.18"):
scripts/test_release.py:434:        "spawnpoint @p ~8 ~0 ~66",
[0m
[0m$ [0mls reports/audit/pack-free-basgiath-java/java/src/main/java/com/basgiath/ 2>/dev/null || ls java/src/main/java/com/basgiath/; echo ---; wc -l java/src/main/java/com/basgiath/*.java java/build.gradle java/settings.gradle java/gradle.properties
Basgiath.java
BasgiathClient.java
BasgiathCommands.java
BasgiathContent.java
BasgiathData.java
BasgiathEvents.java
BasgiathForms.java
BasgiathNetwork.java
BasgiathSmokeTest.java
Codices.java
DragonEntity.java
DragonModel.java
FlightHud.java
Keepers.java
Signets.java
Vault.java
---
      54 java/src/main/java/com/basgiath/Basgiath.java
     167 java/src/main/java/com/basgiath/BasgiathClient.java
      63 java/src/main/java/com/basgiath/BasgiathCommands.java
      96 java/src/main/java/com/basgiath/BasgiathContent.java
     187 java/src/main/java/com/basgiath/BasgiathData.java
     226 java/src/main/java/com/basgiath/BasgiathEvents.java
     373 java/src/main/java/com/basgiath/BasgiathForms.java
      37 java/src/main/java/com/basgiath/BasgiathNetwork.java
     257 java/src/main/java/com/basgiath/BasgiathSmokeTest.java
      80 java/src/main/java/com/basgiath/Codices.java
     117 java/src/main/java/com/basgiath/DragonEntity.java
     145 java/src/main/java/com/basgiath/DragonModel.java
     185 java/src/main/java/com/basgiath/FlightHud.java
     134 java/src/main/java/com/basgiath/Keepers.java
     111 java/src/main/java/com/basgiath/Signets.java
     112 java/src/main/java/com/basgiath/Vault.java
     137 java/build.gradle
      19 java/settings.gradle
      40 java/gradle.properties
    2540 total
[0m
[0m$ [0msed -n 130,240p scripts/test_editions.py; echo "=========== _split / _extract / hoist ==========="; sed -n 138,240p scripts/editions.py
"a lectern direction becomes a cardinal",
    to_java('setblock ~1 ~2 ~3 lectern["direction"=3]'),
    "setblock ~1 ~2 ~3 lectern[facing=west]",
)
check_raises("an unknown block state stops the build", 'setblock ~ ~ ~ stone["mystery"=1]')

# Java renamed this one in 1.17; Bedrock never did. Passing it through unlisted is
# how the whole live function failed to parse on Java the first time.
check(
    "a grass path becomes a dirt path",
    to_java("setblock ~1 ~2 ~3 grass_path"),
    "setblock ~1 ~2 ~3 dirt_path",
)
check_raises("an unlisted block stops the build", "setblock ~ ~ ~ mystery_block")

# --- relative selectors -------------------------------------------------------
# Java 1.21.1 will not parse `x=~4` in a selector, and a selector that does not
# parse takes its whole function down with it. The offset moves into `positioned`.

check(
    "a relative box in the chain becomes a positioned",
    to_java('execute as @e[type=armor_stand,name="a",c=1] at @s as @a[x=~4,y=~32,z=~14,dx=10,dy=3,dz=14] run tag @s add x'),
    'execute as @e[type=minecraft:armor_stand,name="a",limit=1] at @s positioned ~4 ~32 ~14'
    ' as @a[dx=10,dy=3,dz=14] run tag @s add x',
)
check(
    "a relative box in the run command hangs the positioned on the chain",
    to_java('execute as @e[name="a"] at @s run tag @a[x=~4,y=~32,z=~14,dx=10,dy=3,dz=14] add cp_west'),
    'execute as @e[name="a"] at @s positioned ~4 ~32 ~14'
    ' run tag @a[dx=10,dy=3,dz=14] add cp_west',
)
check_raises(
    "a relative origin with no box size stops the build",
    "execute at @s as @a[x=~4,y=~32,z=~14] run tag @s add x",
)

# --- the deliberate drops ----------------------------------------------------

check("tickingarea drops", to_java("tickingarea remove college_a"), None)
check(
    "an anchored tickingarea drops under its own name",
    to_java('execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea remove college_a'),
    None,
)
check(
    "an on_area_loaded schedule drops",
    to_java("schedule on_area_loaded add tickingarea college_b basgiath/fill_far"),
    None,
)
check(
    "the drop key names the inner verb, not execute",
    drop_key('execute as @e[name="x"] at @s run tickingarea remove college_a'),
    "tickingarea",
)

# --- strictness ---------------------------------------------------------------

check_raises("an unknown verb stops the build", "clone ~ ~ ~ ~1 ~1 ~1")
check_raises("an unknown entity stops the build", 'summon wither "x" ~ ~ ~')
check_raises("an unknown effect stops the build", "effect @p levitation 8 0 true")
check_raises("an unknown particle stops the build", "particle minecraft:heart ~ ~ ~")
check_raises("an unknown gamerule stops the build", "gamerule pvp true")


# --- the promise that Bedrock does not move ----------------------------------


def check_generator_output() -> None:
    """Every line the generator builds must be readable by the Java dialect.

    A line the dialect cannot read is a hole in the Java world. This walks the
    real command list rather than a fixture, so a new zone command is caught the
    day it is written.
    """
    import build_map as bm

    unreadable: list[str] = []
    for line in bm.geometry():
        try:
            to_java(line)
        except TranslationError as exc:
            unreadable.append(str(exc))
    for block in (bm.live_text(), bm.SUMMON, bm.RUN_START, bm.RUN_STOP, bm.build_text(1), bm.raise_text()):
        for line in block.split("\n"):
            if not line.strip():
                continue
            try:
                to_java(line)
            except TranslationError as exc:
                unreadable.append(str(exc))
    for line in unreadable[:5]:
        FAILURES.append(f"the generator emits a line the Java dialect cannot read: {line}")


def check_no_bedrock_ids_in_the_tree() -> None:
    """No Bedrock-only id may reach the shipped Java datapack."""
    tree = ROOT / "java" / "src" / "main" / "resources"
    if not tree.exists():
        FAILURES.append("the Java datapack tree is missing. Run python3 scripts/build_map.py first.")
        return
    for path in tree.rglob("*.mcfunction"):
        text = path.read_text(encoding="utf-8")
        for bad in BEDROCK_ONLY:
            if bad in text:
                FAILURES.append(f"{path.relative_to(ROOT)} carries the Bedrock-only id {bad!r}")
    tag = tree / "data" / "minecraft" / "tags" / "function" / "tick.json"
    if not tag.exists():
        FAILURES.append("the Java tree has no minecraft:tick tag, so basgiath:tick never runs")


check_generator_output()
=========== _split / _extract / hoist ===========
def _split_relative_box(token: str) -> tuple[str | None, str]:
    """Pull a relative box out of a selector.

    Bedrock accepts relative coordinates in a selector: ``@a[x=~4,y=~32,z=~14,
    dx=10,dy=3,dz=14]`` means "a box 10 by 3 by 14, starting four blocks east and
    so on from here". Java 1.21.1 rejects the ``~`` and fails to parse the command,
    which takes the whole function down at load time.

    Java reaches the same box a different way: set the execution position with
    ``positioned``, then let a bare ``dx,dy,dz`` selector measure from it. So the
    offset moves out of the selector and into the execute chain.

    Returns (the offset as a ``positioned`` suffix, or None, and the rewritten
    selector). A relative box with no ``dx``/``dy``/``dz`` stops the build: a
    degenerate box has no Java equivalent worth guessing at.
    """
    head, sep, body = token.partition("[")
    if not sep or not token.startswith("@"):
        return None, token
    options = body.rstrip("]").split(",")
    offset: dict[str, str] = {}
    kept: list[str] = []
    for option in options:
        key, _, value = option.partition("=")
        if key in ("x", "y", "z") and value.startswith("~"):
            offset[key] = value
        else:
            kept.append(option)
    if not offset:
        return None, token
    missing = [axis for axis in ("x", "y", "z") if axis not in offset]
    if missing:
        raise TranslationError(
            f"the selector {token!r} gives a relative {offset} without the "
            f"missing {missing}. A partly relative box cannot be hoisted."
        )
    if not any(option.partition("=")[0] in ("dx", "dy", "dz") for option in kept):
        raise TranslationError(
            f"the selector {token!r} gives a relative origin but no dx/dy/dz, so "
            "the box it means is ambiguous. Java cannot express it."
        )
    positioned = f"positioned {offset['x']} {offset['y']} {offset['z']}"
    rewritten = head + ("[" + ",".join(kept) + "]" if kept else "")
    return positioned, rewritten


_CHAIN_SELECTOR_RE = re.compile(r"\b(as|at)\s+(@[a-z]\[[^\]]*\])")


def _hoist_in_chain(prefix: str) -> str:
    """Rewrite an execute chain, putting ``positioned`` before each relative box.

    The rewrite is a substitution over the selectors themselves, not a re-tokenise
    and re-join. A re-join would put spaces back into anything it did not parse
    cleanly, and NBT is not whitespace-tolerant in the places that matters.
    """
    def replace(match: re.Match[str]) -> str:
        keyword, selector = match.group(1), match.group(2)
        positioned, rewritten = _split_relative_box(selector)
        if positioned is None:
            return match.group(0)
        # `positioned` belongs before the `as`/`at` it feeds, so the selector still
        # measures from the position it saw.
        return f"{positioned} {keyword} {rewritten}"

    return _CHAIN_SELECTOR_RE.sub(replace, prefix)


def _extract_from_command(command: str) -> tuple[str, str | None]:
    """Strip relative boxes out of a run command.

    A ``positioned`` cannot go inside a run command, so the offset comes out and
    the caller appends it to the end of the execute chain, one step before ``run``.
    That is the position the selector would otherwise have measured from.
    """
    positioned: str | None = None

    def replace(match: re.Match[str]) -> str:
        nonlocal positioned
        offset, rewritten = _split_relative_box(match.group(0))
        if offset is not None:
            positioned = offset
        return rewritten

    return _SELECTOR_RE.sub(replace, command), positioned


def _java_selectors(text: str) -> str:
    """Rewrite the selectors in a command for Java.

    Two rewrites, both of which bite silently if they are missed:

    - Bedrock `c=N` is Java `limit=N`. An untranslated `c=` makes the selector
      throw at run time.
    - A `type=` argument carries an entity id, and an entity id is namespaced.
      `unless entity @e[type=dragon_rider:dragon]` guards the dragon summon. Left
      alone on Java the guard never matches anything, so it is always true, and
      the dragon is summoned again on every single tick.
    """

    def fix(match: re.Match[str]) -> str:
        body = re.sub(r"(?<=[,\[])c=(\d+)", r"limit=\1", match.group(0))
[0m
[0m$ [0mPYTHONDONTWRITEBYTECODE=1 python3 - <<'EOF'
import sys, pathlib, difflib
sys.path.insert(0,'scripts')
import editions
bed = pathlib.Path('addon/behavior_pack/functions/basgiath')
jav = pathlib.Path('java/src/main/resources/data/basgiath/function')
same=diff=err=0
diffs=[]
for f in sorted(bed.glob('*.mcfunction')):
    out=[]
    for line in f.read_text().splitlines():
        try:
            j = editions.to_java(line)
        except Exception as e:
            err+=1; diffs.append(('ERR',f.name,line,str(e))); continue
        out.append(j if j is not None else line)
    ship = (jav/f.name).read_text().splitlines() if (jav/f.name).exists() else None
    if ship is None:
        diffs.append(('MISSING',f.name,'','')); continue
    if out==ship: same+=1
    else:
        diff+=1
        for l in difflib.unified_diff(ship,out,lineterm='',n=0):
            if l.startswith(('---','+++','@@')): continue
            diffs.append((f.name,'',l[:200],''))
print('identical files:',same,'differing:',diff,'errors:',err)
for d in diffs[:40]: print(d)
print('bedrock files:',len(list(bed.glob("*.mcfunction"))),'java files:',len(list(jav.glob("*.mcfunction"))))
EOF
identical files: 66 differing: 1 errors: 0
('build.mcfunction', '', '+execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea remove college_a', '')
('build.mcfunction', '', '+execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea add circle ~40 ~32 ~40 4 college_a true', '')
('build.mcfunction', '', '+execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea remove college_b', '')
('build.mcfunction', '', '+execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea add circle ~120 ~32 ~40 4 college_b true', '')
('build.mcfunction', '', '+execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea remove college_c', '')
('build.mcfunction', '', '+execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea add circle ~40 ~32 ~110 4 college_c true', '')
('build.mcfunction', '', '+execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea remove college_d', '')
('build.mcfunction', '', '+execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tickingarea add circle ~120 ~32 ~110 4 college_d true', '')
('build.mcfunction', '', '+schedule on_area_loaded add tickingarea college_b basgiath/fill_far', '')
('build.mcfunction', '', '+schedule on_area_loaded add tickingarea college_d basgiath/fill_far', '')
bedrock files: 67 java files: 67
[0m
[0m$ [0mgrep -rnoE '(@[a-z](\[[^]]*\])?)' addon/behavior_pack/functions/basgiath/ | grep -oE '\[[^]]*\]' | sort -u | head -60; echo "=== selector keys in Bedrock tree ==="; grep -rhoE '\[[^]]*\]' addon/behavior_pack/functions/basgiath/ | tr -d '[]' | tr ',' '\n' | sed 's/=.*//' | sort | uniq -c; echo "=== generator source selector keys ==="; grep -rhoE '@[a-z]\[[^]]*\]' scripts/*.py scripts/zones/*.py | tr -d '[]' | tr ',' '\n' | sed 's/=.*//' | sort | uniq -c
[dx=63,dy=2,dz=2]
[tag=!rope_touch]
[tag=bondcall,tag=!relic]
[tag=bonded,tag=!bondcall]
[tag=gate_run]
[tag=relic,tag=!trial]
[tag=rope_touch,tag=!rope_told]
[tag=rope_touch]
[tag=timed_run]
[type=armor_stand,name="A rider kneels and the dragon decides."]
[type=armor_stand,name="build_anchor",c=1]
[type=armor_stand,name="build_anchor"]
[type=armor_stand,name="Gauntlet timekeeper"]
[type=armor_stand,name="Roll-keeper"]
[type=armor_stand,name="wing1_claw_squad1"]
[type=armor_stand,name="wing1_claw_squad2"]
[type=armor_stand,name="wing1_claw_squad3"]
[type=armor_stand,name="wing1_flame_squad1"]
[type=armor_stand,name="wing1_flame_squad2"]
[type=armor_stand,name="wing1_flame_squad3"]
[type=armor_stand,name="wing1_tail_squad1"]
[type=armor_stand,name="wing1_tail_squad2"]
[type=armor_stand,name="wing1_tail_squad3"]
[type=armor_stand,name="wing2_claw_squad1"]
[type=armor_stand,name="wing2_claw_squad2"]
[type=armor_stand,name="wing2_claw_squad3"]
[type=armor_stand,name="wing2_flame_squad1"]
[type=armor_stand,name="wing2_flame_squad2"]
[type=armor_stand,name="wing2_flame_squad3"]
[type=armor_stand,name="wing2_tail_squad1"]
[type=armor_stand,name="wing2_tail_squad2"]
[type=armor_stand,name="wing2_tail_squad3"]
[type=armor_stand,name="wing3_claw_squad1"]
[type=armor_stand,name="wing3_claw_squad2"]
[type=armor_stand,name="wing3_claw_squad3"]
[type=armor_stand,name="wing3_flame_squad1"]
[type=armor_stand,name="wing3_flame_squad2"]
[type=armor_stand,name="wing3_flame_squad3"]
[type=armor_stand,name="wing3_tail_squad1"]
[type=armor_stand,name="wing3_tail_squad2"]
[type=armor_stand,name="wing3_tail_squad3"]
[type=armor_stand,name="wing4_claw_squad1"]
[type=armor_stand,name="wing4_claw_squad2"]
[type=armor_stand,name="wing4_claw_squad3"]
[type=armor_stand,name="wing4_flame_squad1"]
[type=armor_stand,name="wing4_flame_squad2"]
[type=armor_stand,name="wing4_flame_squad3"]
[type=armor_stand,name="wing4_tail_squad1"]
[type=armor_stand,name="wing4_tail_squad2"]
[type=armor_stand,name="wing4_tail_squad3"]
[type=dragon_rider:dragon]
[x=~124,y=~0,z=~44,dx=10,dy=3,dz=8,tag=!cp_quad]
[x=~124,y=~0,z=~44,dx=10,dy=3,dz=8]
[x=~146,y=~1,z=~80,dx=23,dy=1,dz=2,tag=!gate_run]
[x=~146,y=~1,z=~80,dx=23,dy=1,dz=2]
[x=~146,y=~26,z=~105,dx=23,dy=1,dz=36,tag=gate_run]
[x=~148,y=~12,z=~92,dx=1,dy=5,dz=1,tag=!rope_cool]
[x=~148,y=~12,z=~92,dx=1,dy=5,dz=1]
[x=~148,y=~16,z=~96,dx=1,dy=5,dz=1,tag=!rope_cool]
[x=~148,y=~16,z=~96,dx=1,dy=5,dz=1]
=== selector keys in Bedrock tree ===
   1  after a dragon chooses you."}
   1  and it is not the choosing."}
   1  and Tail."}
   1  candidate"}
   1  Claw
   1  nothing held back. Only you and the keeper will know it."}
   1  shaped like the one that chose you."}
  16 "direction"
   6 "facing_direction"
   1 "objective":"gate_sec"}}
   1 "objective":"run_sec"}}
   2 {"score":{"name":"@s"
   1 {"text":" seconds."}
   1 {"text":"§7Course clock stopped."}
   1 {"text":"A dragon has chosen you. You did not choose it. Stand still and let it look."}
   1 {"text":"A dragon waits on the moss pad. Mount it and fly."}
   1 {"text":"A relic mark burns onto your arm
   1 {"text":"§bCourse  "}
   1 {"text":"§bCourse 0s"}
   1 {"text":"Building"}
   1 {"text":"Cross the Parapet"}
   1 {"text":"Each section holds three squads. Nine marks stand in three groups of three."}
   1 {"text":"Each wing carries three sections: Flame
   1 {"text":"Fan-made. Not official. Not affiliated with any publisher. The glowing stairs are in front of you. A fall from the span sends you back here. Cross the Parapet. The signet stone waits in the dell
   1 {"text":"First-years hold the back two rows of the square until a name is read."}
   1 {"text":"Gauntlet complete. Your time: "}
   1 {"text":"Give the keeper the full name
   1 {"text":"Hold your seat. The dragon will fly and turn. Do not let go."}
   1 {"text":"Keep to the middle path. The dragons watch. This walk is for them to look
   1 {"text":"Raise the college first. Run /function basgiath/build"}
   1 {"text":"Roll call. Four wings answer in this courtyard. Find your row."}
   1 {"text":"s"}
   1 {"text":"Stay still"}
   1 {"text":"The college is rising. Stay still for 15 seconds. Fan-made. Not official. Not affiliated with any publisher."}
   1 {"text":"The scribes read the death roll. We answer for the cadets who did not live to stand here."}
   1 {"text":"The span is one block wide. A fall sends you back to the ground."}
   1 {"text":"Welcome
   1 {"text":"Wingleaders and section leaders are third years. A rare second year may lead a squad."}
   1 {"text":"You grabbed a rope. The run adds 30 seconds."}
   1 {"text":"You held. Walk south to the roll-keeper and give the full name."}
 221 c
  61 dx
  61 dy
  61 dz
 262 name
  71 tag
 263 type
  60 x
  60 y
  60 z
=== generator source selector keys ===
   2 @a{box}
   1 @a{CROSSED_BOX}
   4 @a{start}
   1 @a{summit}
   3 @adx
  23 @atag
  14 @ax
   2 @e…
   3 @ename
  38 @etype
  26 c
  13 dx
  16 dy
  16 dz
   2 limit
  32 name
  20 tag
  14 y
  14 z
[0m
[0m$ [0mgrep -rn "effect " addon/behavior_pack/functions/basgiath/*.mcfunction | head; echo "=== _effect source ==="; sed -n 485,510p scripts/editions.py; echo "=== strictness: any extra-arity setblock/fill in tree? ==="; grep -rncE '^(setblock|fill) .*' addon/behavior_pack/functions/basgiath/*.mcfunction | head -5; grep -rnE '^(setblock|fill) ([^ ]+ ){3,6}[^ ]+ .+' addon/behavior_pack/functions/basgiath/*.mcfunction | head
addon/behavior_pack/functions/basgiath/build.mcfunction:20:execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] invisibility 999999 1 true
addon/behavior_pack/functions/basgiath/build.mcfunction:21:execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] resistance 999999 255 true
addon/behavior_pack/functions/basgiath/raise.mcfunction:1:effect @p slow_falling 8 0 true
addon/behavior_pack/functions/basgiath/raise.mcfunction:2:effect @p resistance 8 5 true
=== _effect source ===
def _effect(line: str, args: list[str]) -> str:
    """Java spells it `effect give`, and namespaces the effect."""
    if len(args) < 2:
        raise TranslationError(f"short effect: {line!r}")
    name = EFFECT_MAP.get(args[1])
    if name is None:
        raise TranslationError(
            f"the Java dialect has no effect mapping for {args[1]!r}. "
            "Add it to EFFECT_MAP in scripts/editions.py."
        )
    return _join(["effect", "give", args[0], name, *args[2:]])


def _schedule(line: str, args: list[str]) -> str | None:
    """Java has one schedule form, and it counts in ticks with a `t` suffix."""
    if not args:
        raise TranslationError(f"short schedule: {line!r}")
    if args[0] == "delay":
        # schedule delay add <function> <ticks>
        if len(args) != 4 or args[1] != "add":
            raise TranslationError(f"unknown schedule delay shape: {line!r}")
        return _join(["schedule", "function", _java_function(args[2]), f"{args[3]}t"])
    if args[0] == "on_area_loaded":
        return None  # recorded in DROPPED
    raise TranslationError(f"unknown schedule form {args[0]!r} in {line!r}")

=== strictness: any extra-arity setblock/fill in tree? ===
addon/behavior_pack/functions/basgiath/build.mcfunction:0
addon/behavior_pack/functions/basgiath/far_01.mcfunction:50
addon/behavior_pack/functions/basgiath/far_02.mcfunction:50
addon/behavior_pack/functions/basgiath/far_03.mcfunction:50
addon/behavior_pack/functions/basgiath/far_04.mcfunction:50
addon/behavior_pack/functions/basgiath/far_01.mcfunction:1:fill ~ ~-2 ~49 ~48 ~-2 ~150 stone
addon/behavior_pack/functions/basgiath/far_01.mcfunction:2:fill ~49 ~-2 ~ ~170 ~-2 ~48 stone
addon/behavior_pack/functions/basgiath/far_01.mcfunction:3:fill ~49 ~-2 ~49 ~170 ~-2 ~150 stone
addon/behavior_pack/functions/basgiath/far_01.mcfunction:4:fill ~ ~-1 ~49 ~48 ~-1 ~150 grass_block
addon/behavior_pack/functions/basgiath/far_01.mcfunction:5:fill ~49 ~-1 ~ ~170 ~-1 ~48 grass_block
addon/behavior_pack/functions/basgiath/far_01.mcfunction:6:fill ~49 ~-1 ~49 ~170 ~-1 ~150 grass_block
addon/behavior_pack/functions/basgiath/far_01.mcfunction:7:fill ~49 ~-1 ~12 ~77 ~1 ~28 stone_bricks
addon/behavior_pack/functions/basgiath/far_03.mcfunction:38:fill ~6 ~-1 ~62 ~9 ~-1 ~68 sea_lantern
addon/behavior_pack/functions/basgiath/far_03.mcfunction:39:fill ~78 ~-1 ~12 ~90 ~32 ~28 stone_bricks
addon/behavior_pack/functions/basgiath/far_03.mcfunction:40:fill ~79 ~ ~13 ~89 ~31 ~27 air
[0m
[0m$ [0msed -n 347,435p scripts/editions.py
def to_java(line: str) -> str | None:
    """One Bedrock command as its Java equivalent. None means Java has no form for it."""
    prefix, command = _inner(line)
    tokens = _tokens(command)
    if not tokens:
        return None
    verb, args = tokens[0], tokens[1:]

    out: str | None

    if verb in ("setblock", "fill"):
        # Same argument order on both editions: coordinates, then the block.
        if verb == "setblock":
            if len(args) < 4:
                raise TranslationError(f"short setblock: {line!r}")
            out = _join([verb, *args[:3], _java_block(args[3])])
        else:
            if len(args) < 7:
                raise TranslationError(f"short fill: {line!r}")
            out = _join([verb, *args[:6], _java_block(args[6])])

    elif verb in ("scoreboard", "tag", "spawnpoint", "tp", "weather", "gamemode", "time", "kill"):
        # Identical on both editions. kill @e[type=armor_stand] resolves the
        # default minecraft namespace on Java, so it needs no rewrite.
        out = command

    elif verb == "summon":
        out = _summon(line, args)

    elif verb == "tellraw":
        if len(args) < 2:
            raise TranslationError(f"short tellraw: {line!r}")
        out = _join([verb, args[0], _java_text(_join(args[1:]))])

    elif verb == "titleraw":
        out = _titleraw(line, args)

    elif verb == "gamerule":
        if len(args) != 2:
            raise TranslationError(f"unexpected gamerule shape: {line!r}")
        key = GAMERULE_MAP.get(args[0].lower())
        if key is None:
            raise TranslationError(
                f"the Java dialect has no gamerule mapping for {args[0]!r}. "
                "Add it to GAMERULE_MAP in scripts/editions.py."
            )
        out = _join([verb, key, args[1]])

    elif verb == "function":
        out = _join([verb, _java_function(args[0])])

    elif verb == "particle":
        out = _particle(line, args)

    elif verb == "effect":
        out = _effect(line, args)

    elif verb == "schedule":
        out = _schedule(line, args)

    elif verb == "tickingarea":
        out = None  # recorded in DROPPED

    else:
        raise TranslationError(
            f"the Java dialect does not know the command {verb!r} in {line!r}. "
            "Teach it in scripts/editions.py, or the Java jar ships without it."
        )

    if out is None:
        return None

    # Java cannot read a relative coordinate inside a selector, so each one moves
    # into a `positioned` on the execute chain. A relative box in the run command
    # has no chain of its own, so its offset joins the end of the chain instead.
    out, from_command = _extract_from_command(out)
    if prefix:
        prefix = _hoist_in_chain(prefix)
        if from_command:
            prefix = f"{prefix} {from_command}"
        return f"execute {_java_selectors(prefix)} run {_java_selectors(out)}"
    if from_command:
        return f"execute {from_command} run {_java_selectors(out)}"
    return _java_selectors(out)


def _summon(line: str, args: list[str]) -> str:
    """Bedrock names the entity inline; Java names it in NBT."""
    if not args:
[0m
[0m◈ [0mParallel Web Search "Minecraft Bedrock /effect command syntax hideParticles particles parameter 1.21"
[0m
[0m$ [0mPYTHONDONTWRITEBYTECODE=1 python3 - <<'EOF'
import glob,re
# exact arity check for setblock/fill and particle in Bedrock tree
bad=[]
for f in sorted(glob.glob('addon/behavior_pack/functions/basgiath/*.mcfunction')):
    for n,l in enumerate(open(f),1):
        l=l.strip()
        if l.startswith('execute '):
            m=re.search(r' run (setblock|fill|particle) ', l)
            if not m: continue
            cmd=l[m.start()+4:]
        elif l.startswith(('setblock ','fill ','particle ')):
            cmd=l
        else: continue
        t=cmd.split()
        v=t[0]
        exp={'setblock':5,'fill':8,'particle':5}[v]
        if len(t)!=exp:
            bad.append((f.split('/')[-1],n,len(t),exp,cmd[:120]))
print('arity outliers:',len(bad))
for b in bad[:20]: print(b)
EOF
arity outliers: 0
[0m
[0m◈ [0mParallel Web Search "Minecraft Java 1.21 tellraw score component "name" selector "@s" objective resolve"
