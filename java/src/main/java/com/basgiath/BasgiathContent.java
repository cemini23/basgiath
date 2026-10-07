package com.basgiath;

import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.minecraft.world.entity.ai.attributes.Attributes;
import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.CreativeModeTab;
import net.minecraft.world.item.Item;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.event.entity.EntityAttributeCreationEvent;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;

/**
 * Everything the mod registers: the dragon, the vault desk, the marks, and the
 * codices.
 *
 * <p>The ids match the Bedrock add-on's names, so one map and one item set read the
 * same on both editions. The namespace is the mod id, so the Bedrock prefix becomes
 * the mod id here. That divergence is deliberate and is the one place the two
 * editions spell an id differently. The Bedrock prefix itself is not written out in
 * this file: the release test scans Java sources for it, and a build that names it
 * here would fail that test for no good reason.
 */
public final class BasgiathContent {

    private BasgiathContent() {}

    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(Registries.ENTITY_TYPE, Basgiath.MOD_ID);
    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(Basgiath.MOD_ID);
    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(Basgiath.MOD_ID);
    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, Basgiath.MOD_ID);

    /** The dragon. Summoned by {@code basgiath:summon_dragon}, and rideable. */
    public static final DeferredHolder<EntityType<?>, EntityType<DragonEntity>> DRAGON =
            ENTITY_TYPES.register("dragon", () -> EntityType.Builder
                    .of(DragonEntity::new, MobCategory.CREATURE)
                    .sized(3.0F, 2.2F)
                    .clientTrackingRange(12)
                    .build("dragon"));

    /** The academy bank. Interacting with it opens the vault desk. */
    public static final DeferredBlock<Block> VAULT_DESK = BLOCKS.register("vault_desk",
            () -> new Block(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.WOOD)
                    .strength(2.5F)
                    .sound(SoundType.WOOD)));
    public static final DeferredItem<BlockItem> VAULT_DESK_ITEM =
            ITEMS.registerSimpleBlockItem("vault_desk", VAULT_DESK);

    // The marks. One silver is nine copper, one gold is nine silver, one note is
    // nine gold. The vault desk honours those ratios.
    public static final DeferredItem<Item> COPPER_MARK = ITEMS.registerSimpleItem("copper_mark");
    public static final DeferredItem<Item> SILVER_MARK = ITEMS.registerSimpleItem("silver_mark");
    public static final DeferredItem<Item> GOLD_MARK = ITEMS.registerSimpleItem("gold_mark");
    public static final DeferredItem<Item> BANK_NOTE = ITEMS.registerSimpleItem("bank_note");

    // The codices. Using one opens its pages.
    public static final DeferredItem<Item> FLIGHT_MANUAL = ITEMS.registerSimpleItem("flight_manual");
    public static final DeferredItem<Item> DRAGON_CODEX = ITEMS.registerSimpleItem("dragon_codex");
    public static final DeferredItem<Item> ACADEMY_ARCHIVE = ITEMS.registerSimpleItem("academy_archive");

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> TAB = TABS.register("basgiath",
            () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.basgiath"))
                    .icon(() -> COPPER_MARK.get().getDefaultInstance())
                    .displayItems((parameters, output) -> {
                        output.accept(VAULT_DESK_ITEM.get());
                        output.accept(COPPER_MARK.get());
                        output.accept(SILVER_MARK.get());
                        output.accept(GOLD_MARK.get());
                        output.accept(BANK_NOTE.get());
                        output.accept(FLIGHT_MANUAL.get());
                        output.accept(DRAGON_CODEX.get());
                        output.accept(ACADEMY_ARCHIVE.get());
                    })
                    .build());

    /** The dragon's attributes. A mount has to be worth riding and hard to lose. */
    public static void onEntityAttributes(EntityAttributeCreationEvent event) {
        event.put(DRAGON.get(), DragonEntity.createAttributes()
                .add(Attributes.MAX_HEALTH, 80.0D)
                .add(Attributes.MOVEMENT_SPEED, 0.30D)
                .add(Attributes.FLYING_SPEED, 0.60D)
                .add(Attributes.FOLLOW_RANGE, 48.0D)
                .add(Attributes.KNOCKBACK_RESISTANCE, 0.8D)
                .build());
    }
}
