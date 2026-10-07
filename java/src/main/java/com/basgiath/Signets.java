package com.basgiath;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * The signet archetypes and the questions that reach them.
 *
 * <p>This is the Java port of the table in {@code addon/behavior_pack/scripts/main.js}.
 * The archetypes are original to this map. The IP rules ban character names, book
 * text, and official art; they put no limit on which powers the map may have, so
 * this set is free to grow.
 *
 * <p>Four questions, and each archetype is offered exactly twice, so every outcome
 * is reachable and none is favoured.
 */
public final class Signets {

    private Signets() {}

    /** One archetype: its key, the name shown, and the line under it. */
    public record Signet(String key, String name, String line) {}

    /** One question: the body text, and the four choices, each pointing at a key. */
    public record Question(String body, List<Choice> choices) {}

    public record Choice(String text, String signet) {}

    public static final Map<String, Signet> ALL = new LinkedHashMap<>();

    static {
        add("storm", "Stormcaller", "The air answers before you speak.");
        add("shadow", "Shadowwalker", "You are hardest to find when it matters.");
        add("ember", "Emberwright", "You reach first and ask later.");
        add("stone", "Stoneward", "Nothing moves you that you did not choose.");
        add("mender", "Mender", "You put back what the field takes.");
        add("ward", "Wardsmith", "You build the thing that holds when nothing else does.");
        add("chronicle", "Chronicler", "You remember what everyone else lets go.");
        add("tide", "Tidekeeper", "You keep your footing where the ground gives way.");
    }

    private static void add(String key, String name, String line) {
        ALL.put(key, new Signet(key, name, line));
    }

    public static final List<Question> QUESTIONS = List.of(
            new Question(
                    "A dragon circles overhead. What do you do?",
                    List.of(
                            new Choice("Stand your ground.", "stone"),
                            new Choice("Go still. Go quiet.", "shadow"),
                            new Choice("Reach out your hand.", "ember"),
                            new Choice("Read the wind.", "storm"))),
            new Question(
                    "A cadet falls beside you on the span. What do you do?",
                    List.of(
                            new Choice("Catch them.", "mender"),
                            new Choice("Hold the line.", "ward"),
                            new Choice("Say their name.", "chronicle"),
                            new Choice("Find the footing.", "tide"))),
            new Question(
                    "The wind turns on the crossing. What do you trust?",
                    List.of(
                            new Choice("Your weight.", "tide"),
                            new Choice("Your grip.", "stone"),
                            new Choice("Your nerve.", "ember"),
                            new Choice("Your patience.", "ward"))),
            new Question(
                    "Your wing is losing. What do you change?",
                    List.of(
                            new Choice("The weather.", "storm"),
                            new Choice("The dark.", "shadow"),
                            new Choice("The count.", "chronicle"),
                            new Choice("The wounded.", "mender"))));

    /**
     * The archetype a set of answers points at.
     *
     * <p>A tie for the top score keeps the last answer that was accepted, which is
     * what the Bedrock script does. {@code last} is the key of that answer, or null
     * when no answer was taken.
     */
    public static Signet resolve(Map<String, Integer> scores, String last) {
        int top = 0;
        for (int value : scores.values()) {
            top = Math.max(top, value);
        }
        String winner = null;
        if (last != null && scores.getOrDefault(last, 0) == top) {
            winner = last;
        } else {
            for (Map.Entry<String, Integer> entry : scores.entrySet()) {
                if (entry.getValue() == top) {
                    winner = entry.getKey();
                    break;
                }
            }
        }
        return ALL.get(winner);
    }

    /** A fresh score table, every archetype at zero. */
    public static Map<String, Integer> blankScores() {
        Map<String, Integer> scores = new LinkedHashMap<>();
        for (String key : ALL.keySet()) {
            scores.put(key, 0);
        }
        return scores;
    }
}
