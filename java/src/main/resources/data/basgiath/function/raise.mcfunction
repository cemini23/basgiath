effect give @p minecraft:slow_falling 8 0 true
effect give @p minecraft:resistance 8 5 true
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run tp @p ~120 ~8 ~40
schedule function basgiath:open 80t
