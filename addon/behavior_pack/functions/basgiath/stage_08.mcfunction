setblock ~69 ~-2 ~118 air
setblock ~69 ~-1 ~118 air
setblock ~68 ~-4 ~117 stone_bricks
setblock ~68 ~-3 ~117 air
setblock ~68 ~-2 ~117 air
setblock ~68 ~-4 ~118 stone_bricks
setblock ~68 ~-3 ~118 air
setblock ~68 ~-2 ~118 air
setblock ~67 ~-5 ~117 stone_bricks
setblock ~67 ~-4 ~117 air
setblock ~67 ~-3 ~117 air
setblock ~67 ~-5 ~118 stone_bricks
setblock ~67 ~-4 ~118 air
setblock ~67 ~-3 ~118 air
setblock ~66 ~-6 ~117 stone_bricks
setblock ~66 ~-5 ~117 air
setblock ~66 ~-4 ~117 air
setblock ~66 ~-6 ~118 stone_bricks
setblock ~66 ~-5 ~118 air
setblock ~66 ~-4 ~118 air
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
gamerule doimmediaterespawn true
gamemode adventure @a
titleraw @p title {"rawtext":[{"text":"Welcome, candidate"}]}
titleraw @p subtitle {"rawtext":[{"text":"Cross the Parapet"}]}
tellraw @a {"rawtext":[{"text":"Fan-made. Not official. Not affiliated with any publisher. Climb the lit stairs. A fall from the span sends you back here. Touch the stone in the Quad. Then run /function basgiath/summon_dragon"}]}
spawnpoint @p ~8 ~0 ~36
tp @p ~8 ~0 ~36
