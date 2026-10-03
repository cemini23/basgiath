execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run summon dragon_rider:dragon ~43 ~-5 ~117
execute as @e[type=armor_stand,name="build_anchor",c=1] run tellraw @a {"rawtext":[{"text":"A dragon waits on the gold pad. Mount it and fly."}]}
execute unless entity @e[type=armor_stand,name="build_anchor"] run tellraw @s {"rawtext":[{"text":"Raise the college first. Run /function basgiath/build"}]}
