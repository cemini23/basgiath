execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run tp @p ~120 ~0 ~40 -90 0
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] run tellraw @p {"text":"You are in the courtyard."}
execute unless entity @e[type=minecraft:armor_stand,name="build_anchor"] run tellraw @s {"text":"Raise the college first. Run /function basgiath/build"}
