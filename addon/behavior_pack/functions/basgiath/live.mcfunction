scoreboard players add #wind map_state 1
execute if score #wind map_state matches 4.. run scoreboard players set #wind map_state 0
execute if score #wind map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] at @s positioned ~15 ~33 ~19 as @a[dx=63,dy=2,dz=2] at @s run tp @s ~ ~ ~0.18
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
scoreboard players add #storm map_state 1
execute if score #storm map_state matches 200.. run scoreboard players set #storm map_state 0
execute if score #storm map_state matches 0 as @e[type=armor_stand,name="build_anchor",c=1] run weather thunder 999999
