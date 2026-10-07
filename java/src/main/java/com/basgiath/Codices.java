package com.basgiath;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import net.minecraft.world.item.Item;

/**
 * The readable codices.
 *
 * <p>Using one opens its pages. Every line is original fan writing: no passage from
 * any book, and no character name. {@code docs/CANON.md} holds the denylist, and the
 * release check scans these strings for it.
 */
public final class Codices {

    private Codices() {}

    /** One book: its item id, the title shown, and its pages. */
    public record Codex(String id, String title, List<String> pages) {}

    private static final Map<String, Codex> BY_ITEM = new LinkedHashMap<>();

    public static final Codex FLIGHT_MANUAL = register("flight_manual", "Flight Manual", List.of(
            "A wing answers the air, not the reins. Sit your weight forward and let the "
                    + "shoulders carry you. The animal reads the shift before you have finished "
                    + "making it.",
            "Climb in long lines, not sharp ones. A hard turn costs more than a climb, and a "
                    + "climb costs more than patience. Most first-month falls are a turn taken too "
                    + "late.",
            "When the wind turns against you, spend the height you have and wait it out. "
                    + "Nothing on the field is worth a broken neck before the season is out."));

    public static final Codex DRAGON_CODEX = register("dragon_codex", "Dragon Codex", List.of(
            "The animal chooses before you do. Stand still, keep your hands down, and let it "
                    + "walk its circle. A circle means it is still deciding.",
            "A bond is not a leash. You will not command it and it will not obey. What the two "
                    + "of you build is a habit of glancing the same way at the same time.",
            "Feed it away from the others. A dragon crowded at its meal learns to guard the "
                    + "plate, and a guarding dragon is a danger to every rider nearby."));

    public static final Codex ACADEMY_ARCHIVE = register("academy_archive", "Academy Archive", List.of(
            "The Parapet has been rebuilt twice. The first crossing was walked at night, in a "
                    + "storm, and the cadet who walked it came back along the span rather than "
                    + "over the gap.",
            "The flight field floods every spring. That is why it sits where it does: the "
                    + "ground there is flat, and flat ground is rare on this side of the Vale.",
            "Old riders say the Gauntlet measures a person. It measures only whether you stop "
                    + "at the far edge, which is a different question and a shorter one."));

    private static Codex register(String id, String title, List<String> pages) {
        Codex codex = new Codex(id, title, pages);
        BY_ITEM.put(id, codex);
        return codex;
    }

    /** The codex an item opens, or null when the item is not a codex. */
    public static Codex forItem(Item item) {
        for (Map.Entry<String, Codex> entry : BY_ITEM.entrySet()) {
            if (itemFor(entry.getKey()) == item) {
                return entry.getValue();
            }
        }
        return null;
    }

    public static Codex byId(String id) {
        return BY_ITEM.get(id);
    }

    private static Item itemFor(String id) {
        return switch (id) {
            case "flight_manual" -> BasgiathContent.FLIGHT_MANUAL.get();
            case "dragon_codex" -> BasgiathContent.DRAGON_CODEX.get();
            case "academy_archive" -> BasgiathContent.ACADEMY_ARCHIVE.get();
            default -> null;
        };
    }
}
