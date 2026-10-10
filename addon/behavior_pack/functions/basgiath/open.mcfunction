scoreboard players set bg_pass map_state 2
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_01
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_02
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_03
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_04
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_05
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_06
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_07
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_08
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_09
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_10
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_11
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_12
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_13
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_14
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_15
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_16
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_17
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_18
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_19
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_20
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_21
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_22
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_23
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_24
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_25
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_26
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run function basgiath/far_27
execute if score bg_done map_state matches 0 run gamemode adventure @a
execute if score bg_done map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s run titleraw @p title {"rawtext":[{"text":"Welcome, candidate"}]}
execute if score bg_done map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s run titleraw @p subtitle {"rawtext":[{"text":"Cross the Parapet"}]}
execute if score bg_done map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s run tellraw @a {"rawtext":[{"text":"Fan-made. Not official. Not affiliated with any publisher. The glowing stairs are in front of you. A fall from the span sends you back here. Cross the Parapet. The signet stone waits in the dell, after a dragon chooses you."}]}
execute if score bg_done map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s run tp @p ~8 ~0 ~66 180 0
scoreboard players set bg_done map_state 1
