import * as GameTest from "@minecraft/server-gametest";

// The dragon is a mount. The shipped behavior pack gives it a one-seat
// minecraft:rideable whose seat 0 controls it, so a mounted player steers it.
// This test spawns the dragon on a small test pad, stands a simulated cadet
// beside it, and only passes after the dragon has ticked for a second: a
// dragon that dies as it ticks, or loses its seat, fails here instead of
// reading green the instant it spawned.
//
// What it cannot check, and why: the script API binds only some entity
// components. minecraft:input_air_controlled -- the flight-control component
// the dragon carries -- is not one of them, so Entity.getComponent and
// GameTest's assertEntityHasComponent both report it as missing on a dragon
// that really has it. Asserting it here would make the test fail for the wrong
// reason. Flight still needs a human on a client; the README says so.
const AT = { x: 2, y: 2, z: 2 };
const CADET = { x: 1, y: 1, z: 1 };
const DRAGON = "dragon_rider:dragon";
const SETTLE_TICKS = 20;

GameTest.register("basgiath", "dragon_rides", (test) => {
  const dragon = test.spawn(DRAGON, AT);

  // 1. The entity exists after the spawn.
  test.assertEntityPresent(DRAGON, AT, 3, true);

  // 2. A cadet can mount it.
  const ride = dragon.getComponent("minecraft:rideable");
  test.assert(ride !== undefined, "the dragon has no minecraft:rideable component");

  // 3. The rider controls it: exactly one seat, and that seat is the
  //    controlling seat. (EntityRideableComponent.familyTypes is not present
  //    in this API build, so the allowed rider family is not asserted.)
  test.assert(ride.seatCount === 1, `the dragon has ${ride.seatCount} seats, not 1`);
  test.assert(ride.controllingSeat === 0, "seat 0 does not control the dragon");

  // 4. A cadet stands on the pad. The test waits, then re-checks, so it proves
  //    the mount survives its own ticks rather than only the spawn tick.
  test.spawnSimulatedPlayer(CADET, "cadet");
  test.runAfterDelay(SETTLE_TICKS, () => {
    test.assertEntityPresent(DRAGON, AT, 3, true);
    const settled = dragon.getComponent("minecraft:rideable");
    test.assert(settled !== undefined, "the dragon lost its rideable component after ticking");
    test.assert(settled.seatCount === 1, "the dragon lost its seat after ticking");
    test.assert(settled.controllingSeat === 0, "the dragon stopped being steerable after ticking");
    test.succeed();
  });
}).maxTicks(200);
