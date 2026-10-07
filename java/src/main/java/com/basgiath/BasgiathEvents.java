package com.basgiath;

import java.util.List;
import java.util.UUID;

import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.decoration.ArmorStand;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.event.entity.player.PlayerEvent;
import net.neoforged.neoforge.event.entity.player.PlayerInteractEvent;
import net.neoforged.neoforge.event.server.ServerStoppingEvent;
import net.neoforged.neoforge.event.tick.ServerTickEvent;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/**
 * The Bedrock script's event handlers.
 *
 * <p>Bedrock subscribed to {@code playerInteractWithBlock}, {@code itemUse}, and
 * {@code scriptEventReceive}, and drove the map from {@code runInterval}. Those
 * jobs are here, except the tick loop, which the datapack now owns through the
 * {@code minecraft:tick} function tag.
 *
 * <p>Every handler here is a game-bus event, so the class is registered on
 * {@code NeoForge.EVENT_BUS} by name from {@link Basgiath}. It carries no
 * {@code @EventBusSubscriber}, because that annotation's bus argument is deprecated
 * and this class must land on one known bus.
 */
public final class BasgiathEvents {

    /** The armor stand the generator builds the college around. */
    public static final String BUILD_ANCHOR = "build_anchor";

    /** The dell stone, in anchor-relative block coordinates. */
    public static final BlockPos SIGNET_STONE = new BlockPos(50, -1, 130);

    /** Set by Threshing when a dragon chooses the rider. */
    public static final String BOND_TAG = "bonded";

    /** How far around the player to look for the anchor when the cache is cold. */
    private static final int SEARCH_RADIUS = 320;

    private static UUID cachedAnchor;
    private static BlockPos cachedOrigin;

    // -----------------------------------------------------------------------
    // Finding the build
    // -----------------------------------------------------------------------

    /**
     * The block the college was raised from.
     *
     * <p>Every stage command is anchor-relative, so an absolute block position is the
     * anchor's floor plus the stage's offset. The anchor is killed and re-summoned by
     * a rebuild, which changes its id, so the cache cannot serve a stale origin: a
     * lookup by id simply misses and the search runs again.
     *
     * <p>The search is bounded rather than world-wide. Everything this mod reacts to
     * stands inside the college, and the college is at most a few hundred blocks
     * across, so a box around the player is enough. A world-wide scan on every click
     * would be the Bedrock script's cost without its excuse.
     */
    public static BlockPos buildOrigin(ServerLevel level, BlockPos near) {
        if (cachedAnchor != null) {
            Entity entity = level.getEntity(cachedAnchor);
            if (entity instanceof ArmorStand stand && stand.isAlive()) {
                return floor(stand);
            }
            cachedAnchor = null;
            cachedOrigin = null;
        }
        var box = new net.minecraft.world.phys.AABB(
                near.getX() - SEARCH_RADIUS, level.getMinBuildHeight(), near.getZ() - SEARCH_RADIUS,
                near.getX() + SEARCH_RADIUS, level.getMaxBuildHeight(), near.getZ() + SEARCH_RADIUS);
        List<ArmorStand> stands = level.getEntitiesOfClass(ArmorStand.class, box,
                stand -> stand.hasCustomName()
                        && BUILD_ANCHOR.equals(stand.getCustomName().getString()));
        if (stands.isEmpty()) {
            return null;
        }
        ArmorStand anchor = stands.get(0);
        cachedAnchor = anchor.getUUID();
        cachedOrigin = floor(anchor);
        return cachedOrigin;
    }

    private static BlockPos floor(ArmorStand stand) {
        // A block command floors its position: an anchor at x = 8.5 puts ~128 at
        // block 136, not 136.5.
        return new BlockPos((int) Math.floor(stand.getX()), (int) Math.floor(stand.getY()),
                (int) Math.floor(stand.getZ()));
    }

    public static void forgetOrigin() {
        cachedAnchor = null;
        cachedOrigin = null;
    }

