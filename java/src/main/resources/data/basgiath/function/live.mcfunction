scoreboard players add bg_wind map_state 1
execute if score bg_wind map_state matches 4.. run scoreboard players set bg_wind map_state 0
execute if score bg_wind map_state matches 0 as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~15 ~33 ~19 as @a[dx=63,dy=2,dz=2] at @s run tp @s ~ ~ ~0.18
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run particle minecraft:smoke ~20 ~34 ~20 0 0 0 0 1 normal
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run particle minecraft:smoke ~40 ~34 ~20 0 0 0 0 1 normal
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run particle minecraft:smoke ~55 ~34 ~20 0 0 0 0 1 normal
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~4 ~32 ~14 as @a[dx=10,dy=3,dz=14,tag=!cp_west] run tellraw @s {"text":"The span is one block wide. A fall sends you back to the ground."}
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~4 ~32 ~14 run tag @a[dx=10,dy=3,dz=14] add cp_west
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~78 ~32 ~14 as @a[dx=12,dy=3,dz=14,tag=!cp_east] run spawnpoint @s ~84 ~33 ~20
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~78 ~32 ~14 run tag @a[dx=12,dy=3,dz=14] add cp_east
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~124 ~0 ~44 as @a[dx=10,dy=3,dz=8,tag=!cp_quad] run spawnpoint @s ~128 ~0 ~48
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~124 ~0 ~44 run tag @a[dx=10,dy=3,dz=8] add cp_quad
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~38 ~-2 ~112 as @a[dx=12,dy=4,dz=12,tag=!cp_valley] run spawnpoint @s ~43 ~-1 ~117
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~38 ~-2 ~112 run tag @a[dx=12,dy=4,dz=12] add cp_valley
scoreboard players add bg_storm map_state 1
execute if score bg_storm map_state matches 200.. run scoreboard players set bg_storm map_state 0
execute if score bg_storm map_state matches 0 as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] run weather thunder 999999
scoreboard players add @a[tag=timed_run] run_tick 1
execute as @a[tag=timed_run] run scoreboard players operation @s run_sec = @s run_tick
scoreboard players operation @a[tag=timed_run] run_sec /= bg_twenty map_state
execute as @a[tag=timed_run] run title @s actionbar [{"text":"§bCourse  "},{"score":{"name":"@s","objective":"run_sec"}},{"text":"s"}]
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run scoreboard players add bg_clock map_state 1
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~146 ~1 ~80 as @a[dx=23,dy=1,dz=2,tag=!gate_run] run tag @s add gate_run
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~146 ~1 ~80 as @a[dx=23,dy=1,dz=2,tag=!gate_run] run tag @s remove gate_done
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~146 ~1 ~80 as @a[dx=23,dy=1,dz=2] run scoreboard players operation @s gate_start = bg_clock map_state
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~146 ~1 ~80 as @a[dx=23,dy=1,dz=2] run scoreboard players set @s gate_pen 0
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=gate_run] run scoreboard players operation @s gate_time = bg_clock map_state
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=gate_run] run scoreboard players operation @s gate_time -= @s gate_start
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=gate_run] run scoreboard players operation @s gate_time += @s gate_pen
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=gate_run] run scoreboard players operation @s gate_sec = @s gate_time
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=gate_run] run scoreboard players operation @s gate_sec /= bg_twenty map_state
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] run tag @s remove gate_run
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] run tag @s add gate_done
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] unless score @s gate_best matches 0.. run scoreboard players set @s gate_best 0
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] if score @s gate_best matches 0 run scoreboard players operation @s gate_best = @s gate_time
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] if score @s gate_best matches 1.. run scoreboard players operation @s gate_best < @s gate_time
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~146 ~26 ~105 as @a[dx=23,dy=1,dz=36,tag=gate_run] run title @s title [{"text":"Gauntlet complete. Your time: "},{"score":{"name":"@s","objective":"gate_sec"}},{"text":" seconds."}]
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~148 ~3 ~81 as @a[dx=1,dy=2,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~148 ~3 ~81 run tag @a[dx=1,dy=2,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~154 ~3 ~81 as @a[dx=1,dy=2,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~154 ~3 ~81 run tag @a[dx=1,dy=2,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~160 ~3 ~81 as @a[dx=1,dy=2,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~160 ~3 ~81 run tag @a[dx=1,dy=2,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~148 ~4 ~84 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~148 ~4 ~84 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~154 ~4 ~84 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~154 ~4 ~84 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~160 ~4 ~84 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~160 ~4 ~84 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~148 ~8 ~88 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~148 ~8 ~88 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~154 ~8 ~88 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~154 ~8 ~88 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~160 ~8 ~88 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~160 ~8 ~88 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~148 ~12 ~92 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~148 ~12 ~92 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~154 ~12 ~92 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~154 ~12 ~92 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~160 ~12 ~92 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~160 ~12 ~92 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~148 ~16 ~96 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~148 ~16 ~96 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~154 ~16 ~96 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~154 ~16 ~96 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~160 ~16 ~96 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~160 ~16 ~96 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~148 ~20 ~100 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~148 ~20 ~100 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~154 ~20 ~100 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~154 ~20 ~100 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~160 ~20 ~100 as @a[dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add @s gate_pen 600
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~160 ~20 ~100 run tag @a[dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run tag @a[tag=rope_touch] add rope_cool
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run tag @a[tag=!rope_touch] remove rope_cool
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run tag @a[tag=!rope_touch] remove rope_told
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=rope_touch,tag=!rope_told] run title @s actionbar {"text":"You grabbed a rope. The run adds 30 seconds."}
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run tag @a[tag=rope_touch] add rope_told
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run scoreboard players add bg_spinline map_state 1
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s if score bg_spinline map_state matches 10.. run scoreboard players set bg_spinline map_state 0
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run particle minecraft:smoke ~152 ~3 ~83 0 0 0 0 1 normal
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s if score bg_spinline map_state matches 5 run particle minecraft:smoke ~152 ~3 ~82 0 0 0 0 1 normal
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~15 ~33 ~12 as @a[dx=62,dy=8,dz=16] run tag @s add crossed
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~38 ~-2 ~112 as @a[dx=12,dy=4,dz=12,tag=crossed,tag=!bonded] run tag @s add bonded
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=bonded,tag=!bondcall] at @s run summon basgiath:dragon ~1 ~ ~
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=bonded,tag=!bondcall] run scoreboard players set bg_bond map_state 1
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=bonded,tag=!bondcall] run tellraw @s {"text":"A dragon has chosen you. You did not choose it. Stand still and let it look."}
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=bonded,tag=!bondcall] run tag @s add bondcall
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=bondcall,tag=!relic] run tellraw @s {"text":"A relic mark burns onto your arm, shaped like the one that chose you."}
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=bondcall,tag=!relic] run tag @s add relic
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=relic,tag=!trial] run tellraw @s {"text":"Hold your seat. The dragon will fly and turn. Do not let go."}
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s as @a[tag=relic,tag=!trial] run tag @s add trial
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~42 ~-2 ~116 as @a[dx=2,dy=3,dz=2,tag=trial,tag=!flew] run tellraw @s {"text":"You held. Walk south to the roll-keeper and give the full name."}
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~42 ~-2 ~116 as @a[dx=2,dy=3,dz=2,tag=trial,tag=!flew] run tag @s add flew
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~48 ~-2 ~122 as @a[dx=4,dy=3,dz=4,tag=flew,tag=!named] run tellraw @s {"text":"Give the keeper the full name, nothing held back. Only you and the keeper will know it."}
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s positioned ~48 ~-2 ~122 as @a[dx=4,dy=3,dz=4,tag=flew,tag=!named] run tag @s add named
