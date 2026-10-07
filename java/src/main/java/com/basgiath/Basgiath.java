package com.basgiath;

import org.slf4j.Logger;

import com.mojang.logging.LogUtils;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.ModContainer;
import net.neoforged.fml.common.Mod;
import net.neoforged.fml.event.lifecycle.FMLCommonSetupEvent;
import net.neoforged.neoforge.common.NeoForge;

/**
 * Entry point for the Basgiath Java port.
 *
 * <p>The map itself is not built here. {@code scripts/build_map.py} writes the
 * datapack, this mod ships it, and {@code /function basgiath:build} raises the
 * college at run time. The mod supplies what a datapack cannot: the dragon entity,
 * the vault desk, and the screens.
 *
 * <p>See {@code docs/JAVA-PORT-PROMPT.md} for the task ladder, and
 * {@code docs/IP-RULES.md} for the naming rules that every shipped string respects.
 */
@Mod(Basgiath.MOD_ID)
public final class Basgiath {

    /** The mod id. Must match the {@code modId} entry in neoforge.mods.toml. */
    public static final String MOD_ID = "basgiath";

    private static final Logger LOGGER = LogUtils.getLogger();

    public Basgiath(IEventBus modEventBus, ModContainer modContainer) {
        BasgiathContent.ENTITY_TYPES.register(modEventBus);
        BasgiathContent.BLOCKS.register(modEventBus);
        BasgiathContent.ITEMS.register(modEventBus);
        BasgiathContent.TABS.register(modEventBus);
        BasgiathData.ATTACHMENTS.register(modEventBus);

        modEventBus.addListener(BasgiathContent::onEntityAttributes);
        modEventBus.addListener(this::onCommonSetup);

        // Game events, not mod events. These are the Bedrock script's old jobs.
        // Registered by class, which picks up the static handlers, and by name so it
        // is obvious which bus each one lands on. Nothing here relies on the loader
        // guessing a bus.
        NeoForge.EVENT_BUS.register(BasgiathEvents.class);
        NeoForge.EVENT_BUS.register(BasgiathCommands.class);
        NeoForge.EVENT_BUS.register(BasgiathSmokeTest.class);
    }

    private void onCommonSetup(FMLCommonSetupEvent event) {
        LOGGER.info("{} loaded", MOD_ID);
    }
}
