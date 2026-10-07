package com.basgiath;

import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.UUID;

import net.minecraft.network.chat.Component;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.phys.Vec3;

/**
 * The rider's dragon readout: speed, altitude, and stamina, on the action bar.
 *
 * <p>The whole point is the easing. A reading taken every tick changes constantly and
 * reads as noise, so each number tweens toward its new value on an ease-in-out
 * curve. The display settles, and a change is visible as a change rather than a
 * flicker.
 *
 * <p>Speed is read from the dragon's own movement since the last draw, so it needs
 * no velocity API. This is a direct port of the Bedrock readout.
 */
public final class FlightHud {

    private FlightHud() {}

    /** Ticks between redraws, so five draws a second. */
    private static final int HUD_INTERVAL = 4;
    /** Redraws an eased change takes. */
    private static final int TWEEN_DRAWS = 5;
    private static final int BAR_CELLS = 10;
    /** Blocks per second that counts as full work. */
    private static final double FAST = 20.0D;
    private static final double STAMINA_MAX = 100.0D;
    private static final double STAMINA_DRAIN = 3.0D;
    private static final double STAMINA_RECOVER = 1.2D;
    private static final double STAMINA_WORK = 0.35D;
    /** While a rider carries this tag the course clock owns the action bar. */
    private static final String COURSE_TAG = "timed_run";

    private static int countdown;

    /** One player's readout state. */
    private static final class State {
        final Eased speed = new Eased(0.0D);
        final Eased altitude = new Eased(0.0D);
        final Eased stamina = new Eased(STAMINA_MAX);
        double bar = STAMINA_MAX;
        Vec3 last;
        boolean shown;
    }

    private static final Map<UUID, State> STATES = new HashMap<>();

    /**
     * A number that slides to a new target instead of jumping to it.
     *
     * <p>Re-aiming restarts the curve from wherever the value has reached, so a
     * target that moves mid-tween does not snap back.
     */
    private static final class Eased {
        double value;
        double from;
        double to;
        int step = TWEEN_DRAWS;

        Eased(double value) {
            this.value = value;
            this.from = value;
            this.to = value;
        }

        void aim(double target) {
            if (target != this.to) {
                this.from = this.value;
                this.to = target;
                this.step = 0;
            }
        }

        double advance() {
            if (this.step < TWEEN_DRAWS) {
                this.step += 1;
            }
            double t = (double) this.step / TWEEN_DRAWS;
            this.value = this.from + (this.to - this.from) * easeInOutCubic(t);
            return this.value;
        }
    }

    /** Slow at both ends, fast through the middle. A linear walk reads as a slide. */
    private static double easeInOutCubic(double t) {
        if (t <= 0.0D) {
            return 0.0D;
        }
        if (t >= 1.0D) {
            return 1.0D;
        }
        return t < 0.5D ? 4.0D * t * t * t : 1.0D - Math.pow(-2.0D * t + 2.0D, 3.0D) / 2.0D;
    }

    private static double clamp(double value, double low, double high) {
        return value < low ? low : value > high ? high : value;
    }

    /** Colour carries the fill, so any font renders the bar. */
    private static String staminaBar(double value) {
        int filled = (int) Math.round(clamp(value / STAMINA_MAX, 0.0D, 1.0D) * BAR_CELLS);
        return "§a" + "|".repeat(filled) + "§8" + "|".repeat(BAR_CELLS - filled);
    }

    public static void tick(MinecraftServer server) {
        countdown += 1;
        if (countdown < HUD_INTERVAL) {
            return;
        }
        countdown = 0;
        for (ServerPlayer player : server.getPlayerList().getPlayers()) {
            try {
                if (player.getTags().contains(COURSE_TAG)) {
                    continue; // the course clock owns the line
                }
                draw(player);
            } catch (RuntimeException ignored) {
                // One player's readout must never take the tick loop down.
            }
        }
    }

    private static void draw(ServerPlayer player) {
        State state = STATES.computeIfAbsent(player.getUUID(), id -> new State());

        DragonEntity mount = player.getVehicle() instanceof DragonEntity dragon ? dragon : null;
        if (mount == null) {
            state.last = null;
            if (state.shown) {
                player.displayClientMessage(Component.literal("§7"), true);
                state.shown = false;
            }
            return;
        }

        Vec3 here = mount.position();
        double speed = 0.0D;
        if (state.last != null) {
            speed = here.distanceTo(state.last) / (HUD_INTERVAL / 20.0D);
        }
        state.last = here;

        state.shown = true;
        state.speed.aim(speed);
        state.altitude.aim(here.y);

        double work = clamp(speed / FAST, 0.0D, 1.0D);
        state.bar = clamp(
                state.bar + (work > STAMINA_WORK ? -STAMINA_DRAIN * work : STAMINA_RECOVER),
                0.0D, STAMINA_MAX);
        state.stamina.aim(state.bar);

        double shownSpeed = state.speed.advance();
        double shownAltitude = state.altitude.advance();
        double shownStamina = state.stamina.advance();

        player.displayClientMessage(Component.literal(
                "§bSpeed §f" + String.format("%.1f", shownSpeed) + "§7 b/s  "
                        + "§bAlt §f" + Math.round(shownAltitude) + "  "
                        + "§bStamina §r" + staminaBar(shownStamina)), true);
    }

    /** Drop a player's readout. Called on disconnect so the map cannot grow forever. */
    public static void forget(ServerPlayer player) {
        STATES.remove(player.getUUID());
    }

    /** Drop readouts for players who are no longer online. */
    public static void prune(MinecraftServer server) {
        Iterator<UUID> it = STATES.keySet().iterator();
        while (it.hasNext()) {
            if (server.getPlayerList().getPlayer(it.next()) == null) {
                it.remove();
            }
        }
    }
}
