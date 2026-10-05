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
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a remove rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~148,y=~3,z=~81,dx=1,dy=2,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~148,y=~3,z=~81,dx=1,dy=2,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~154,y=~3,z=~81,dx=1,dy=2,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~154,y=~3,z=~81,dx=1,dy=2,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~160,y=~3,z=~81,dx=1,dy=2,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~160,y=~3,z=~81,dx=1,dy=2,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~148,y=~4,z=~84,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~148,y=~4,z=~84,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~154,y=~4,z=~84,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~154,y=~4,z=~84,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~160,y=~4,z=~84,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~160,y=~4,z=~84,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~148,y=~8,z=~88,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~148,y=~8,z=~88,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~154,y=~8,z=~88,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~154,y=~8,z=~88,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~160,y=~8,z=~88,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~160,y=~8,z=~88,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~148,y=~12,z=~92,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~148,y=~12,z=~92,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~154,y=~12,z=~92,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~154,y=~12,z=~92,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~160,y=~12,z=~92,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~160,y=~12,z=~92,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~148,y=~16,z=~96,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~148,y=~16,z=~96,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~154,y=~16,z=~96,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~154,y=~16,z=~96,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~160,y=~16,z=~96,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~160,y=~16,z=~96,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~148,y=~20,z=~100,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~148,y=~20,z=~100,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~154,y=~20,z=~100,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~154,y=~20,z=~100,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~160,y=~20,z=~100,dx=1,dy=5,dz=1,tag=!rope_cool] run scoreboard players add #gauntlet map_state 30
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[x=~160,y=~20,z=~100,dx=1,dy=5,dz=1] add rope_touch
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[tag=rope_touch] add rope_cool
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[tag=!rope_touch] remove rope_cool
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[tag=!rope_touch] remove rope_told
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[tag=rope_touch,tag=!rope_told] run titleraw @s actionbar {"rawtext":[{"text":"You grabbed a rope. The run adds 30 seconds."}]}
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tag @a[tag=rope_touch] add rope_told
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run scoreboard players add #spinline map_state 1
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s if score #spinline map_state matches 10.. run scoreboard players set #spinline map_state 0
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run particle minecraft:basic_smoke_particle ~152 ~3 ~83
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s if score #spinline map_state matches 5 run particle minecraft:basic_smoke_particle ~152 ~3 ~82
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~15,y=~33,z=~12,dx=62,dy=8,dz=16] run tag @s add crossed
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~38,y=~-2,z=~112,dx=12,dy=4,dz=12,tag=crossed,tag=!bonded] run tag @s add bonded
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[tag=bonded,tag=!bondcall] at @s run summon dragon_rider:dragon ~1 ~ ~
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[tag=bonded,tag=!bondcall] run scoreboard players set #bond map_state 1
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[tag=bonded,tag=!bondcall] run tellraw @s {"rawtext":[{"text":"A dragon has chosen you. You did not choose it. Stand still and let it look."}]}
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[tag=bonded,tag=!bondcall] run tag @s add bondcall
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[tag=bondcall,tag=!relic] run tellraw @s {"rawtext":[{"text":"A relic mark burns onto your arm, shaped like the one that chose you."}]}
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[tag=bondcall,tag=!relic] run tag @s add relic
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[tag=relic,tag=!trial] run tellraw @s {"rawtext":[{"text":"Hold your seat. The dragon will fly and turn. Do not let go."}]}
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[tag=relic,tag=!trial] run tag @s add trial
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~42,y=~-2,z=~116,dx=2,dy=3,dz=2,tag=trial,tag=!flew] run tellraw @s {"rawtext":[{"text":"You held. Walk south to the roll-keeper and give the full name."}]}
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~42,y=~-2,z=~116,dx=2,dy=3,dz=2,tag=trial,tag=!flew] run tag @s add flew
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~48,y=~-2,z=~122,dx=4,dy=3,dz=4,tag=flew,tag=!named] run tellraw @s {"rawtext":[{"text":"Give the keeper the full name, nothing held back. Only you and the keeper will know it."}]}
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s as @a[x=~48,y=~-2,z=~122,dx=4,dy=3,dz=4,tag=flew,tag=!named] run tag @s add named
