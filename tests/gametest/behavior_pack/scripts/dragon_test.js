import * as GameTest from "@minecraft/server-gametest";

// The dragon is a mount. The shipped behavior pack gives it a one-seat
// minecraft:rideable whose seat 0 controls it, so a mounted player steers it.
// This test spawns the dragon in a small test pad and checks those facts.
//
// What it cannot check, and why: the script API binds only some entity
// components. minecraft:input_air_controlled -- the flight-control component
// the dragon carries -- is not one of them, so Entity.getComponent and
// GameTest's assertEntityHasComponent both report it as missing on a dragon
// that really has it. Asserting it here would make the test fail for the wrong
// reason. Flight still needs a human on a client; the README says so.
const AT = { x: 2, y: 2, z: 2 };
const DRAGON = "dragon_rider:dragon";

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

  test.succeed();
}).maxTicks(200);
