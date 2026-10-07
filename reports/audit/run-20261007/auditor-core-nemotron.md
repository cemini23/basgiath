<!-- model=nvidia/nemotron-3-super-120b-a12b:free pack=pack-audit2-modcore usage={'prompt_tokens': 12271, 'completion_tokens': 12000, 'total_tokens': 24271, 'cost': 0, 'is_byok': False, 'prompt_tokens_details': {'cached_tokens': 0, 'cache_write_tokens': 0, 'audio_tokens': 0, 'video_tokens': 0}, 'cost_details': {'upstream_inference_cost': 0, 'upstream_inference_prompt_cost': 0, 'upstream_inference_completions_cost': 0}, 'completion_tokens_details': {'reasoning_tokens': 2499, 'image_tokens': 0, 'audio_tokens': 0}} -->

The cache is only valid for the current world because the anchor is summoned in the current world. If the world changes (e.g., the player travels to another world in a modded environment) then the anchor from the previous world would not be found in the current world (because the entity UUID would not exist in the current world) so the cache would be cleared (by setting to null) and a new search would be done.

    But wait: The method does:
        if (cachedAnchor != null) {
            Entity entity = level.getEntity(cachedAnchor);
            if (entity instanceof ArmorStand stand && stand.isAlive()) {
                return floor(stand);
            }
            cachedAnchor = null;
            cachedOrigin = null;
        }

    So if the entity is not found (returns null) or not an ArmorStand or not alive, it clears the cache and then does a search.

    Therefore, if the anchor from a previous build (in a different world) is not present in the current world, the cache will be cleared and a search will be done.

    However, what if the same world is reloaded? The anchor would be killed and re-summoned by the build function, so the UUID would change. The old UUID would not be found (because the old armor stand was killed) so the cache would be cleared and a new search would be done.

    Therefore, the cache does not serve a position from a previous build (because the anchor UUID changes on rebuild) and does not survive a world change (because the anchor from the other world isn't in the current world).

    But note: The cache is static and therefore persists across world loads in the same server run. However, the method has a safety check: if the cached anchor entity is not found or not valid, it clears the cache and searches. So it is safe.

    However, the question is: "Can that cache serve a position from a *previous* build, or survive a world change?"

    The answer is: It cannot serve a position from a previous build because the anchor UUID changes on rebuild (so the old UUID won't be found). And it cannot survive a world change in the sense of being valid for the wrong world because the entity lookup will fail (return null) and clear the cache.

    Therefore, the cache is safe and does not serve stale data.

    But note: The cache might serve a position from the current build that is still valid (if the anchor hasn't been killed and re-summoned). That is intended.

    So the verdict is: OK? However, let's read the question again: "Can that cache serve a position from a *previous* build, or survive a world change?"

    We have argued that it cannot. So the design is correct.

    However, note that the cache is cleared only when the anchor entity is not found or not valid. What if the anchor entity is still alive but the world has changed? That cannot happen because the anchor is tied to the world it was summoned in.

    Therefore, item 7 is OK.

 8. `BasgiathEvents.buildOrigin` searches a box around the player. Everything it guards — the dell stone and the two keeper lecterns — is within that box. Check the offsets in `BasgiathEvents.SIGNET_STONE` and `Keepers.ALL` against `SEARCH_RADIUS`.

    In `BasgiathEvents.java`:
        private static final int SEARCH_RADIUS = 320;

        public static final BlockPos SIGNET_STONE = new BlockPos(50, -1, 130);

    And in `Keepers.java` (which we don't have the full code for, but we can infer from the usage in `BasgiathEvents`):

        for (Keepers.Keeper keeper : Keepers.ALL) {
            if (pos.equals(origin.offset(keeper.offset()))) {
                ...
            }
        }

    We need to know the offsets of the keepers. Since we don't have the `Keepers` class, we must look for it in the provided files.

    The provided files do not include `Keepers.java`. However, note that the checklist says: "Answer the checklist below, item by item. Do not look for anything else." and we are only given the files that are listed.

    But wait: The `BasgiathEvents.java` file we have does reference `Keepers.ALL` and `keeper.offset()`. We must have the `Keepers` class to check the offsets.

    Since the `Keepers` class is not provided in the context, we cannot check the offsets. Therefore, we must say UNSURE for this item.

    However, note that the context says: "Two known-fixed bugs, so do not report them: a block id Java renames (`grass_path`), and relative coordinates inside a selector, which Java rejects." but that doesn't help.

    Without the `Keepers` class, we cannot verify the offsets.

    Therefore, item 8 is UNSURE.

 9. `BasgiathEvents.deny` calls `setCanceled(true)` and `setCancellationResult(SUCCESS)` on a `RightClickBlock`. On NeoForge 1.21.1, does that actually stop the block's own use — a lectern opening its page screen, say?

    In `BasgiathEvents.java`:
        private static void deny(PlayerInteractEvent.RightClickBlock event) {
            event.setUseBlock(TriState.FALSE);
            event.setUseItem(TriState.FALSE);
            event.setCanceled(true);
            event.setCancellationResult(InteractionResult.SUCCESS);
        }

    We are setting the event to canceled and the cancellation result to SUCCESS.

    In NeoForge, for `PlayerInteractEvent.RightClickBlock`, setting the event to canceled prevents the default action (which would be the block's use action, like opening a lectern) from occurring.

    Additionally, setting the cancellation result to SUCCESS tells the system that the event was handled successfully (so it doesn't fall back to the default action).

    Therefore, this should prevent the lectern from opening its page screen.

    However, note: The `setUseBlock` and `setUseItem` to FALSE are also set. These are used to control whether the block or item is used. Setting them to FALSE prevents the use action.

    So the combination should work.

    But let's check the NeoForge documentation for 1.21.1: The `PlayerInteractEvent.RightClickBlock` event, when canceled, prevents the block interaction. The `setCancellationResult` is used to indicate the result of the interaction (if canceled). Setting it to SUCCESS is appropriate.

    Therefore, item 9 is OK.

10. `BasgiathEvents.onRightClickItem` cancels the event and then opens a codex form.
    Is cancelling before opening correct, and does it work for a client that predicts?

    In `BasgiathEvents.java`:
        @SubscribeEvent
        public static void onRightClickItem(PlayerInteractEvent.RightClickItem event) {
            if (!(event.getEntity() instanceof ServerPlayer player)) {
                return;
            }
            ItemStack stack = event.getItemStack();
            if (stack.isEmpty()) {
                return;
            }
            Codices.Codex codex = Codices.forItem(stack.getItem());
            if (codex == null) {
                return;
            }
            event.setCanceled(true);
            event.setCancellationResult(InteractionResult.SUCCESS);
            BasgiathForms.CodexFlow.start(player, codex);
        }

    We cancel the event and set the result to SUCCESS, then we open the codex form.

    Canceling the event prevents the default item use action (which would be nothing for a codex? but note: the codex items are custom and might not have a default use action). However, it is safe to cancel.

    For client prediction: The client might predict the item use (like swinging the arm) but if the server cancels the event, the client will be corrected. However, opening a GUI (the codex form) is a server-side action that the client must be notified of. The mod uses a payload to open the form on the client.

    The cancellation on the server prevents the default action (if any) and then the server initiates the form opening. The client, having predicted the item use, will see the arm swing and then the form open (because the server sends the packet to open the form). This is standard and should work.

    Therefore, item 10 is OK.

11. `BasgiathCommands` registers `/basgiath vale`, which teleports via
    `player.server.getLevel(VALE)`. Is `teleportTo(ServerLevel, double, double, double, float, float)`
    the right call, and is the arrival position above the flat floor?

    In `BasgiathCommands.java`:
        player.teleportTo(vale, VALE_ARRIVAL.getX() + 0.5,
                VALE_ARRIVAL.getY(), VALE_ARRIVAL.getZ() + 0.5,
                player.getYRot(), player.getXRot());

    The `VALE_ARRIVAL` is defined as:
        private static final BlockPos VALE_ARRIVAL =
                new BlockPos(0, 7, 0);

    So the teleport call uses:
        x: 0 + 0.5 = 0.5
        y: 7
        z: 0 + 0.5 = 0.5

    The comment says: "Where a player lands when they step into the Vale. The flat floor tops out at y=6."

    So the floor is at y=6, and the player is teleported to y=7, which is above the floor (by 1 block). This is correct to avoid being inside the floor.

    The `teleportTo` method for a `ServerPlayer` with arguments (ServerLevel, double, double, double, float, float) is the correct method to teleport to a specific dimension and position.

    Therefore, item 11 is OK.

12. Any handler in these files that can throw and take a tick or an event down with it.

    We must look for any handler (method annotated with @SubscribeEvent or called by an event) that can throw an exception and is not caught.

    We are to look in the provided files.

    Let's go through each file:

    - `Basgiath.java`: 
        Constructor: 
            BasgiathContent.ENTITY_TYPES.register(modEventBus); ... 
            These are registry events and should not throw (but if they do, they are caught by the system?).
            modEventBus.addListener(BasgiathContent::onEntityAttributes); 
            modEventBus.addListener(this::onCommonSetup);
            NeoForge.EVENT_BUS.register(BasgiathEvents.class);
            ... 
        These are registrations and should not throw.

    - `BasgiathCommands.java`:
        onRegisterCommands: 
            event.getDispatcher().register(...) 
            This should not throw.

    - `BasgiathContent.java`:
        onEntityAttributes: 
            event.put(DRAGON.get(), DragonEntity.createAttributes() ...);
            This should not throw.

    - `BasgiathData.java`:
        No event handlers (the methods are static and not annotated with @SubscribeEvent).

    - `BasgiathEvents.java`:
        onRightClickBlock: 
            It does: 
                if (!(event.getEntity() instanceof ServerPlayer player) ... return;
                ... 
                BlockPos origin = buildOrigin(level, pos);
                ... 
            The `buildOrigin` method: 
                It uses a static cache and does a search. 
                It does not throw any checked exceptions. 
                It might throw a NullPointerException if `level` is null? But the event guarantees that if we are in the method, `level` is a ServerLevel (because we checked `event.getLevel() instanceof ServerLevel`). 
                However, note: the method `buildOrigin` is called with `level` and `pos` from the event. The event's `getLevel()` is checked to be ServerLevel, so `level` is non-null. 
                The search uses `level.getEntitiesOfClass` which should not throw.

            The `deny` method: 
                It sets some values on the event. Should not throw.

        onRightClickItem: 
            Similar checks and then `BasgiathForms.CodexFlow.start(player, codex);` 
            We don't have the code for `BasgiathForms`, but note: the checklist says we are only to look at the provided files. We don't have `BasgiathForms.java`. 
            However, the instruction says: "Do not look for anything else." meaning we should not look beyond the provided files. 
            But we are allowed to see if there is a throw in the provided files. Since we don't have the `BasgiathForms` code, we cannot know if `CodexFlow.start` throws. 
            However, note that the event handler itself does not throw: it only calls the method. If the method throws, it would propagate.

        onServerTick: 
            Keepers.tick(server); 
            FlightHud.tick(server); 
            Again, we don't have the code for `Keepers` or `FlightHud`, so we cannot know if they throw.

        onLogout: 
            BasgiathForms.forget(player); 
            Keepers.forget(player); 
            FlightHud.forget(player); 
            Same issue.

        onServerStopping: 
            forgetOrigin(); 
            This just sets two static fields to null. Should not throw.

    - `BasgiathNetwork.java`:
        onRegisterPayloads: 
            event.registrar("1") ... 
            Should not throw.

    - `BasgiathSmokeTest.java`:
        onServerStarted: 
            if (System.getProperty("basgiath.smoke") == null) { return; }
            try {
                run(server);
            } catch (RuntimeException error) { ... }
            ... 
        The `run` method: 
            It calls several methods that might throw. 
            For example: 
                checkEveryFunctionLoaded(server): 
                    It uses `server.getResourceManager().listResources` and then iterates. 
                    It might throw if the server is in a bad state? But unlikely.
                checkDragonAssets(): 
                    It uses `BasgiathSmokeTest.class.getResource` and `getResourceAsStream`. 
                    These can return null but do not throw. 
                    The JSON parsing might throw if the file is malformed? 
                    It is wrapped in a try-catch for Exception, so it catches and then calls `check` which does not throw.
                checkVale(server): 
                    It calls `server.getLevel` and then gets block states. 
                    Should not throw.
            Then it runs commands: 
                loudCommand and command: 
                    These call the command dispatcher. 
                    The command dispatcher can throw a `CommandSyntaxException` but note: 
                        In `loudCommand`: 
                            System.out.println ... 
                            source.getServer().getCommands().performPrefixedCommand(source, command);
                        This can throw a `CommandSyntaxException` (which is a checked exception) but the method does not catch it. 
                        However, note that the `onServerStarted` method catches `RuntimeException` and `CommandSyntaxException` is not a `RuntimeException` (it is a checked exception). 
                        Therefore, if a `CommandSyntaxException` is thrown, it will not be caught by the `catch (RuntimeException error)` and will propagate out of the `onServerStarted` method, which is an event handler.

            This means that if a command has a syntax error (which should not happen in the smoke test because we are using hardcoded strings) then an unchecked exception? Actually, `CommandSyntaxException` is a checked exception. 

            But note: the `performPrefixedCommand` method throws `CommandSyntaxException`. 

            Therefore, the `loudCommand` and `command` methods can throw a `CommandSyntaxException`. 

            Since the `onServerStarted` method only catches `RuntimeException`, a `CommandSyntaxException` would not be caught and would cause the event handler to throw, which would take down the tick or event.

        However, note that the smoke test is only run when the system property is set, and the commands used are fixed strings that are known to be valid. But in principle, if there was a typo in the command string, it would throw.

        But the checklist says: "Any handler in these files that can throw and take a tick or an event down with it."

        We have found a potential throw in `BasgiathSmokeTest` in the `loudCommand` and `command` methods (which are called from `run`). 

        However, note that the `onServerStarted` method is registered to handle `ServerStartedEvent`. If it throws, the event is not handled properly and the exception might be logged and the server might continue? But the exception is not caught by the event system.

        In NeoForge, if an event handler throws an exception, it is caught and logged, but the event processing continues for other handlers. However, the exception is still thrown and might cause the current thread to stop processing further events? Actually, the event bus catches exceptions and logs them, so the handler throwing does not break the event bus. But the handler itself did throw.

        The question is: "take a tick or an event down with it" meaning does it cause the tick or event to not be completed? 

        If the handler throws, then the rest of the handler is not run, but the event is considered handled (by the event bus) and the tick continues. 

        However, note that the `ServerStartedEvent` is fired once when the server starts. If the handler throws, the server start process might be affected? But the event is fired after the server has started.

        But the smoke test is designed to run and then halt the server. If it throws, it might not halt the server properly.

        However, the question is about any handler that can throw. We have found that the `loudCommand` and `command` methods in `BasgiathSmokeTest` can throw a `CommandSyntaxException` (if the command string is invalid). 

        Therefore, item 12 is WRONG because there is a handler (in `BasgiathSmokeTest`) that can throw.

        We must provide the file and line.

        The `loudCommand` method is in `BasgiathSmokeTest.java` at the line where it calls `performPrefixedCommand`. 

        Let's look at the provided `BasgiathSmokeTest.java`:

        private static void loudCommand(CommandSourceStack source, String command) {
            System.out.println("SMOKE  running [" + command + "]");
            source.getServer().getCommands().performPrefixedCommand(source, command);
        }

        The line that can throw is the call to `performPrefixedCommand`.

        We don't have the exact line number in the provided text, but we can count.

        However, note: the instructions say: "If you cannot point at a line, say so instead of guessing."

        We are given the entire file. We can count the lines.

        But note: the provided context is the entire file. We can assume that the line numbers are as in the provided block.

        Let me count the lines in `BasgiathSmokeTest.java` from the provided text:

        We'll write a temporary count:

        ... (we don't need to count every line, we can find the method)

        The method `loudCommand` starts at:

        private static void loudCommand(CommandSourceStack source, String command) {
            System.out.println("SMOKE  running [" + command + "]");
            source.getServer().getCommands().performPrefixedCommand(source, command);
        }

        In the provided text, we see:

        private static void loudCommand(CommandSourceStack source, String command) {
            System.out.println("SMOKE  running [" + command + "]");
            source.getServer().getCommands().performPrefixedCommand(source, command);
        }

        This is three lines. The throw can happen on the third line.

        However, to be precise, we note that the line number in the provided file block is not given. But we can say the file is `BasgiathSmokeTest.java` and the line is the one containing the call to `performPrefixedCommand`.

        Since we are not given line numbers in the context, we must rely on the fact that the evaluator has the file and can count.

        Alternatively, we can note that the method is near the end of the file.

        But the instructions say: "Evidence (file:line)". We must provide a line number.

        Let's count the lines in the provided `BasgiathSmokeTest.java` block:

        We'll copy the provided text and count.

        However, note: the evaluator has the exact file. We can approximate.

        Since we cannot be sure of the exact line number without the file, and the instructions say if we cannot point at a line say so, we must say UNSURE for the line? 

        But wait: we know the method and we know the line within the method. We can give the line number relative to the method? 

        The instructions do not specify. We must provide the absolute line number in the file.

        Given that we are not provided with line numbers in the context, and the file is long, we cannot accurately count.

        Therefore, we must say that we cannot point at a line? 

        However, note: the checklist item 12 is about any handler in these files. We have identified that the handler `onServerStarted` in `BasgiathSmokeTest` can throw because it calls `loudCommand` which can throw. 

        We can say the file is `BasgiathSmokeTest.java` and the method is `loudCommand` (or `onServerStarted` via `loudCommand`). 

        But the instructions require a line.

        Alternatively, we can look for the line in the provided text block by counting the lines we are given.

        Let me try to count the lines in the provided `BasgiathSmokeTest.java`:

        The provided text for `BasgiathSmokeTest.java` starts at:

        ```
        package com.basgiath;

        import java.util.List;
        import java.util.Optional;

        import net.minecraft.commands.CommandSourceStack;
        import net.minecraft.core.BlockPos;
        import net.minecraft.resources.ResourceLocation;
        import net.minecraft.server.MinecraftServer;
        import net.minecraft.server.level.ServerLevel;
        import net.minecraft.world.entity.Entity;
        import net.minecraft.world.entity.EntityType;
        import net.minecraft.world.entity.decoration.ArmorStand;
        import net.minecraft.world.level.block.Blocks;
        import net.neoforged.bus.api.SubscribeEvent;
        import net.neoforged.neoforge.event.server.ServerStartedEvent;
        ```

        and ends at:

        ```
            }
        }
        ```

        We can count the lines in this block.

        However, note: the evaluator has the exact same file? We are to use the provided context.

        Since we are in a simulated environment, I will assume that the line numbers are as in the provided block and count accordingly.

        Let me count:

        1: package com.basgiath;
        2: 
        3: import java.util.List;
        4: import java.util.Optional;
        5: 
        6: import net.minecraft.commands.CommandSourceStack;
        7: import net.minecraft.core.BlockPos;
        8: import net.minecraft.resources.ResourceLocation;
        9: import net.minecraft.server.MinecraftServer;
        10: import net.minecraft.server.level.ServerLevel;
        11: import net.minecraft.world.entity.Entity;
        12: import net.minecraft.world.entity.EntityType;
        13: import net.minecraft.world.entity.decoration.ArmorStand;
        14: import net.minecraft.world.level.block.Blocks;
        15: import net.neoforged.bus.api.SubscribeEvent;
        16: import net.neoforged.neoforge.event.server.ServerStartedEvent;
        17: 
        18: /**
        19:  * A headless check that the port actually works.
        20:  *
        21:  * <p>The prompt asks for two things to be confirmed on the first Java world:
        22:  * {@code /function basgiath:build} raises the college, and one summonable dragon
        23:  * exists. Neither can be confirmed by reading code, and a dedicated server has no
        24:  * player to run the build from, so this class drives the machine directly.
        25:  *
        26:  * <p>It runs only when the {@code basgiath.smoke} system property is set, which the
        27:  * {@code smoke} run config in build.gradle sets. It writes a pass or fail line per
        28:  * check, then stops the server, so it is usable from a shell and from CI.
        29:  *
        30:  * <p>What it proves: the generated Java datapack parses and executes, every stage
        31:  * places the blocks the generator intended, and the dragon entity type is
        32:  * registered and summonable. What it does not prove: anything that needs a client,
        33:  * which is the screens and the renderer.
        34:  */
        35: public final class BasgiathSmokeTest {
        36: 
        37:  private BasgiathSmokeTest() {}
        38: 
        39:  /**
        40:   * Where the college is raised for this run.
        41:   *
        42:   * <p>It has to sit in a loaded chunk, or the anchor is summoned into a place the
        43:   * server is not tracking and every stage finds nothing to move. The world spawn
        44:   * is the one position guaranteed to be loaded on a fresh dedicated server.
        45:   */
        46:  private static BlockPos ANCHOR = new BlockPos(0, 64, 0);
        47: 
        48:  private static int passed;
        49:  private static int failed;
        50: 
        51:  private static void check(String name, boolean ok, String detail) {
        52:      if (ok) {
        53:          passed += 1;
        54:          System.out.println("SMOKE PASS  " + name);
        55:      } else {
        56:          failed += 1;
        57:          System.out.println("SMOKE FAIL  " + name + " :: " + detail);
        58:      }
        59:  }
        60: 
        61:  @SubscribeEvent
        62:  public static void onServerStarted(ServerStartedEvent event) {
        63:      if (System.getProperty("basgiath.smoke") == null) {
        64:          return;
        65:      }
        66:      MinecraftServer server = event.getServer();
        67:      try {
        68:          run(server);
        69:      } catch (RuntimeException error) {
        70:          failed += 1;
        71:          System.out.println("SMOKE FAIL  the smoke test threw :: " + error);
        72:          error.printStackTrace(System.out);
        73:      } finally {
        74:          System.out.println("SMOKE RESULT  passed=" + passed + " failed=" + failed);
        75:          server.halt(false);
        76:      }
        77:  }
        78: 
        79:  /**
        80:   * Every function the generator wrote has to have loaded.
        81:   *
        82:   * <p>A function that fails to parse does not warn and does not half-load: it is
        83:   * dropped, and every call to it quietly does nothing. That is how both of this
        84:   * port's generation bugs showed up — a block id Java had renamed, and a relative
        85:   * selector coordinate Java refuses. Neither was visible on the Bedrock side, and
        86:   * neither would have been visible here without this check.
        87:   *
        88:   * <p>So the check compares what is on disk with what the game actually loaded,
        89:   * rather than trusting that a build that produced no errors is a build that runs.
        90:   */
        91:  private static void checkEveryFunctionLoaded(MinecraftServer server) {
        92:      final String prefix = "function/";
        93:      final String suffix = ".mcfunction";
        94:      // The path here is relative to the data root, and each hit already carries the
        95:      // namespace, so `function/build.mcfunction` arrives as
        96:      // `basgiath:function/build.mcfunction`.
        97:      var onDisk = server.getResourceManager().listResources(
        98:              "function",
        99:              location -> location.getNamespace().equals(Basgiath.MOD_ID)
        100:                     && location.getPath().endsWith(suffix));
        101: 
        102:      List<String> missing = new java.util.ArrayList<>();
        103:      for (ResourceLocation location : onDisk.keySet()) {
        104:          String path = location.getPath();
        105:          String name = path.substring(prefix.length(), path.length() - suffix.length());
        106:          ResourceLocation id = ResourceLocation.fromNamespaceAndPath(Basgiath.MOD_ID, name);
        107:          if (server.getFunctions().get(id).isEmpty()) {
        108:              missing.add(name);
        109:          }
        110:      }
        111:      for (String name : missing) {
        112:          System.out.println("SMOKE    did not load: " + name);
        113:      }
        114:      check("every generated function loaded (" + onDisk.size() + " on disk)",
        115:              onDisk.size() > 0 && missing.isEmpty(),
        116:              missing.size() + " of " + onDisk.size() + " functions failed to load");
        117:  }
        118: 
        119:  /**
        120:   * The dragon's three assets are present, and the animations it asks for exist.
        121:   *
        122:   * <p>GeckoLib keys its baked animations on the animation file's own JSON key and
        123:   * looks them up with a plain map get. A mismatch is not an error: the model just
        124:   * never moves. That is invisible on a dedicated server and easy to miss on a
        125:   * client, so the two names are checked against the file here.
        126:   */
        127:  private static void checkDragonAssets() {
        128:      String animationPath = "/assets/" + Basgiath.MOD_ID
        129:              + "/animations/entity/dragon.animation.json";
        130:      String geoPath = "/assets/" + Basgiath.MOD_ID + "/geo/entity/dragon.geo.json";
        131:      String texturePath = "/assets/" + Basgiath.MOD_ID + "/textures/entity/dragon.png";
        132: 
        133:      for (String path : new String[]{animationPath, geoPath, texturePath}) {
        134:          check("the dragon asset " + path.substring(path.lastIndexOf('/') + 1) + " ships",
        135:                  BasgiathSmokeTest.class.getResource(path) != null,
        136:                  "not on the classpath: " + path);
        137:      }
        138: 
        139:      try (var stream = BasgiathSmokeTest.class.getResourceAsStream(animationPath)) {
        140:          if (stream == null) {
        141:              return;
        142:          }
        143:          var root = com.google.gson.JsonParser.parseString(
        144:                  new String(stream.readAllBytes(), java.nio.charset.StandardCharsets.UTF_8))
        145:                  .getAsJsonObject();
        146:          var animations = root.getAsJsonObject("animations");
        147:          for (String wanted : new String[]{
        148:                  DragonEntity.IDLE_ANIMATION, DragonEntity.FLY_ANIMATION}) {
        149:              check("the dragon animation " + wanted + " exists in the file",
        150:                      animations != null && animations.has(wanted),
        151:                      "the entity asks for it but the animation file has key set "
        152:                              + (animations == null ? "<no animations block>"
        153:                                      : animations.keySet().toString()));
        154:          }
        155:      } catch (Exception error) {
        156:          check("the dragon animation file is readable", false, String.valueOf(error));
        157:      }
        158:  }
        159: 
        160:  /**
        161:   * The Vale, the Java-only dimension.
        162:   *
        163:   * <p>Dimension data that parses but registers wrong does not throw: the level is
        164:   * simply absent, and {@code /basgiath vale} is the only thing that would ever say
        165:   * so. This asks the server for the level by key and then reads a block out of it,
        166:   * which is the only way to tell the generator ran.
        167:   */
        168:  private static void checkVale(MinecraftServer server) {
        169:      ServerLevel vale = server.getLevel(BasgiathCommands.VALE);
        170:      check("the Vale dimension is registered", vale != null,
        171:              "basgiath:vale is not a loaded level; the dimension data did not take");
        172:      if (vale == null) {
        173:          return;
        174:      }
        175:      // The flat layers top out at y=6: bedrock, stone x3, dirt x2, grass_block.
        176:      var surface = vale.getBlockState(new BlockPos(0, 6, 0));
        177:      check("the Vale floor is the flat preset's surface",
        178:              surface.is(Blocks.GRASS_BLOCK),
        179:              "expected grass_block at 0,6,0 in the Vale, found " + surface.getBlock());
        180:      // The fixed time lives on the dimension type, not on the level clock. A
        181:      // non-overworld level mirrors the overworld's day time, so reading
        182:      // getDayTime() here would report the overworld's clock and say nothing about
        183:      // this dimension at all.
        184:      check("the Vale holds a fixed midnight",
        185:              vale.dimensionType().fixedTime().orElse(-1L) == 18000L,
        186:              "the dimension type fixes time at "
        187:                      + vale.dimensionType().fixedTime() + ", not 18000");
        188:  }
        189: 
        190:  private static void run(MinecraftServer server) {
        191:      ServerLevel level = server.overworld();
        192:      ANCHOR = level.getSharedSpawnPos().above(2);
        193:      System.out.println("SMOKE  building at " + ANCHOR);
        194:      checkEveryFunctionLoaded(server);
        195:      checkDragonAssets();
        196:      checkVale(server);
        197:      // Not suppressed: a command that fails says why in the log, and a silent
        198:      // failure is exactly what this test exists to catch.
        199:      CommandSourceStack source = server.createCommandSourceStack();
        200: 
        201:      // 1. The datapack loaded, and its functions are reachable by namespaced id.
        202:      Optional<?> build = server.getFunctions().get(
        203:              ResourceLocation.fromNamespaceAndPath(Basgiath.MOD_ID, "build"));
        204:      check("the datapack registers basgiath:build", build.isPresent(),
        205:              "basgiath:build is not in the function manager");
        206: 
        207:      // 2. The anchor the generator builds around.
        208:      loudCommand(source, "kill @e[type=minecraft:armor_stand,name=\"build_anchor\"]");
        209:      loudCommand(source, "summon minecraft:armor_stand " + ANCHOR.getX() + " " + ANCHOR.getY()
        210:              + " " + ANCHOR.getZ() + " {CustomName:'{\"text\":\"build_anchor\"}',NoGravity:1b}");
        211: 
        212:      var stands = level.getEntitiesOfClass(ArmorStand.class,
        213:              new net.minecraft.world.phys.AABB(ANCHOR).inflate(16),
        214:              stand -> true);
        215:      System.out.println("SMOKE  armor stands within 16 blocks: " + stands.size());
        216:      for (ArmorStand stand : stands) {
        217:          System.out.println("SMOKE    at " + stand.blockPosition() + " name="
        218:                  + (stand.hasCustomName() ? stand.getCustomName().getString() : "<none>"));
        219:      }
        220:      ArmorStand anchor = stands.stream()
        221:              .filter(stand -> stand.hasCustomName()
        222:                      && BasgiathEvents.BUILD_ANCHOR.equals(stand.getCustomName().getString()))
        223:              .findFirst().orElse(null);
        224:      check("the build anchor exists", anchor != null, "no armor stand named build_anchor");
        225: 
        226:      // 3. Every stage the generator wrote runs. The stage list is discovered rather
        227:      // 228:      // than hardcoded, so a change to the generator cannot silently skip one.
        229:      int stages = 0;
        230:      for (int index = 1; index <= 256; index++) {
        231:          String name = String.format("stage_%02d", index);
        232:          if (server.getFunctions().get(
        233:                  ResourceLocation.fromNamespaceAndPath(Basgiath.MOD_ID, name)).isEmpty()) {
        234:              break;
        235:          }
        236:          stages += 1;
        237:          command(source, "execute as @e[type=minecraft:armor_stand,name=\"build_anchor\",limit=1]"
        238:                  + " at @s run function " + Basgiath.MOD_ID + ":" + name);
        239:      }
        240:      check("the generator wrote more than one stage", stages > 1, "only " + stages + " stages");
        241: 
        242:      // 4. The stages placed what the generator meant. finish() puts a stone pressure
        243:      // 244:      // plate at anchor + (5, DECK_Y + 1, SPAN_Z); if the stages ran, it is there.
        245:      BlockPos plate = ANCHOR.offset(5, 33, 20);
        246:      check("a stage placed the west span plate",
        247:              level.getBlockState(plate).is(Blocks.STONE_PRESSURE_PLATE),
        248:              "expected a stone pressure plate at " + plate + ", found "
        249:                      + level.getBlockState(plate).getBlock());
        250: 
        251:      // The span deck itself: two blocks are cut out of it on purpose, so the middle
        252:      // 253:      // is air and the rest is not.
        254:      BlockPos deck = ANCHOR.offset(20, 32, 20);
        255:      check("the span deck is solid where it should be",
        256:              !level.getBlockState(deck).isAir(),
        257:              "expected the deck at " + deck + " to be built, found air");
        258: 
        259:      // 5. The dragon. This is the entity the
