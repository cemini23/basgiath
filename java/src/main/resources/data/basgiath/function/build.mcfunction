title @s times 0 80 10
title @s title {"text":"Building"}
title @s subtitle {"text":"Stay still"}
scoreboard objectives add map_state dummy
scoreboard objectives add gate_time dummy
scoreboard objectives add gate_sec dummy
scoreboard objectives add gate_start dummy
scoreboard objectives add gate_pen dummy
scoreboard objectives add gate_best dummy
scoreboard objectives add run_tick dummy
scoreboard objectives add run_sec dummy
scoreboard players set bg_twenty map_state 20
scoreboard objectives setdisplay sidebar gate_sec
kill @e[type=minecraft:armor_stand,name="build_anchor"]
execute at @s run setblock ~ ~-1 ~ stone
execute at @s run setblock ~ ~-1 ~-1 sea_lantern
execute at @s run setblock ~1 ~-1 ~-1 sea_lantern
execute at @s run setblock ~-1 ~-1 ~-1 sea_lantern
execute at @s run summon minecraft:armor_stand ~ ~ ~ {CustomName:'{"text":"build_anchor"}'}
execute at @s run effect give @e[type=minecraft:armor_stand,name="build_anchor",limit=1] minecraft:invisibility 999999 1 true
execute at @s run effect give @e[type=minecraft:armor_stand,name="build_anchor",limit=1] minecraft:resistance 999999 255 true
gamerule sendCommandFeedback false
gamemode adventure @a
scoreboard players set bg_done map_state 0
scoreboard players set bg_pass map_state 1
schedule function basgiath:raise 300t
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_01
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_02
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_03
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_04
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_05
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_06
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_07
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_08
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_09
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_10
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_11
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_12
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_13
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_14
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_15
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_16
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_17
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_18
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_19
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_20
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_21
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_22
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_23
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_24
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_25
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_26
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_27
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_28
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_29
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_30
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_31
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_32
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_33
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run function basgiath:stage_34
scoreboard players set bg_stage map_state 0
tellraw @s {"text":"The college is rising. Stay still for 15 seconds. Fan-made. Not official. Not affiliated with any publisher."}
