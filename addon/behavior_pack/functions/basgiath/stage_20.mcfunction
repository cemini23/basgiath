gamerule keepinventory true
gamerule sendcommandfeedback false
gamerule commandblockoutput false
gamerule doimmediaterespawn true
gamemode adventure @a
titleraw @p title {"rawtext":[{"text":"Welcome, candidate"}]}
titleraw @p subtitle {"rawtext":[{"text":"Cross the Parapet"}]}
tellraw @a {"rawtext":[{"text":"Fan-made. Not official. Not affiliated with any publisher. The glowing stairs are in front of you. A fall from the span sends you back here. Touch the stone in the Quad. Then run /function basgiath/summon_dragon"}]}
spawnpoint @p ~8 ~0 ~66
tp @p ~8 ~0 ~66 180 0
