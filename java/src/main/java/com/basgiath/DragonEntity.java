package com.basgiath;

import javax.annotation.Nullable;

import net.minecraft.world.entity.Entity;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.Mob;
import net.minecraft.world.entity.MoverType;
import net.minecraft.world.entity.PathfinderMob;
import net.minecraft.world.entity.ai.attributes.AttributeSupplier;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.entity.ai.goal.FloatGoal;
import net.minecraft.world.entity.ai.goal.LookAtPlayerGoal;
import net.minecraft.world.entity.ai.goal.RandomLookAroundGoal;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;

import software.bernie.geckolib.animatable.GeoEntity;
import software.bernie.geckolib.animatable.instance.AnimatableInstanceCache;
import software.bernie.geckolib.animation.AnimatableManager;
import software.bernie.geckolib.animation.AnimationController;
import software.bernie.geckolib.animation.RawAnimation;
import software.bernie.geckolib.util.GeckoLibUtil;

/**
 * The dragon: a rideable flying mount.
 *
 * <p>Movement is written directly rather than handed to a pathfinder. A mount does
 * not decide where to go, so the only thing worth reading is the rider's own
 * input. Flight is driven from the rider's look direction, so a rider who pitches
 * down dives, and a rider who pitches up climbs.
 *
 * <p>The model and the animations come from GeckoLib, which reads the Bedrock
 * geometry and animation formats directly. The same one model and the same two
 * animations therefore serve both editions: {@code animation.dragon.idle} and
 * {@code animation.dragon.fly}, both written for the Bedrock pack and copied into
 * the Java tree by {@code scripts/build_java_assets.py}.
 */
public class DragonEntity extends PathfinderMob implements GeoEntity {

    /** How much of the speed is carried into a sideways move. */
    private static final double STRAFE_FACTOR = 0.6D;
    /** Air drag. Below 1, so the dragon coasts to a stop instead of stopping dead. */
    private static final double DRAG = 0.91D;

    public DragonEntity(EntityType<? extends DragonEntity> type, Level level) {
        super(type, level);
        // A dragon does not fall. It hovers when it is idle and flies when it is ridden.
        this.setNoGravity(true);
    }

    public static AttributeSupplier.Builder createAttributes() {
        return Mob.createMobAttributes();
    }

    // -----------------------------------------------------------------------
    // GeckoLib
    // -----------------------------------------------------------------------

    private final AnimatableInstanceCache cache = GeckoLibUtil.createInstanceCache(this);

    /**
     * The idle loop, and the wingbeat under it. Both come from the Bedrock pack.
     *
     * <p>The names are the animation file's own keys, not the short form. GeckoLib
     * keys its baked animation map on the JSON key verbatim and looks it up with a
     * plain map get, so {@code "idle"} would match nothing and the dragon would move
     * in silence. These two strings must stay in step with
     * {@code assets/basgiath/animations/entity/dragon.animation.json}.
     */
    public static final String IDLE_ANIMATION = "animation.dragon.idle";
    public static final String FLY_ANIMATION = "animation.dragon.fly";

    private static final RawAnimation IDLE = RawAnimation.begin().thenLoop(IDLE_ANIMATION);
    private static final RawAnimation FLY = RawAnimation.begin().thenLoop(FLY_ANIMATION);

    /**
     * Fly when moving, rest when not.
     *
     * <p>The test is the dragon's own velocity rather than the walk animation, because
     * a flying mount never walks: its limb animation stays at zero and a
     * walk-speed test would leave the wings still while it crossed the sky.
     */
    @Override
    public void registerControllers(AnimatableManager.ControllerRegistrar controllers) {
        controllers.add(new AnimationController<>(this, "movement", 5, state ->
                state.setAndContinue(isFlying() ? FLY : IDLE)));
    }

    /** Whether the dragon is moving enough to be worth a wingbeat. */
    public boolean isFlying() {
        return this.getDeltaMovement().lengthSqr() > 1.0E-4
                || this.getControllingPassenger() != null;
    }

    @Override
    public AnimatableInstanceCache getAnimatableInstanceCache() {
        return this.cache;
    }

    @Override
    protected void registerGoals() {
        this.goalSelector.addGoal(0, new FloatGoal(this));
        this.goalSelector.addGoal(5, new LookAtPlayerGoal(this, Player.class, 16.0F));
        this.goalSelector.addGoal(6, new RandomLookAroundGoal(this));
    }

    /** One rider, on the back. */
    @Override
    protected boolean canAddPassenger(Entity passenger) {
        return this.getPassengers().isEmpty();
    }

    @Override
    @Nullable
    public LivingEntity getControllingPassenger() {
        return this.getFirstPassenger() instanceof Player player ? player : null;
    }

    @Override
    public boolean isPushable() {
        return false;
    }

    @Override
    protected boolean isAffectedByFluids() {
        return false;
    }

    /**
     * Fly, or wait.
     *
     * <p>With a rider, the look direction is the heading and the forward key is the
     * throttle. Without one, the dragon holds its position: a summoned dragon that
     * wandered off would be worse than one that waits.
     */
    @Override
    public void travel(Vec3 input) {
        LivingEntity controller = this.getControllingPassenger();
        if (this.isAlive() && controller instanceof Player rider && this.isControlledByLocalInstance()) {
            this.setYRot(rider.getYRot());
            this.yRotO = this.getYRot();
            this.setXRot(rider.getXRot() * 0.5F);
            this.xRotO = this.getXRot();

            float throttle = rider.zza;
            float strafe = rider.xxa;
            double speed = this.getAttributeValue(Attributes.FLYING_SPEED);
            Vec3 look = this.getViewVector(1.0F);

            Vec3 motion = look.scale(throttle * speed);
            if (strafe != 0.0F) {
                // Level sideways move, so a turn does not also change altitude.
                Vec3 right = new Vec3(-look.z, 0.0D, look.x).normalize();
                motion = motion.add(right.scale(strafe * speed * STRAFE_FACTOR));
            }

            this.setDeltaMovement(this.getDeltaMovement().add(motion).scale(DRAG));
            this.move(MoverType.SELF, this.getDeltaMovement());
            this.setDeltaMovement(this.getDeltaMovement().scale(0.98D));
            return;
        }

        // No rider. Hold station rather than drifting: a summoned dragon that
        // wandered off would be worse than one that waits.
        this.setDeltaMovement(this.getDeltaMovement().scale(0.90D));
        this.move(MoverType.SELF, this.getDeltaMovement());
    }
}
