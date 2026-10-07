package com.basgiath;

import java.util.ArrayList;
import java.util.List;

import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;

/**
 * The academy bank.
 *
 * <p>The vault desk takes the marks a cadet is carrying and keeps a balance per
 * rider, then pays marks back out. The balance is a data attachment, so it survives
 * a restart and needs no scoreboard.
 *
 * <p>Every value is in copper marks and matches the conversion ratios: a silver
 * mark is nine copper, a gold mark is nine silver, a note is nine gold.
 */
public final class Vault {

    /** One denomination: the item, and what it is worth in copper. */
    public record Denomination(Item item, int value) {}

    /** One payout: what the desk pays, and what it costs. */
    public record Withdrawal(String label, Item item, int cost) {}

    public static final List<Withdrawal> WITHDRAWALS = List.of(
            new Withdrawal("Withdraw a silver mark", BasgiathContent.SILVER_MARK.get(), 9),
            new Withdrawal("Withdraw a gold mark", BasgiathContent.GOLD_MARK.get(), 81),
            new Withdrawal("Withdraw a bank note", BasgiathContent.BANK_NOTE.get(), 729));

    private final ServerPlayer player;

    public Vault(ServerPlayer player) {
        this.player = player;
    }

    private static List<Denomination> currency() {
        return List.of(
                new Denomination(BasgiathContent.COPPER_MARK.get(), 1),
                new Denomination(BasgiathContent.SILVER_MARK.get(), 9),
                new Denomination(BasgiathContent.GOLD_MARK.get(), 81),
                new Denomination(BasgiathContent.BANK_NOTE.get(), 729));
    }

    /** The slot numbers holding a mark, so a deposit can empty exactly those. */
    private List<Integer> markSlots() {
        List<Integer> slots = new ArrayList<>();
        var inventory = player.getInventory();
        for (int slot = 0; slot < inventory.getContainerSize(); slot++) {
            if (valueOf(inventory.getItem(slot)) > 0) {
                slots.add(slot);
            }
        }
        return slots;
    }

    private static int valueOf(ItemStack stack) {
        if (stack.isEmpty()) {
            return 0;
        }
        for (Denomination coin : currency()) {
            if (stack.is(coin.item())) {
                return coin.value() * stack.getCount();
            }
        }
        return 0;
    }

    /** What the rider is carrying, in copper marks. */
    public int carried() {
        int total = 0;
        var inventory = player.getInventory();
        for (int slot = 0; slot < inventory.getContainerSize(); slot++) {
            total += valueOf(inventory.getItem(slot));
        }
        return total;
    }

    /** Bank everything the rider carries. Returns how much was banked. */
    public int depositAll() {
        int total = 0;
        var inventory = player.getInventory();
        for (int slot : markSlots()) {
            total += valueOf(inventory.getItem(slot));
            inventory.setItem(slot, ItemStack.EMPTY);
        }
        if (total > 0) {
            BasgiathData.setBank(player, BasgiathData.bank(player) + total);
        }
        return total;
    }

    /**
     * Pay out one denomination.
     *
     * <p>The marks are charged only if the pack accepted them. A full inventory must
     * not cost the rider anything.
     */
    public boolean withdraw(Withdrawal entry) {
        if (BasgiathData.bank(player) < entry.cost()) {
            return false;
        }
        ItemStack stack = new ItemStack(entry.item(), 1);
        if (!player.getInventory().add(stack) && !stack.isEmpty()) {
            return false;
        }
        BasgiathData.setBank(player, BasgiathData.bank(player) - entry.cost());
        return true;
    }
}
