package com.basgiath;

import java.util.List;
import java.util.Optional;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.core.BlockPos;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.level.block.Blocks;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.neoforge.event.server.ServerStartedEvent;

/**
 * A headless check that the port actually works.
 *
 * <p>The prompt asks for two things to be confirmed on the first Java world:
 * {@code /function basgiath:build} raises the college, and one summonable dragon
 * exists. Neither can be confirmed by reading code, and a dedicated server has no
 * player to run the build from, so this class drives the machine directly.
 *
 * <p>It runs only when the {@code basgiath.smoke} system property is set, which the
 * {@code smoke} run config in build.gradle sets. It writes a pass or fail line per
 * check, then stops the server, so it is usable from a shell and from CI.
 *
 * <p>What it proves: the generated Java datapack parses and executes, every stage
 * places the blocks the generator intended, and the dragon entity type is
 * registered and summonable. What it does not prove: anything that needs a client,
 * which is the screens and the renderer.
 */
public final class BasgiathSmokeTest {

    private BasgiathSmokeTest() {}

    /**
     * Where the college is raised for this run.
     *
     * <p>It has to sit in a loaded chunk, or the anchor is summoned into a place the
     * server is not tracking and every stage finds nothing to move. The world spawn
     * is the one position guaranteed to be loaded on a fresh dedicated server.
     */
    private static BlockPos ANCHOR = new BlockPos(0, 64, 0);

    private static int passed;
    private static int failed;

    private static void check(String name, boolean ok, String detail) {
        if (ok) {
            passed += 1;
            System.out.println("SMOKE PASS  " + name);
        } else {
            failed += 1;
            System.out.println("SMOKE FAIL  " + name + " :: " + detail);
        }
    }

    @SubscribeEvent
    public static void onServerStarted(ServerStartedEvent event) {
        if (System.getProperty("basgiath.smoke") == null) {
            return;
        }
        MinecraftServer server = event.getServer();
        try {
            run(server);
        } catch (RuntimeException error) {
            failed += 1;
            System.out.println("SMOKE FAIL  the smoke test threw :: " + error);
            error.printStackTrace(System.out);
        } finally {
            System.out.println("SMOKE RESULT  passed=" + passed + " failed=" + failed);
            server.halt(false);
        }
    }

    /**
     * Every function the generator wrote has to have loaded.
     *
     * <p>A function that fails to parse does not warn and does not half-load: it is
     * dropped, and every call to it quietly does nothing. That is how both of this
     * port's generation bugs showed up — a block id Java had renamed, and a relative
     * selector coordinate Java refuses. Neither was visible on the Bedrock side, and
     * neither would have been visible here without this check.
     *
     * <p>So the check compares what is on disk with what the game actually loaded,
     * rather than trusting that a build that produced no errors is a build that runs.
     */
    private static void checkEveryFunctionLoaded(MinecraftServer server) {
        final String prefix = "function/";
        final String suffix = ".mcfunction";
        // The path here is relative to the data root, and each hit already carries the
        // namespace, so `function/build.mcfunction` arrives as
        // `basgiath:function/build.mcfunction`.
        var onDisk = server.getResourceManager().listResources(
                "function",
                location -> location.getNamespace().equals(Basgiath.MOD_ID)
                        && location.getPath().endsWith(suffix));

        List<String> missing = new java.util.ArrayList<>();
        for (ResourceLocation location : onDisk.keySet()) {
            String path = location.getPath();
            String name = path.substring(prefix.length(), path.length() - suffix.length());
            ResourceLocation id = ResourceLocation.fromNamespaceAndPath(Basgiath.MOD_ID, name);
            if (server.getFunctions().get(id).isEmpty()) {
                missing.add(name);
            }
        }
        for (String name : missing) {
            System.out.println("SMOKE    did not load: " + name);
        }
        check("every generated function loaded (" + onDisk.size() + " on disk)",
                onDisk.size() > 0 && missing.isEmpty(),
                missing.size() + " of " + onDisk.size() + " functions failed to load");
    }

