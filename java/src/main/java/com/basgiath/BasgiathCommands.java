package com.basgiath;

import com.mojang.brigadier.builder.LiteralArgumentBuilder;

import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.RegisterCommandsEvent;

/**
 * The test bypasses, as commands.
 *
 * <p>The Bedrock script reached its forms through {@code /scriptevent}. Java has no
 * scriptevent, so each bypass becomes a subcommand. They open the same flows the
 * block interactions open, without the gate in front of them, so a flow stays
 * reachable without walking the map to it.
 *
 * <p>They need permission level 2, because they are development tools and not part
 * of the map.
 *
 * <p>{@code RegisterCommandsEvent} is a game-bus event, so this class is registered
 * on {@code NeoForge.EVENT_BUS} by name from {@link Basgiath}.
 */
public final class BasgiathCommands {

    private BasgiathCommands() {}

    /**
     * The Vale: the college's own dimension.
     *
     * <p>This is Java-only scope. Bedrock custom dimensions are experimental and
     * void-only, so the Bedrock map is built in the overworld and this dimension
     * exists on Java alone. It is flat, because the map is raised by
     * {@code basgiath:build} wherever the player stands rather than shipped as built
     * blocks, and it holds a fixed midnight so the crossing is always in the dark.
     */
    public static final net.minecraft.resources.ResourceKey<net.minecraft.world.level.Level> VALE =
            net.minecraft.resources.ResourceKey.create(
                    net.minecraft.core.registries.Registries.DIMENSION,
                    net.minecraft.resources.ResourceLocation.fromNamespaceAndPath(
                            Basgiath.MOD_ID, "vale"));

    /** Where a player lands when they step into the Vale. The flat floor tops out at y=6. */
    private static final net.minecraft.core.BlockPos VALE_ARRIVAL =
            new net.minecraft.core.BlockPos(0, 7, 0);

    @SubscribeEvent
    public static void onRegisterCommands(RegisterCommandsEvent event) {
        event.getDispatcher().register(Commands.literal("basgiath")
                .then(bypass("signet", player -> BasgiathForms.SignetFlow.start(player)))
                .then(bypass("vault", player -> BasgiathForms.VaultFlow.start(player)))
                .then(bypass("rider_name",
                        player -> BasgiathForms.KeeperFlow.start(player, Keepers.SCROLL_KEEPER)))
                .then(bypass("dragon_name",
                        player -> BasgiathForms.KeeperFlow.start(player, Keepers.ROLL_KEEPER)))
                .then(Commands.literal("vale").requires(source -> source.hasPermission(2))
                        .executes(context -> {
                            ServerPlayer player = context.getSource().getPlayerOrException();
                            net.minecraft.server.level.ServerLevel vale =
                                    player.server.getLevel(VALE);
                            if (vale == null) {
                                context.getSource().sendFailure(Component.literal(
                                        "The Vale is not loaded. Check that basgiath:vale "
                                                + "dimension data shipped."));
                                return 0;
                            }
                            player.teleportTo(vale, VALE_ARRIVAL.getX() + 0.5,
                                    VALE_ARRIVAL.getY(), VALE_ARRIVAL.getZ() + 0.5,
                                    player.getYRot(), player.getXRot());
                            return 1;
                        }))
                .then(Commands.literal("origin").requires(source -> source.hasPermission(2))
                        .executes(context -> {
                            CommandSourceStack source = context.getSource();
                            var pos = BasgiathEvents.buildOrigin(source.getLevel(),
                                    net.minecraft.core.BlockPos.containing(source.getPosition()));
                            source.sendSuccess(() -> Component.literal(pos == null
                                    ? "No build anchor here. Run /function basgiath:build first."
                                    : "Build anchor at " + pos.getX() + " " + pos.getY() + " "
                                            + pos.getZ()), false);
                            return 1;
                        })));
    }

    /** One bypass: a name, and what it opens for the player who ran it. */
    private static LiteralArgumentBuilder<CommandSourceStack> bypass(
            String name, java.util.function.Consumer<ServerPlayer> action) {
        return Commands.literal(name).requires(source -> source.hasPermission(2))
                .executes(context -> {
                    ServerPlayer player = context.getSource().getPlayerOrException();
                    action.accept(player);
                    return 1;
                });
    }
}
