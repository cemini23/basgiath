scoreboard players add bg_wind map_state 1
execute if score bg_wind map_state matches 4.. run scoreboard players set bg_wind map_state 0
execute if score bg_wind map_state matches 0 positioned ~15 ~33 ~19 as @a[dx=13,dy=2,dz=2] at @s run tp @s ~ ~ ~0.18
execute if score bg_wind map_state matches 0 positioned ~65 ~33 ~19 as @a[dx=13,dy=2,dz=2] at @s run tp @s ~ ~ ~0.18
particle minecraft:smoke ~20 ~34 ~20 0 0 0 0 1 normal
particle minecraft:smoke ~40 ~34 ~20 0 0 0 0 1 normal
particle minecraft:smoke ~55 ~34 ~20 0 0 0 0 1 normal
execute positioned ~4 ~32 ~14 as @a[dx=10,dy=3,dz=14,tag=!cp_west] run tellraw @s {"text":"The span is one block wide. A fall sends you back to the ground."}
execute positioned ~4 ~32 ~14 run tag @a[dx=10,dy=3,dz=14] add cp_west
execute positioned ~78 ~32 ~14 as @a[dx=12,dy=3,dz=14,tag=!cp_east] run spawnpoint @s ~84 ~33 ~20
execute positioned ~78 ~32 ~14 run tag @a[dx=12,dy=3,dz=14] add cp_east
execute positioned ~124 ~0 ~44 as @a[dx=10,dy=3,dz=8,tag=!cp_quad] run spawnpoint @s ~128 ~0 ~48
execute positioned ~124 ~0 ~44 run tag @a[dx=10,dy=3,dz=8] add cp_quad
execute positioned ~38 ~-2 ~112 as @a[dx=12,dy=4,dz=12,tag=!cp_valley] run spawnpoint @s ~43 ~-1 ~117
execute positioned ~38 ~-2 ~112 run tag @a[dx=12,dy=4,dz=12] add cp_valley
scoreboard players add bg_storm map_state 1
execute if score bg_storm map_state matches 200.. run scoreboard players set bg_storm map_state 0
execute if score bg_storm map_state matches 0 run weather thunder 999999
scoreboard players add @a[tag=timed_run] run_tick 1
execute as @a[tag=timed_run] run scoreboard players operation @s run_sec = @s run_tick
scoreboard players operation @a[tag=timed_run] run_sec /= bg_twenty map_state
execute as @a[tag=timed_run] run title @s actionbar [{"text":"§bCourse  "},{"score":{"name":"@s","objective":"run_sec"}},{"text":"s"}]
scoreboard players add bg_clock map_state 1
execute positioned ~146 ~1 ~80 as @a[dx=23,dy=1,dz=2,tag=!gate_run] run tag @s remove gate_done
execute positioned ~146 ~1 ~80 as @a[dx=23,dy=1,dz=2,tag=!gate_run] run tag @s add gate_run
execute positioned ~146 ~1 ~80 as @a[dx=23,dy=1,dz=2] run scoreboard players operation @s gate_start = bg_clock map_state
execute positioned ~146 ~1 ~80 as @a[dx=23,dy=1,dz=2] run scoreboard players set @s gate_pen 0
execute as @a[tag=gate_run] run scoreboard players operation @s gate_time = bg_clock map_state
execute as @a[tag=gate_run] run scoreboard players operation @s gate_time -= @s gate_start
execute as @a[tag=gate_run] run scoreboard players operation @s gate_time += @s gate_pen
execute as @a[tag=gate_run] run scoreboard players operation @s gate_sec = @s gate_time
execute as @a[tag=gate_run] run scoreboard players operation @s gate_sec /= bg_twenty map_state
execute positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] run tag @s add gate_done
execute positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] unless score @s gate_best matches 0.. run scoreboard players set @s gate_best 0
execute positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] if score @s gate_best matches 0 run scoreboard players operation @s gate_best = @s gate_time
execute positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] if score @s gate_best matches 1.. run scoreboard players operation @s gate_best < @s gate_time
execute positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] run title @s title [{"text":"Gauntlet complete. Your time: "},{"score":{"name":"@s","objective":"gate_sec"}},{"text":" seconds."}]
execute positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] run give @s basgiath:silver_mark 3
execute positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] run tag @s remove gate_run
execute positioned ~148 ~3 ~81 as @a[dx=1,dy=2,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~148 ~3 ~81 run tag @a[dx=1,dy=2,dz=1] add rope_touch
execute positioned ~154 ~3 ~81 as @a[dx=1,dy=2,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~154 ~3 ~81 run tag @a[dx=1,dy=2,dz=1] add rope_touch
execute positioned ~160 ~3 ~81 as @a[dx=1,dy=2,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~160 ~3 ~81 run tag @a[dx=1,dy=2,dz=1] add rope_touch
execute positioned ~148 ~4 ~84 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~148 ~4 ~84 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~154 ~4 ~84 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~154 ~4 ~84 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~160 ~4 ~84 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~160 ~4 ~84 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~148 ~8 ~88 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~148 ~8 ~88 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~154 ~8 ~88 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~154 ~8 ~88 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~160 ~8 ~88 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~160 ~8 ~88 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~148 ~12 ~92 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~148 ~12 ~92 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~154 ~12 ~92 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~154 ~12 ~92 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~160 ~12 ~92 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~160 ~12 ~92 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~148 ~16 ~96 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~148 ~16 ~96 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~154 ~16 ~96 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~154 ~16 ~96 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~160 ~16 ~96 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~160 ~16 ~96 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~148 ~20 ~100 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~148 ~20 ~100 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~154 ~20 ~100 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~154 ~20 ~100 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute positioned ~160 ~20 ~100 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute positioned ~160 ~20 ~100 run tag @a[dx=1,dy=5,dz=1] add rope_touch
tag @a[tag=rope_touch] add rope_cool
tag @a[tag=!rope_touch] remove rope_cool
tag @a[tag=!rope_touch] remove rope_told
execute as @a[tag=rope_touch,tag=!rope_told] run title @s actionbar {"text":"You grabbed a rope. The run adds 30 seconds."}
tag @a[tag=rope_touch] add rope_told
scoreboard players add bg_spinline map_state 1
execute if score bg_spinline map_state matches 10.. run scoreboard players set bg_spinline map_state 0
particle minecraft:smoke ~152 ~3 ~83 0 0 0 0 1 normal
execute if score bg_spinline map_state matches 5 run particle minecraft:smoke ~152 ~3 ~82 0 0 0 0 1 normal
execute positioned ~48 ~-2 ~122 as @a[dx=4,dy=3,dz=4,tag=flew,tag=!named] run tellraw @s {"text":"Give the keeper the full name, nothing held back. Only you and the keeper will know it."}
execute positioned ~48 ~-2 ~122 as @a[dx=4,dy=3,dz=4,tag=flew,tag=!named] run tag @s add named
execute positioned ~38 ~1 ~112 as @a[dx=12,dy=24,dz=12,tag=trial,tag=!flew] run tellraw @s {"text":"You held. Walk south to the roll-keeper and give the full name."}
execute positioned ~38 ~1 ~112 as @a[dx=12,dy=24,dz=12,tag=trial,tag=!flew] run tag @s add flew
execute as @a[tag=relic,tag=!trial] run tellraw @s {"text":"Hold your seat. The dragon will fly and turn. Do not let go."}
execute as @a[tag=relic,tag=!trial] run tag @s add trial
execute as @a[tag=bondcall,tag=!relic] run tellraw @s {"text":"A relic mark burns onto your arm, shaped like the one that chose you."}
execute as @a[tag=bondcall,tag=!relic] run tag @s add relic
execute as @a[tag=bonded,tag=!bondcall] at @s run summon basgiath:dragon ~1 ~ ~
execute as @a[tag=bonded,tag=!bondcall] run scoreboard players set bg_bond map_state 1
execute as @a[tag=bonded,tag=!bondcall] run tellraw @s {"text":"A dragon has chosen you. You did not choose it. Stand still and let it look."}
execute as @a[tag=bonded,tag=!bondcall] run give @s basgiath:copper_mark 5
execute as @a[tag=bonded,tag=!bondcall] run tag @s add bondcall
execute positioned ~38 ~-2 ~112 as @a[dx=12,dy=4,dz=12,tag=crossed,tag=!bonded] run tag @s add bonded
execute positioned ~15 ~33 ~12 as @a[dx=62,dy=8,dz=16] run tag @s add crossed