    // -----------------------------------------------------------------------
    // Interactions
    // -----------------------------------------------------------------------

    @SubscribeEvent
    public static void onRightClickBlock(PlayerInteractEvent.RightClickBlock event) {
        if (!(event.getEntity() instanceof ServerPlayer player)
                || !(event.getLevel() instanceof ServerLevel level)) {
            return;
        }
        BlockPos pos = event.getPos();
        BlockState state = level.getBlockState(pos);

        if (state.is(BasgiathContent.VAULT_DESK.get())) {
            deny(event);
            BasgiathForms.VaultFlow.start(player);
            return;
        }

        BlockPos origin = buildOrigin(level, pos);

        if (state.is(Blocks.LODESTONE)) {
            // Only the dell stone opens the signet form. A lodestone anywhere else is
            // left alone, so vanilla behaviour stands for a stone that is not ours.
            if (origin == null || !pos.equals(origin.offset(SIGNET_STONE))) {
                return;
            }
            deny(event);
            if (player.getTags().contains(BOND_TAG)) {
                BasgiathForms.SignetFlow.start(player);
            } else {
                player.displayClientMessage(
                        Component.literal("§7A signet comes after a dragon chooses you."), false);
            }
            return;
        }

        if (state.is(Blocks.LECTERN)) {
            // No anchor means the college was never built here. Say so rather than
            // letting the page screen open on a lectern that means nothing.
            if (origin == null) {
                deny(event);
                player.displayClientMessage(Component.literal(
                        "§7The college is not built here. Run /function basgiath:build first."), false);
                return;
            }
            for (Keepers.Keeper keeper : Keepers.ALL) {
                if (pos.equals(origin.offset(keeper.offset()))) {
                    deny(event);
                    BasgiathForms.KeeperFlow.start(player, keeper);
                    return;
                }
            }
        }
    }

    /** Stop the block's own use, so a lectern never opens its own page screen. */
    private static void deny(PlayerInteractEvent.RightClickBlock event) {
        event.setUseBlock(net.neoforged.neoforge.common.util.TriState.FALSE);
        event.setUseItem(net.neoforged.neoforge.common.util.TriState.FALSE);
        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.SUCCESS);
    }

    @SubscribeEvent
    public static void onRightClickItem(PlayerInteractEvent.RightClickItem event) {
        if (!(event.getEntity() instanceof ServerPlayer player)) {
            return;
        }
        ItemStack stack = event.getItemStack();
        if (stack.isEmpty()) {
            return;
        }
        Codices.Codex codex = Codices.forItem(stack.getItem());
        if (codex == null) {
            return;
        }
        event.setCanceled(true);
        event.setCancellationResult(InteractionResult.SUCCESS);
        BasgiathForms.CodexFlow.start(player, codex);
    }

    // -----------------------------------------------------------------------
    // The tick
    // -----------------------------------------------------------------------

    @SubscribeEvent
    public static void onServerTick(ServerTickEvent.Post event) {
        MinecraftServer server = event.getServer();
        Keepers.tick(server);
        FlightHud.tick(server);
    }

    @SubscribeEvent
    public static void onLogout(PlayerEvent.PlayerLoggedOutEvent event) {
        if (event.getEntity() instanceof ServerPlayer player) {
            BasgiathForms.forget(player);
            Keepers.forget(player);
            FlightHud.forget(player);
        }
    }

    @SubscribeEvent
    public static void onServerStopping(ServerStoppingEvent event) {
        forgetOrigin();
    }

    /** Deliver a form answer to the flow that asked for it. */
    public static void handleFormAnswer(BasgiathForms.FormAnswer payload, IPayloadContext context) {
        if (context.player() instanceof ServerPlayer player) {
            // The client sends an answer outside the tick, so put it back on the
            // server thread rather than touching world state from the network thread.
            player.server.execute(() -> BasgiathForms.handle(player, payload));
        }
    }
}
