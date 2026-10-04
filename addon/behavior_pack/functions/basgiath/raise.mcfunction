effect @p slow_falling 8 0 true
effect @p resistance 8 5 true
execute as @e[type=armor_stand,name="build_anchor",c=1] at @s run tp @p ~120 ~8 ~40
schedule delay add basgiath/open 80