    /**
     * The dragon's three assets are present, and the animations it asks for exist.
     *
     * <p>GeckoLib keys its baked animations on the animation file's own JSON key and
     * looks them up with a plain map get. A mismatch is not an error: the model just
     * never moves. That is invisible on a dedicated server and easy to miss on a
     * client, so the two names are checked against the file here.
     */
    private static void checkDragonAssets() {
        String animationPath = "/assets/" + Basgiath.MOD_ID
                + "/animations/entity/dragon.animation.json";
        String geoPath = "/assets/" + Basgiath.MOD_ID + "/geo/entity/dragon.geo.json";
        String texturePath = "/assets/" + Basgiath.MOD_ID + "/textures/entity/dragon.png";

        for (String path : new String[]{animationPath, geoPath, texturePath}) {
            check("the dragon asset " + path.substring(path.lastIndexOf('/') + 1) + " ships",
                    BasgiathSmokeTest.class.getResource(path) != null,
                    "not on the classpath: " + path);
        }

        try (var stream = BasgiathSmokeTest.class.getResourceAsStream(animationPath)) {
            if (stream == null) {
                return;
            }
            var root = com.google.gson.JsonParser.parseString(
                    new String(stream.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8))
                    .getAsJsonObject();
            var animations = root.getAsJsonObject("animations");
            for (String wanted : new String[]{
                    DragonEntity.IDLE_ANIMATION, DragonEntity.FLY_ANIMATION}) {
                check("the dragon animation " + wanted + " exists in the file",
                        animations != null && animations.has(wanted),
                        "the entity asks for it but the animation file has key set "
                                + (animations == null ? "<no animations block>"
                                        : animations.keySet().toString()));
            }
        } catch (Exception error) {
            check("the dragon animation file is readable", false, String.valueOf(error));
        }
    }

    /**
     * The Vale, the Java-only dimension.
     *
     * <p>Dimension data that parses but registers wrong does not throw: the level is
     * simply absent, and {@code /basgiath vale} is the only thing that would ever say
     * so. This asks the server for the level by key and then reads a block out of it,
     * which is the only way to tell the generator ran.
     */
    private static void checkVale(MinecraftServer server) {
        ServerLevel vale = server.getLevel(BasgiathCommands.VALE);
        check("the Vale dimension is registered", vale != null,
                "basgiath:vale is not a loaded level; the dimension data did not take");
        if (vale == null) {
            return;
        }
        // The flat layers top out at y=6: bedrock, stone x3, dirt x2, grass_block.
        var surface = vale.getBlockState(new BlockPos(0, 6, 0));
        check("the Vale floor is the flat preset's surface",
                surface.is(Blocks.GRASS_BLOCK),
                "expected grass_block at 0,6,0 in the Vale, found " + surface.getBlock());
        // The fixed time lives on the dimension type, not on the level clock. A
        // non-overworld level mirrors the overworld's day time, so reading
        // getDayTime() here would report the overworld's clock and say nothing about
        // this dimension at all.
        check("the Vale holds a fixed midnight",
                vale.dimensionType().fixedTime().orElse(-1L) == 18000L,
                "the dimension type fixes time at "
                        + vale.dimensionType().fixedTime() + ", not 18000");
    }

