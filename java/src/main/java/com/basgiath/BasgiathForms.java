package com.basgiath;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import net.minecraft.network.RegistryFriendlyByteBuf;
import net.minecraft.network.chat.Component;
import net.minecraft.network.codec.ByteBufCodecs;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.server.level.ServerPlayer;
import net.neoforged.neoforge.network.PacketDistributor;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/**
 * The forms the Bedrock script showed with {@code @minecraft/server-ui}, and the
 * state that gives them meaning.
 *
 * <p>Bedrock forms block on a promise: {@code await form.show(player)} returns the
 * answer, and the flow reads top to bottom. Java has no such call, so the same
 * flow is split in two. The server sends a form and remembers what it was for; the
 * client answers later over a payload; the server picks the flow back up.
 *
 * <p>That is why every pending flow is a record here rather than a local variable.
 * The state has to outlive the call that started it.
 *
 * <p>Java 1.21.1 has no dialogs. A custom Screen is the option this port takes.
 */
public final class BasgiathForms {

    private BasgiathForms() {}

    /** Which control the client should draw. */
    public enum Kind {
        /** A list of buttons, answered with the index of the one pressed. */
        CHOICE,
        /** A prompt with one text field, answered with the text. */
        TEXT
    }

    // -----------------------------------------------------------------------
    // The payloads
    // -----------------------------------------------------------------------

    /** Server to client: show this form. */
    public record OpenForm(
            int formId, int kind, String title, String body, List<String> options)
            implements CustomPacketPayload {

        public static final CustomPacketPayload.Type<OpenForm> TYPE =
                new CustomPacketPayload.Type<>(
                        ResourceLocation.fromNamespaceAndPath(Basgiath.MOD_ID, "open_form"));

        public static final StreamCodec<RegistryFriendlyByteBuf, OpenForm> CODEC =
                StreamCodec.composite(
                        ByteBufCodecs.VAR_INT, OpenForm::formId,
                        ByteBufCodecs.VAR_INT, OpenForm::kind,
                        ByteBufCodecs.STRING_UTF8, OpenForm::title,
                        ByteBufCodecs.STRING_UTF8, OpenForm::body,
                        ByteBufCodecs.collection(ArrayList::new, ByteBufCodecs.STRING_UTF8),
                        OpenForm::options,
                        OpenForm::new);

        @Override
        public CustomPacketPayload.Type<? extends CustomPacketPayload> type() {
            return TYPE;
        }
    }

    /** Client to server: the answer, or a cancellation. */
    public record FormAnswer(int formId, int selection, String text) implements CustomPacketPayload {

        public static final CustomPacketPayload.Type<FormAnswer> TYPE =
                new CustomPacketPayload.Type<>(
                        ResourceLocation.fromNamespaceAndPath(Basgiath.MOD_ID, "form_answer"));

        /** The selection sent when the player closed the form without answering. */
        public static final int CANCELED = -1;

        public static final StreamCodec<RegistryFriendlyByteBuf, FormAnswer> CODEC =
                StreamCodec.composite(
                        ByteBufCodecs.VAR_INT, FormAnswer::formId,
                        ByteBufCodecs.VAR_INT, FormAnswer::selection,
                        ByteBufCodecs.STRING_UTF8, FormAnswer::text,
                        FormAnswer::new);

        @Override
        public CustomPacketPayload.Type<? extends CustomPacketPayload> type() {
            return TYPE;
        }
    }

    // -----------------------------------------------------------------------
    // The pending flows
    // -----------------------------------------------------------------------

    /** A flow waiting on an answer. */
    public sealed interface Pending {

        /** The signet quiz, part way through. */
        record Quiz(int question, Map<String, Integer> scores, String last) implements Pending {}

        /** A keeper waiting for a name. The id picks which keeper it was. */
        record Keeper(String keeperId) implements Pending {}

        /** The vault desk. */
        record Vault() implements Pending {}

        /** A codex, open at a page. */
        record Codex(String codexId, int page) implements Pending {}

        /** The signet result screen, which can roll again. */
        record Result(String signetKey) implements Pending {}
    }

    private static final Map<UUID, Pending> PENDING = new LinkedHashMap<>();
    private static final Map<UUID, Integer> NEXT_ID = new LinkedHashMap<>();
    /** The form each player is currently looking at, so an older answer can be told apart. */
    private static final Map<UUID, Integer> LIVE_FORM = new LinkedHashMap<>();

    /** Put a form on the screen and remember what the answer is for. */
    public static void open(ServerPlayer player, Pending pending, Kind kind,
                            String title, String body, List<String> options) {
        UUID key = player.getUUID();
        int id = NEXT_ID.merge(key, 1, Integer::sum);
        PENDING.put(key, pending);
        LIVE_FORM.put(key, id);
        PacketDistributor.sendToPlayer(player,
                new OpenForm(id, kind.ordinal(), title, body, List.copyOf(options)));
    }

