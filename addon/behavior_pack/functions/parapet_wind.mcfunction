# Push players who stand on the span. The path runs along +X. Wind pushes toward +Z.
# Replace the box and the push distance after you build the span. See README.md.
execute as @a[x=0,y=80,z=-1,dx=60,dy=3,dz=3] at @s run tp @s ~ ~ ~0.15
execute as @a[x=0,y=80,z=-1,dx=60,dy=3,dz=3] at @s run particle minecraft:basic_smoke_particle ~ ~1 ~0.4