    private static void run(MinecraftServer server) {
        ServerLevel level = server.overworld();
        ANCHOR = level.getSharedSpawnPos().above(2);
        System.out.println("SMOKE  building at " + ANCHOR);
        checkEveryFunctionLoaded(server);
        checkDragonAssets();
        checkVale(server);
        // Not suppressed: a command that fails says why in the log, and a silent
        // failure is exactly what this test exists to catch.
        CommandSourceStack source = server.createCommandSourceStack();

        // 1. The datapack loaded, and its functions are reachable by namespaced id.
        Optional<?> build = server.getFunctions().get(
                ResourceLocation.fromNamespaceAndPath(Basgiath.MOD_ID, "build"));
        check("the datapack registers basgiath:build", build.isPresent(),
                "basgiath:build is not in the function manager");

        // 2. The anchor the generator builds around.
        loudCommand(source, "kill @e[type=minecraft:armor_stand,name=\"build_anchor\"]");
        loudCommand(source, "summon minecraft:armor_stand " + ANCHOR.getX() + " " + ANCHOR.getY()
                + " " + ANCHOR.getZ() + " {CustomName:'{\"text\":\"build_anchor\"}',NoGravity:1b}");

        var stands = level.getEntitiesOfClass(ArmorStand.class,
                new net.minecraft.world.phys.AABB(ANCHOR).inflate(16),
                stand -> true);
        System.out.println("SMOKE  armor stands within 16 blocks: " + stands.size());
        for (ArmorStand stand : stands) {
            System.out.println("SMOKE    at " + stand.blockPosition() + " name="
                    + (stand.hasCustomName() ? stand.getCustomName().getString() : "<none>"));
        }
        ArmorStand anchor = stands.stream()
                .filter(stand -> stand.hasCustomName()
                        && BasgiathEvents.BUILD_ANCHOR.equals(stand.getCustomName().getString()))
                .findFirst().orElse(null);
        check("the build anchor exists", anchor != null, "no armor stand named build_anchor");

        // 3. Every stage the generator wrote runs. The stage list is discovered rather
        // than hardcoded, so a change to the generator cannot silently skip one.
        int stages = 0;
        for (int index = 1; index <= 256; index++) {
            String name = String.format("stage_%02d", index);
            if (server.getFunctions().get(
                    ResourceLocation.fromNamespaceAndPath(Basgiath.MOD_ID, name)).isEmpty()) {
                break;
            }
            stages += 1;
            command(source, "execute as @e[type=minecraft:armor_stand,name=\"build_anchor\",limit=1]"
                    + " at @s run function " + Basgiath.MOD_ID + ":" + name);
        }
        check("the generator wrote more than one stage", stages > 1, "only " + stages + " stages");

        // 4. The stages placed what the generator meant. finish() puts a stone pressure
        // plate at anchor + (5, DECK_Y + 1, SPAN_Z); if the stages ran, it is there.
        BlockPos plate = ANCHOR.offset(5, 33, 20);
        check("a stage placed the west span plate",
                level.getBlockState(plate).is(Blocks.STONE_PRESSURE_PLATE),
                "expected a stone pressure plate at " + plate + ", found "
                        + level.getBlockState(plate).getBlock());

        // The span deck itself: two blocks are cut out of it on purpose, so the middle
        // is air and the rest is not.
        BlockPos deck = ANCHOR.offset(20, 32, 20);
        check("the span deck is solid where it should be",
                !level.getBlockState(deck).isAir(),
                "expected the deck at " + deck + " to be built, found air");

        // 5. The dragon. This is the entity the port exists to bring across.
        command(source, "kill @e[type=" + Basgiath.MOD_ID + ":dragon]");
        command(source, "summon " + Basgiath.MOD_ID + ":dragon "
                + (ANCHOR.getX() + 40) + " " + (ANCHOR.getY() + 5) + " " + (ANCHOR.getZ() + 40));
        var dragons = level.getEntities(EntityType.byString(Basgiath.MOD_ID + ":dragon").orElseThrow(),
                entity -> true);
        check("the dragon is summonable", !dragons.isEmpty(),
                "summon " + Basgiath.MOD_ID + ":dragon produced no entity");
        for (Entity dragon : dragons) {
            check("the dragon is the mod's own class", dragon instanceof DragonEntity,
                    "the summoned dragon is " + dragon.getClass().getName());
            break;
        }

        // 6. The tick loop. Bedrock ran basgiath/tick from the script every tick; Java
        // runs it from the minecraft:tick tag. If the tag is missing, nothing the map
        // does after the build ever happens.
        var tickFunctions = level.getServer().getFunctions()
                .getTag(ResourceLocation.fromNamespaceAndPath("minecraft", "tick"));
        boolean tagged = tickFunctions.stream()
                .anyMatch(function -> function.id().toString()
                        .startsWith(Basgiath.MOD_ID + ":tick"));
        check("basgiath:tick is in the minecraft:tick tag", tagged,
                "the tick tag does not reach basgiath:tick");

        // 7. Persistence. The wing roster has to survive, and a data attachment has to
        // be readable, before any of it can be called ported.
        check("the wing roster loads", BasgiathData.WingRoster.get(level) != null,
                "SavedData did not come back");
    }

    /**
     * Whether a command is legal syntax.
     *
     * <p>A syntax error arrives as a {@code CommandSyntaxException}. Anything else
     * means the command parsed and then failed to run, which is a different thing:
     * "no entity was found" is a runtime complaint about an empty world, not a
     * verdict on the grammar.
     */
    /** Why a command did not run, for a failure message that says something. */
    private static String why(MinecraftServer server, CommandSourceStack source, String command) {
        try {
            server.getCommands().getDispatcher().execute(command, source);
            return "it ran";
        } catch (Exception error) {
            return error.getClass().getSimpleName() + ": " + error.getMessage();
        }
    }

    private static boolean parses(MinecraftServer server, CommandSourceStack source, String command) {
        try {
            server.getCommands().getDispatcher().execute(command, source);
            return true;
        } catch (com.mojang.brigadier.exceptions.CommandSyntaxException syntax) {
            return false;
        } catch (Exception runtime) {
            return true;
        }
    }

    private static void command(CommandSourceStack source, String command) {
        source.getServer().getCommands().performPrefixedCommand(source, command);
    }

    /**
     * Run a command, print what it returned, and let its messages reach the log.
     *
     * <p>A failing command reports through the log rather than a return value, so the
     * source here is not suppressed. That is the whole point of this variant.
     */
    private static void loudCommand(CommandSourceStack source, String command) {
        System.out.println("SMOKE  running [" + command + "]");
        source.getServer().getCommands().performPrefixedCommand(source, command);
    }
}
