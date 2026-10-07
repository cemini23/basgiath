package com.basgiath;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import com.mojang.serialization.Codec;

import net.minecraft.core.HolderLookup;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.Tag;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.player.Player;
import net.neoforged.neoforge.attachment.AttachmentType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;

/**
 * Everything that has to survive a restart.
 *
 * <p>The Bedrock script kept per-player values in dynamic properties and the wing
 * roster in a world dynamic property. On Java those become two different things,
 * because they have two different lifetimes:
 *
 * <ul>
 *   <li>Per-player values are <b>data attachments</b>. They ride the player, they
 *       persist with the player, and they copy on death.
 *   <li>The wing roster is one list for the whole world, so it is <b>SavedData</b>
 *       on the overworld. It outlives any one player.
 * </ul>
 *
 * <p>The Bedrock script keyed the roster on the player id rather than the display
 * name, so a rename cannot put the same rider on a wing twice. The same key is
 * used here.
 */
public final class BasgiathData {

    private BasgiathData() {}

    public static final DeferredRegister<AttachmentType<?>> ATTACHMENTS =
            DeferredRegister.create(NeoForgeRegistries.ATTACHMENT_TYPES, Basgiath.MOD_ID);

    /** The signet key this player rolled, or empty. */
    public static final DeferredHolder<AttachmentType<?>, AttachmentType<String>> SIGNET =
            ATTACHMENTS.register("signet", () -> AttachmentType.builder(() -> "")
                    .serialize(Codec.STRING).copyOnDeath().build());

    /** The rider's own name, written at the scroll lectern. */
    public static final DeferredHolder<AttachmentType<?>, AttachmentType<String>> RIDER_NAME =
            ATTACHMENTS.register("rider_name", () -> AttachmentType.builder(() -> "")
                    .serialize(Codec.STRING).copyOnDeath().build());

    /** The full name of the dragon that chose the rider, written at the roll lectern. */
    public static final DeferredHolder<AttachmentType<?>, AttachmentType<String>> DRAGON_NAME =
            ATTACHMENTS.register("dragon_name", () -> AttachmentType.builder(() -> "")
                    .serialize(Codec.STRING).copyOnDeath().build());

    /** Marks held at the vault desk. */
    public static final DeferredHolder<AttachmentType<?>, AttachmentType<Integer>> BANK =
            ATTACHMENTS.register("bank", () -> AttachmentType.builder(() -> 0)
                    .serialize(Codec.INT).copyOnDeath().build());

    public static String signet(Player player) {
        String value = player.getData(SIGNET);
        return value == null ? "" : value;
    }

    public static String riderName(Player player) {
        String value = player.getData(RIDER_NAME);
        return value == null ? "" : value;
    }

    public static String dragonName(Player player) {
        String value = player.getData(DRAGON_NAME);
        return value == null ? "" : value;
    }

    public static int bank(Player player) {
        Integer value = player.getData(BANK);
        return value == null ? 0 : Math.max(0, value);
    }

    public static void setBank(Player player, int value) {
        player.setData(BANK, Math.max(0, value));
    }

    /**
     * Strip what a name may not carry.
     *
     * <p>Names are player input. Colour codes and control characters come out, runs
     * of whitespace collapse, and the length is capped. This is the same cleaning
     * the Bedrock script did.
     */
    public static String cleanName(String raw) {
        if (raw == null) {
            return "";
        }
        String stripped = raw.replaceAll("§.", "")
                .replaceAll("[\\u0000-\\u001f\\u007f]", " ")
                .replaceAll("\\s+", " ")
                .trim();
        return stripped.length() > 16 ? stripped.substring(0, 16) : stripped;
    }

    // -----------------------------------------------------------------------
    // The wing roster
    // -----------------------------------------------------------------------

    /** One rider on the wing. */
    public record WingEntry(UUID id, String name, String signet) {}

    /**
     * The whole world's wing roster, most recent last, capped at 24 riders.
     *
     * <p>Bedrock kept this as a JSON string in a world dynamic property, which meant
     * a failed parse silently emptied the wing. Here the list is structured NBT, so
     * a bad tag costs one entry and not the roster.
     */
    public static class WingRoster extends net.minecraft.world.level.saveddata.SavedData {

        public static final String DATA_NAME = "basgiath_wing_roster";
        private static final int MAX_ENTRIES = 24;

        private final Map<UUID, WingEntry> entries = new LinkedHashMap<>();

        public static WingRoster get(ServerLevel level) {
            return level.getServer().overworld().getDataStorage().computeIfAbsent(
                    new net.minecraft.world.level.saveddata.SavedData.Factory<>(
                            WingRoster::new, WingRoster::load),
                    DATA_NAME);
        }

        public static WingRoster load(CompoundTag tag, HolderLookup.Provider registries) {
            WingRoster roster = new WingRoster();
            ListTag list = tag.getList("riders", Tag.TAG_COMPOUND);
            for (int index = 0; index < list.size(); index++) {
                CompoundTag entry = list.getCompound(index);
                try {
                    UUID id = entry.getUUID("id");
                    roster.entries.put(id, new WingEntry(
                            id, entry.getString("name"), entry.getString("signet")));
                } catch (RuntimeException ignored) {
                    // One malformed entry costs that entry, never the roster.
                }
            }
            return roster;
        }

        @Override
        public CompoundTag save(CompoundTag tag, HolderLookup.Provider registries) {
            ListTag list = new ListTag();
            for (WingEntry entry : entries.values()) {
                CompoundTag row = new CompoundTag();
                row.putUUID("id", entry.id());
                row.putString("name", entry.name());
                row.putString("signet", entry.signet());
                list.add(row);
            }
            tag.put("riders", list);
            return tag;
        }

        /** Put one rider on the wing, replacing any earlier entry for that rider. */
        public int remember(UUID id, String name, String signet) {
            List<WingEntry> ordered = new ArrayList<>(entries.values());
            ordered.removeIf(entry -> entry.id().equals(id));
            ordered.add(new WingEntry(id, name, signet));
            while (ordered.size() > MAX_ENTRIES) {
                ordered.remove(0);
            }
            entries.clear();
            for (WingEntry entry : ordered) {
                entries.put(entry.id(), entry);
            }
            setDirty();
            return entries.size();
        }

        public int size() {
            return entries.size();
        }
    }
}