    /** Forget a player's flow. Called on disconnect so the maps do not grow forever. */
    public static void forget(ServerPlayer player) {
        UUID key = player.getUUID();
        PENDING.remove(key);
        NEXT_ID.remove(key);
        LIVE_FORM.remove(key);
    }

    /**
     * The answer came back. Route it to the flow that asked for it.
     *
     * <p>The form id is checked before anything is touched. A screen is replaced
     * when the server sends the next one, but a client that has not drawn the new
     * form yet can still answer the old one, and that answer would otherwise be
     * applied to the flow that replaced it — a click on "Stand your ground" landing
     * on the wrong question. A mismatched answer is dropped and the live flow is
     * left alone.
     *
     * <p>A cancellation for the live form drops the flow. That matches the Bedrock
     * script, where {@code response.canceled} returns and leaves nothing behind.
     */
    public static void handle(ServerPlayer player, FormAnswer answer) {
        UUID key = player.getUUID();
        Integer live = LIVE_FORM.get(key);
        if (live == null || live.intValue() != answer.formId()) {
            return;
        }
        LIVE_FORM.remove(key);
        Pending pending = PENDING.remove(key);
        if (pending == null) {
            return;
        }
        if (answer.selection() == FormAnswer.CANCELED) {
            return;
        }
        ServerLevel level = player.serverLevel();
        switch (pending) {
            case Pending.Quiz quiz -> SignetFlow.answer(player, level, quiz, answer.selection());
            case Pending.Keeper keeper -> KeeperFlow.answer(player, keeper, answer.text());
            case Pending.Vault ignored -> VaultFlow.answer(player, answer.selection());
            case Pending.Codex codex -> CodexFlow.answer(player, codex, answer.selection());
            case Pending.Result result -> SignetFlow.result(player, result, answer.selection());
        }
    }

    // -----------------------------------------------------------------------
    // The flows
    // -----------------------------------------------------------------------

    /** The signet quiz: four questions, then a result. */
    static final class SignetFlow {

        private SignetFlow() {}

        static void start(ServerPlayer player) {
            ask(player, 0, Signets.blankScores(), null);
        }

        static void ask(ServerPlayer player, int index, Map<String, Integer> scores, String last) {
            if (index >= Signets.QUESTIONS.size()) {
                finish(player, scores, last);
                return;
            }
            Signets.Question question = Signets.QUESTIONS.get(index);
            List<String> options = question.choices().stream().map(Signets.Choice::text).toList();
            open(player,
                    new Pending.Quiz(index, scores, last),
                    Kind.CHOICE,
                    "Signet",
                    question.body(),
                    options);
        }

        static void answer(ServerPlayer player, ServerLevel level, Pending.Quiz quiz, int selection) {
            Map<String, Integer> scores = new LinkedHashMap<>(quiz.scores());
            String last = quiz.last();
            Signets.Question question = Signets.QUESTIONS.get(quiz.question());
            if (selection >= 0 && selection < question.choices().size()) {
                Signets.Choice choice = question.choices().get(selection);
                scores.merge(choice.signet(), 1, Integer::sum);
                last = choice.signet();
            }
            ask(player, quiz.question() + 1, scores, last);
        }

        static void finish(ServerPlayer player, Map<String, Integer> scores, String last) {
            Signets.Signet signet = Signets.resolve(scores, last);
            if (signet == null) {
                return;
            }
            player.setData(BasgiathData.SIGNET, signet.key());
            int riders = BasgiathData.WingRoster.get(player.serverLevel())
                    .remember(player.getUUID(), player.getName().getString(), signet.key());

            player.displayClientMessage(Component.literal("§7Your signet: §6" + signet.name()
                    + "§7. " + signet.line()), false);
            player.displayClientMessage(Component.literal("§7" + wingLine(riders)), false);

            // The result screen. "Again" is index 0, "Done" index 1.
            open(player, new Pending.Result(signet.key()), Kind.CHOICE, "Your signet",
                    "You are a §6" + signet.name() + "§r.\n\n" + signet.line() + "\n\n"
                            + wingLine(riders) + "\n\nTake it again, or put it away.",
                    List.of("Again", "Done"));
        }

        static void result(ServerPlayer player, Pending.Result pending, int selection) {
            if (selection == 0) {
                start(player);
            }
        }

        static String wingLine(int riders) {
            return riders == 1 ? "Your wing has 1 rider." : "Your wing has " + riders + " riders.";
        }
    }

    /** A keeper asking for a name. */
    static final class KeeperFlow {

