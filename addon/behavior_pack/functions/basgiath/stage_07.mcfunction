fill ~90 ~-1 ~18 ~96 ~-1 ~22 stone_bricks
fill ~108 ~-1 ~79 ~112 ~-1 ~89 stone_bricks
fill ~71 ~-1 ~116 ~98 ~-1 ~120 stone_bricks
setblock ~45 ~8 ~20 air
setblock ~46 ~8 ~20 air
setblock ~8 ~9 ~18 stone_pressure_plate
setblock ~84 ~9 ~18 stone_pressure_plate
setblock ~128 ~ ~46 stone_pressure_plate
setblock ~43 ~-5 ~115 stone_pressure_plate
time set night
weather thunder 999999
gamerule dodaylightcycle false
gamerule doweathercycle false
gamerule domobspawning false
gamerule keepinventory true
gamerule sendcommandfeedback false
gamerule commandblockoutput false
gamemode adventure @a
titleraw @p title {"rawtext":[{"text":"Welcome, candidate"}]}
titleraw @p subtitle {"rawtext":[{"text":"Cross the Parapet"}]}
tellraw @a {"rawtext":[{"text":"Fan-made. Not official. Not affiliated with any publisher. Touch the stone in the Quad. Then run /function basgiath/summon_dragon"}]}
tp @p ~8 ~9 ~20
