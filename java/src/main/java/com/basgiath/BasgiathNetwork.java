package com.basgiath;

import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.fml.loading.FMLEnvironment;
import net.neoforged.neoforge.network.event.RegisterPayloadHandlersEvent;
import net.neoforged.neoforge.network.handling.IPayloadContext;

/**
 * The two payloads the forms travel on.
 *
 * <p>{@code RegisterPayloadHandlersEvent} is a mod-bus event, which is the default
 * bus for {@code @EventBusSubscriber}, so this class needs no bus argument.
 */
@EventBusSubscriber(modid = Basgiath.MOD_ID)
public final class BasgiathNetwork {

    private BasgiathNetwork() {}

    @SubscribeEvent
    public static void onRegisterPayloads(RegisterPayloadHandlersEvent event) {
        var registrar = event.registrar("1");
        registrar.playToClient(BasgiathForms.OpenForm.TYPE, BasgiathForms.OpenForm.CODEC,
                BasgiathNetwork::handleOpenForm);
        registrar.playToServer(BasgiathForms.FormAnswer.TYPE, BasgiathForms.FormAnswer.CODEC,
                BasgiathEvents::handleFormAnswer);
    }

    private static void handleOpenForm(BasgiathForms.OpenForm payload, IPayloadContext context) {
        // The client class is referenced only inside this branch, so a dedicated
        // server never loads it. The dist guard is what keeps that true.
        if (FMLEnvironment.dist == Dist.CLIENT) {
            BasgiathClient.openForm(payload);
        }
    }
}
