execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tp @p ~120 ~0 ~40 -90 0
execute as @e[type=armor_stand,name="build_anchor",c=1] run tellraw @p {"rawtext":[{"text":"You are in the courtyard."}]}
execute unless entity @e[type=armor_stand,name="build_anchor"] run tellraw @s {"rawtext":[{"text":"Raise the college first. Run /function basgiath/build"}]}