        private KeeperFlow() {}

        static void start(ServerPlayer player, Keepers.Keeper keeper) {
            if (keeper.needTag() != null && !player.getTags().contains(keeper.needTag())) {
                player.displayClientMessage(Component.literal(keeper.refusal()), false);
                return;
            }
            open(player, new Pending.Keeper(keeper.id()), Kind.TEXT,
                    keeper.title(), keeper.ask(), List.of());
        }

        static void answer(ServerPlayer player, Pending.Keeper pending, String raw) {
            Keepers.Keeper keeper = Keepers.byId(pending.keeperId());
            if (keeper == null) {
                return;
            }
            String name = BasgiathData.cleanName(raw);
            if (name.isEmpty()) {
                player.displayClientMessage(
                        Component.literal("§7That name will not do. Speak again."), false);
                return;
            }
            String previous = player.getData(keeper.attachment());
            player.setData(keeper.attachment(), name);

            if (Keepers.SCROLL.equals(keeper.id())) {
                player.displayClientMessage(Component.literal(
                        previous != null && !previous.isEmpty()
                                ? "§7The scribe strikes the old name and writes §f" + name + "§7."
                                : "§7The scribe writes it down: §f" + name + "§7. Stand in your row."),
                        false);
                // Writing a name reads the roll again, so a rename is heard too.
                player.removeTag(Keepers.ROLLCALL_TAG);
                Keepers.schedule(player);
            } else {
                player.displayClientMessage(Component.literal(
                        "§7The keeper closes the roll. Only you and the keeper know that name."), false);
            }
        }
    }

    /** The academy bank. */
    static final class VaultFlow {

        private VaultFlow() {}

        static final int DEPOSIT = 0;

        static void start(ServerPlayer player) {
            Vault vault = new Vault(player);
            List<String> options = new ArrayList<>();
            options.add("Deposit carried marks");
            for (Vault.Withdrawal entry : Vault.WITHDRAWALS) {
                options.add(entry.label() + " (" + entry.cost() + ")");
            }
            open(player, new Pending.Vault(), Kind.CHOICE, "Vault Desk",
                    "You carry " + vault.carried() + " in marks.\nThe vault holds "
                            + BasgiathData.bank(player) + ".",
                    options);
        }

        static void answer(ServerPlayer player, int selection) {
            Vault vault = new Vault(player);
            if (selection == DEPOSIT) {
                int banked = vault.depositAll();
                player.displayClientMessage(Component.literal(banked > 0
                        ? "§7The desk counts §f" + banked + "§7 into the vault. It holds §f"
                                + BasgiathData.bank(player) + "§7."
                        : "§7There is nothing in your hands to bank."), false);
                return;
            }
            int index = selection - 1;
            if (index < 0 || index >= Vault.WITHDRAWALS.size()) {
                return;
            }
            boolean paid = vault.withdraw(Vault.WITHDRAWALS.get(index));
            player.displayClientMessage(Component.literal(paid
                    ? "§7The desk pays out. The vault holds §f" + BasgiathData.bank(player) + "§7."
                    : "§7The vault cannot cover that, or your hands are full."), false);
        }
    }

    /** A codex, page by page. */
    static final class CodexFlow {

        private CodexFlow() {}

        static void start(ServerPlayer player, Codices.Codex codex) {
            page(player, codex, 0);
        }

        static void page(ServerPlayer player, Codices.Codex codex, int page) {
            int index = Math.max(0, Math.min(page, codex.pages().size() - 1));
            List<String> options = new ArrayList<>();
            if (index < codex.pages().size() - 1) {
                options.add("Next page");
            }
            if (index > 0) {
                options.add("Previous page");
            }
            options.add("Close");
            open(player, new Pending.Codex(codex.id(), index), Kind.CHOICE,
                    codex.title() + " - page " + (index + 1) + " of " + codex.pages().size(),
                    codex.pages().get(index), options);
        }

        static void answer(ServerPlayer player, Pending.Codex pending, int selection) {
            Codices.Codex codex = Codices.byId(pending.codexId());
            if (codex == null) {
                return;
            }
            int index = pending.page();
            boolean hasNext = index < codex.pages().size() - 1;
            boolean hasBack = index > 0;
            List<String> actions = new ArrayList<>();
            if (hasNext) {
                actions.add("next");
            }
            if (hasBack) {
                actions.add("back");
            }
            actions.add("close");
            if (selection < 0 || selection >= actions.size()) {
                return;
            }
            switch (actions.get(selection)) {
                case "next" -> page(player, codex, index + 1);
                case "back" -> page(player, codex, index - 1);
                default -> {
                    // Closed. Nothing to do.
                }
            }
        }
    }

}
