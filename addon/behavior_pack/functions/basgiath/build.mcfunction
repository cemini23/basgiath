scoreboard objectives add map_state dummy
kill @e[type=armor_stand,name="build_anchor"]
execute as @s if entity @s[y=-64,dy=44] run tp @s ~ 80 ~
execute at @s run setblock ~ ~-1 ~ stone
execute at @s run summon armor_stand "build_anchor" ~ ~ ~
execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] invisibility 999999 1 true
execute at @s run effect @e[type=armor_stand,name="build_anchor",c=1] resistance 999999 255 true
scoreboard players set #stage map_state 1
tellraw @s {"rawtext":[{"text":"The college is rising. Stay still. Fan-made. Not official. Not affiliated with any publisher."}]}
