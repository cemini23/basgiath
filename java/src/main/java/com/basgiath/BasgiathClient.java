package com.basgiath;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.components.EditBox;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.client.renderer.entity.EntityRendererProvider;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.client.event.EntityRenderersEvent;
import net.neoforged.neoforge.network.PacketDistributor;

import software.bernie.geckolib.model.DefaultedEntityGeoModel;
import software.bernie.geckolib.renderer.GeoEntityRenderer;

/**
 * The Java client: the forms the Bedrock script showed, and the dragon's renderer.
 *
 * <p>This class is loaded on the client only. The guard in
 * {@link BasgiathEvents#handleOpenForm} is what keeps a dedicated server from ever
 * touching it.
 */
@EventBusSubscriber(modid = Basgiath.MOD_ID, value = Dist.CLIENT)
public final class BasgiathClient {

    private BasgiathClient() {}

    public static void openForm(BasgiathForms.OpenForm form) {
        Minecraft.getInstance().setScreen(new FormScreen(form));
    }

    /**
     * Say so when the client side is up.
     *
     * <p>A client-side failure — a renderer registered against nothing, a model layer
     * that will not bake — takes the game down at startup, and nothing on a dedicated
     * server can see it. CI starts the client under a virtual display and waits for
     * this line. If it never appears, the client died and the log says where.
     */
    @SubscribeEvent
    public static void onClientSetup(
            net.neoforged.fml.event.lifecycle.FMLClientSetupEvent event) {
        com.mojang.logging.LogUtils.getLogger().info("BASGIATH CLIENT READY");
    }

    /**
     * The dragon's renderer.
     *
     * <p>GeckoLib draws it, from the Bedrock geometry and animation files the pack
     * already ships. {@link DefaultedEntityGeoModel} takes the entity id and derives
     * the three resource paths from it, which is why the assets sit at
     * {@code geo/entity/dragon.geo.json}, {@code animations/entity/dragon.animation.json},
     * and {@code textures/entity/dragon.png}. GeckoLib supplies its own model layer,
     * so nothing is baked here.
     */
    @SubscribeEvent
    public static void onRegisterRenderers(EntityRenderersEvent.RegisterRenderers event) {
        event.registerEntityRenderer(BasgiathContent.DRAGON.get(), DragonRenderer::new);
    }

    private static final class DragonRenderer extends GeoEntityRenderer<DragonEntity> {
        DragonRenderer(EntityRendererProvider.Context context) {
            super(context, new DefaultedEntityGeoModel<>(
                    ResourceLocation.fromNamespaceAndPath(Basgiath.MOD_ID, "dragon")));
        }
    }

    /**
     * One form. The Bedrock script had four kinds; they all reduce to a title, a
     * body, and either a row of buttons or a single text field.
     */
    private static final class FormScreen extends Screen {

        private static final int MAX_WIDTH = 320;

        private final BasgiathForms.OpenForm form;
        private EditBox textField;
        private boolean answered;

        FormScreen(BasgiathForms.OpenForm form) {
            super(Component.literal(form.title()));
            this.form = form;
        }

        @Override
        protected void init() {
            int centre = this.width / 2;
            int boxWidth = Math.min(MAX_WIDTH, this.width - 40);

            if (form.kind() == BasgiathForms.Kind.TEXT.ordinal()) {
                textField = new EditBox(this.font, centre - boxWidth / 2, this.height / 2 + 20,
                        boxWidth, 20, Component.literal("a name"));
                textField.setMaxLength(16);
                addRenderableWidget(textField);
                setInitialFocus(textField);

                addRenderableWidget(Button.builder(Component.literal("Confirm"),
                                button -> send(0, textField.getValue()))
                        .bounds(centre - boxWidth / 2, this.height / 2 + 48, boxWidth / 2 - 2, 20).build());
                addRenderableWidget(Button.builder(Component.literal("Cancel"),
                                button -> send(BasgiathForms.FormAnswer.CANCELED, ""))
                        .bounds(centre + 2, this.height / 2 + 48, boxWidth / 2 - 2, 20).build());
                return;
            }

            // A choice. The buttons stack from just under the body text.
            int count = form.options().size();
            int top = bodyTop() + bodyHeight() + 12;
            for (int index = 0; index < count; index++) {
                int position = index;
                addRenderableWidget(Button.builder(Component.literal(form.options().get(index)),
                                button -> send(position, ""))
                        .bounds(centre - boxWidth / 2, top + index * 24, boxWidth, 20).build());
            }
        }

        private int bodyTop() {
            return Math.max(40, this.height / 2 - 80);
        }

        private int bodyHeight() {
            return this.font.lineHeight * bodyLines().length;
        }

        private String[] bodyLines() {
            return form.body().isEmpty() ? new String[0] : form.body().split("\n", -1);
        }

        private void send(int selection, String text) {
            answered = true;
            PacketDistributor.sendToServer(
                    new BasgiathForms.FormAnswer(form.formId(), selection, text));
            super.onClose();
        }

        @Override
        public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
            super.render(graphics, mouseX, mouseY, partialTick);
            int centre = this.width / 2;
            graphics.drawCenteredString(this.font, this.title, centre, bodyTop() - 24, 0xFFD070);

            String[] lines = bodyLines();
            int y = bodyTop();
            for (String line : lines) {
                graphics.drawCenteredString(this.font, Component.literal(line), centre, y, 0xE0E0E0);
                y += this.font.lineHeight;
            }
        }

        @Override
        public void onClose() {
            // Closing without answering drops the flow, the same as a cancelled
            // Bedrock form. An answered form has already sent, so it must not send
            // a second, cancelling message behind itself.
            if (!answered) {
                answered = true;
                PacketDistributor.sendToServer(new BasgiathForms.FormAnswer(
                        form.formId(), BasgiathForms.FormAnswer.CANCELED, ""));
            }
            super.onClose();
        }

        @Override
        public boolean isPauseScreen() {
            return false;
        }
    }
}
