execute unless entity @e[type=basgiath:dragon] as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] at @s run summon basgiath:dragon ~43 ~-1 ~117
execute as @e[type=minecraft:armor_stand,name="build_anchor",limit=1] run tellraw @a {"text":"A dragon waits on the moss pad. Mount it and fly."}
execute unless entity @e[type=minecraft:armor_stand,name="build_anchor"] run tellraw @s {"text":"Raise the college first. Run /function basgiath/build"}
