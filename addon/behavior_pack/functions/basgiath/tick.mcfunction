scoreboard players operation #now map_state = #stage map_state
execute if score #now map_state matches 1 as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_01
execute if score #now map_state matches 1 run scoreboard players set #stage map_state 2
execute if score #now map_state matches 2 as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_02
execute if score #now map_state matches 2 run scoreboard players set #stage map_state 3
execute if score #now map_state matches 3 as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_03
execute if score #now map_state matches 3 run scoreboard players set #stage map_state 4
execute if score #now map_state matches 4 as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_04
execute if score #now map_state matches 4 run scoreboard players set #stage map_state 5
execute if score #now map_state matches 5 as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_05
execute if score #now map_state matches 5 run scoreboard players set #stage map_state 6
execute if score #now map_state matches 6 as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_06
execute if score #now map_state matches 6 run scoreboard players set #stage map_state 7
execute if score #now map_state matches 7 as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/stage_07
execute if score #now map_state matches 7 run scoreboard players set #stage map_state 0
execute if score #now map_state matches 0 run function basgiath/live
