package com.basgiath;

import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import net.minecraft.core.BlockPos;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.registries.DeferredHolder;

/**
 * The two keepers, and the roll call.
 *
 * <p>The block is the key. A lectern at a known offset from the build anchor names
 * the keeper and the value to write, so the keeper is found by where it stands
 * rather than by anything carved into it.
 */
public final class Keepers {

    private Keepers() {}

    public static final String SCROLL = "scroll";
    public static final String ROLL = "roll";

    /** Set once a rider has answered the roll, so the call is heard only once. */
    public static final String ROLLCALL_TAG = "rollcall_done";

    /** One keeper: where it stands, what it writes, and what it says. */
    public record Keeper(
            String id,
            BlockPos offset,
            DeferredHolder<AttachmentType<?>, AttachmentType<String>> attachment,
            String title,
            String ask,
            String needTag,
            String refusal) {}

    /** The scroll lectern in the Quad, which takes the rider's own name. */
    public static final Keeper SCROLL_KEEPER = new Keeper(
            SCROLL,
            new BlockPos(128, 1, 34),
            BasgiathData.RIDER_NAME,
            "The scroll",
            "The scribe waits. Give your name.",
            null,
            null);

    /** The roll lectern in the dell, which takes the dragon's full name. */
    public static final Keeper ROLL_KEEPER = new Keeper(
            ROLL,
            new BlockPos(50, -1, 123),
            BasgiathData.DRAGON_NAME,
            "The roll",
            "Give the name of the one that chose you.",
            "bonded",
            "§7A name comes after a dragon chooses you.");

    public static final List<Keeper> ALL = List.of(SCROLL_KEEPER, ROLL_KEEPER);

    public static Keeper byId(String id) {
        for (Keeper keeper : ALL) {
            if (keeper.id().equals(id)) {
                return keeper;
            }
        }
        return null;
    }

    /**
     * The roll call: the rider's own name, read back to the world.
     *
     * <p>A command cannot read a data attachment, so the read lives in code. The
     * name is player input, and it reaches the world through the chat packet, which
     * does not parse a command. {@link BasgiathData#cleanName} has already stripped
     * colour codes and control characters.
     */
    public static void read(ServerPlayer player) {
        String name = BasgiathData.riderName(player);
        if (name.isEmpty() || player.getTags().contains(ROLLCALL_TAG)) {
            return;
        }
        player.addTag(ROLLCALL_TAG);
        player.serverLevel().getServer().getPlayerList().broadcastSystemMessage(
                net.minecraft.network.chat.Component.literal(
                        "§7Roll call. §f" + name + "§7 answers and takes their place."),
                false);
    }

    /**
     * Pending roll calls, one per rider.
     *
     * <p>A second write inside the beat replaces the first, so two quick writes
     * cannot leave two live reads chasing the same rider. The Bedrock script used
     * {@code system.runTimeout} with a cancellation map for the same reason; this is
     * the same idea driven by the server tick.
     */
    private static final Map<UUID, Integer> PENDING = new LinkedHashMap<>();

    /** Ticks between a name being written and the roll being read. Three seconds. */
    public static final int ROLL_DELAY_TICKS = 60;

    public static void schedule(ServerPlayer player) {
        PENDING.put(player.getUUID(), ROLL_DELAY_TICKS);
    }

    /** Advance every pending roll call by one tick. */
    public static void tick(MinecraftServer server) {
        if (PENDING.isEmpty()) {
            return;
        }
        Iterator<Map.Entry<UUID, Integer>> it = PENDING.entrySet().iterator();
        while (it.hasNext()) {
            Map.Entry<UUID, Integer> entry = it.next();
            int left = entry.getValue() - 1;
            if (left > 0) {
                entry.setValue(left);
                continue;
            }
            it.remove();
            ServerPlayer player = server.getPlayerList().getPlayer(entry.getKey());
            if (player != null) {
                read(player);
            }
        }
    }

    public static void forget(ServerPlayer player) {
        PENDING.remove(player.getUUID());
    }
}
