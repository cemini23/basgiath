// Dragon Rider Map — the signet form and the two keepers.
// Target: Minecraft Bedrock 26.x, @minecraft/server 2.x
//
// Trigger: interact with a lodestone (the "Bonding Stone") after the bond.
//          Canon puts the signet weeks after a dragon chooses the rider,
//          so the form opens only for a player with the "bonded" tag.
//          Threshing sets that tag (and the bg_bond score) when a dragon
//          chooses the player. This script only reads the tag.
//          Interact with either keeper lectern and the keeper opens a form:
//          the Scroll-keeper takes the rider's name, the Roll-keeper takes the
//          dragon's full name. Names live on the player as dynamic properties.
// Test:    /scriptevent dragon_rider:signet
//          /scriptevent dragon_rider:rider_name
//          /scriptevent dragon_rider:dragon_name
//
// Original archetypes only. Do not replace these with the book's signets.

import { world, system } from "@minecraft/server";
import { ActionFormData, MessageFormData, ModalFormData } from "@minecraft/server-ui";

const BONDING_BLOCK = "minecraft:lodestone";
const SIGNET_PROPERTY = "dragon_rider:signet";
const TEST_EVENT = "dragon_rider:signet";
const BOND_TAG = "bonded";
const NO_BOND_LINE = "§7A signet comes after a dragon chooses you.";

// The two naming beats. A keeper only writes the rider's own name onto the
// rider. No name is ever read back into a command string.
const LECTERN_BLOCK = "minecraft:lectern";
const RIDER_PROPERTY = "dragon_rider:rider_name";
const DRAGON_PROPERTY = "dragon_rider:dragon_name";
const ROLLCALL_TAG = "rollcall_done";
const BUILD_ANCHOR = "build_anchor";

const QUESTIONS = [
  {
    body: "A dragon circles overhead. What do you do?",
    choices: [
      { text: "Stand your ground.", signet: "stone" },
      { text: "Go still. Go quiet.", signet: "shadow" },
      { text: "Reach out your hand.", signet: "ember" },
      { text: "Read the wind.", signet: "storm" },
    ],
  },
  {
    body: "The Parapet sways under your boots. What carries you across?",
    choices: [
      { text: "Rage.", signet: "ember" },
      { text: "Discipline.", signet: "storm" },
      { text: "Silence.", signet: "shadow" },
      { text: "Patience.", signet: "stone" },
    ],
  },
  {
    body: "Your wing is losing. What do you change?",
    choices: [
      { text: "The weather.", signet: "storm" },
      { text: "The ground.", signet: "stone" },
      { text: "The dark.", signet: "shadow" },
      { text: "The odds.", signet: "ember" },
    ],
  },
];

const SIGNETS = {
  storm: { name: "Stormcaller", line: "The air answers before you speak." },
  shadow: { name: "Shadowwalker", line: "You are hardest to find when it matters." },
  ember: { name: "Emberwright", line: "You reach first and ask later." },
  stone: { name: "Stoneward", line: "Nothing moves you that you did not choose." },
};

function blankScores() {
  return { storm: 0, shadow: 0, ember: 0, stone: 0 };
}

// The Scroll-keeper holds the roll desk lectern in the Quad courtyard. The
// Roll-keeper holds the lectern one block north of the armor stand in the
// dell. The block is the key: it names the keeper and the property to write.
// The coordinates are the build's own: the generator wraps every stage in
// `execute as @e[type=armor_stand,name="build_anchor",c=1] at @s`, so a
// setblock lands at anchor + relative. The absolute block location is therefore
// floor(anchor) + relative, which is what buildOrigin() resolves.
const KEEPERS = [
  {
    id: "scroll",
    block: { x: 128, y: 1, z: 34 },
    property: RIDER_PROPERTY,
    needTag: null,
    title: "The scroll",
    ask: "The scribe waits. Give your name.",
    refusal: null,
  },
  {
    id: "roll",
    block: { x: 50, y: -1, z: 123 },
    property: DRAGON_PROPERTY,
    needTag: BOND_TAG,
    title: "The roll",
    ask: "Give the name of the one that chose you.",
    refusal: "§7A name comes after a dragon chooses you.",
  },
];

// The generator stamps the college around an armor stand named "build_anchor"
// at the player's feet, and every stage command is anchor-relative. The anchor
// is killed and re-summoned by `build_text` when the build runs again, so the
// origin is resolved fresh on every interact rather than cached: an event
// handler runs on a click, where one getEntities call is cheap, and a stale
// cached origin would point at the previous build. Math.floor is required
// because a block command floors its position: an anchor at x = 8.5 puts ~128
// at block 136, not 136.5.
function buildOrigin() {
  const dim = world.getDimension("overworld");
  for (const e of dim.getEntities({ type: "minecraft:armor_stand" })) {
    if (e.nameTag === BUILD_ANCHOR) {
      return {
        x: Math.floor(e.location.x),
        y: Math.floor(e.location.y),
        z: Math.floor(e.location.z),
      };
    }
  }
  return null;
}

function cleanName(raw) {
  if (typeof raw !== "string") return "";
  let s = raw
    .replace(/§./g, "")
    .replace(/[\u0000-\u001f\u007f]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  if (s.length > 16) s = s.slice(0, 16);
  return s;
}

// The roll call is the rider's own name, read from a dynamic property. A
// command cannot read a dynamic property, so the read lives here. The name is
// player input, so it reaches the world through world.sendMessage, which does
// not parse: it can never become a command injection. cleanName already
// stripped colour codes and control characters before the name was stored.
// A rider who leaves inside the three-second beat misses the call. Talking to
// the keeper again clears the tag and reads the roll again, so it self-heals;
// a catch-up loop would only add a reason for the tag to go stale.
function readRollCall(player) {
  const name = player.getDynamicProperty(RIDER_PROPERTY);
  if (typeof name !== "string" || !name) return;
  if (player.hasTag(ROLLCALL_TAG)) return;
  player.addTag(ROLLCALL_TAG);
  world.sendMessage(`§7Roll call. §f${name}§7 answers and takes their place.`);
}

// One pending roll call per player. A second name write inside the 60-tick beat
// cancels the first callback, so two quick writes cannot leave two live reads
// chasing the same player. system.clearRunTimeout is stable in @minecraft/server
// 2.0.0. player.id is stable across a rename; player.name is not.
const rollCallTimeouts = new Map();

function scheduleRollCall(player) {
  const key = player.id;
  const prior = rollCallTimeouts.get(key);
  if (prior !== undefined) {
    try {
      system.clearRunTimeout(prior);
    } catch (e) {
      // The handle already fired or the engine dropped it. Either way there is
      // nothing left to cancel.
    }
  }
  const handle = system.runTimeout(() => {
    rollCallTimeouts.delete(key);
    readRollCall(player);
  }, 60);
  rollCallTimeouts.set(key, handle);
}

async function runKeeperForm(player, keeper) {
  if (keeper.needTag && !player.hasTag(keeper.needTag)) {
    player.sendMessage(keeper.refusal);
    return;
  }

  const form = new ModalFormData()
    .title(keeper.title)
    .textField(keeper.ask, "a name");

  const response = await form.show(player);
  if (response.canceled) return;

  const values = response.formValues ?? [];
  const name = cleanName(values[0]);
  if (!name) {
    player.sendMessage("§7That name will not do. Speak again.");
    return;
  }

  const previous = player.getDynamicProperty(keeper.property);
  player.setDynamicProperty(keeper.property, name);

  if (keeper.id === "scroll") {
    if (typeof previous === "string" && previous) {
      player.sendMessage(`§7The scribe strikes the old name and writes §f${name}§7.`);
    } else {
      player.sendMessage(`§7The scribe writes it down: §f${name}§7. Stand in your row.`);
    }
    // Writing a name reads the roll again, so a rename is heard too. A pending
    // call is cancelled first, so two quick writes leave one live callback.
    player.removeTag(ROLLCALL_TAG);
    scheduleRollCall(player);
  } else {
    player.sendMessage("§7The keeper closes the roll. Only you and the keeper know that name.");
  }
}

// form.show can reject when the player disconnects or already has a screen
// open, and system.run discards the promise it is handed. Catch it here so the
// rejection can never surface as an unhandled one.
function openKeeperForm(player, keeper) {
  system.run(() => {
    runKeeperForm(player, keeper).catch(() => {
      try {
        player.sendMessage("§7The keeper cannot open the page right now. Try again.");
      } catch (e) {
        // The player is gone. Nothing left to say.
      }
    });
  });
}

function rememberOnWing(player, signetKey) {
  let wing = [];
  try {
    const raw = world.getDynamicProperty("dragon_rider:wing");
    if (typeof raw === "string") {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) wing = parsed;
    }
  } catch (e) {
    wing = [];
  }

  // Key on the stable player id, not the display name: a rename must not put
  // the same rider on the wing twice.
  wing = wing.filter((entry) => entry && entry.id !== player.id);
  wing.push({ id: player.id, name: player.name, signet: signetKey });
  if (wing.length > 24) wing = wing.slice(-24);

  world.setDynamicProperty("dragon_rider:wing", JSON.stringify(wing));
  return wing.length;
}

async function runSignetQuiz(player) {
  const scores = blankScores();
  let lastSignet = null;

  for (const question of QUESTIONS) {
    const form = new ActionFormData().title("Signet").body(question.body);
    for (const choice of question.choices) {
      form.button(choice.text);
    }

    const response = await form.show(player);
    if (response.canceled) return;

    const choice = question.choices[response.selection];
    if (choice) {
      scores[choice.signet] += 1;
      lastSignet = choice.signet;
    }
  }

  // A tie for the top score keeps the last accepted answer.
  const topScore = Math.max(...Object.values(scores));
  const leaders = Object.keys(scores).filter((key) => scores[key] === topScore);
  const signetKey =
    lastSignet !== null && scores[lastSignet] === topScore ? lastSignet : leaders[0];
  const signet = SIGNETS[signetKey];

  player.setDynamicProperty(SIGNET_PROPERTY, signetKey);
  const riderCount = rememberOnWing(player, signetKey);
  const wingLine =
    riderCount === 1 ? "Your wing has 1 rider." : `Your wing has ${riderCount} riders.`;

  player.onScreenDisplay.setTitle(`§6${signet.name}`);
  player.sendMessage(`§7Your signet: §6${signet.name}§7. ${signet.line}`);
  player.sendMessage(`§7${wingLine}`);

  const result = new MessageFormData()
    .title("Your signet")
    .body(`You are a §6${signet.name}§r.\n\n${signet.line}\n\n${wingLine}\n\nTake it again, or share your result.`)
    .button1("Again")
    .button2("Done");

  const again = await result.show(player);
  if (again.selection === 0) runSignetQuiz(player);
}

// A lodestone use is always cancelled so the compass screen never opens.
// The form itself waits for the bond. The plaza stone stays where it is.
// A keeper lectern is cancelled the same way, so the page screen never opens.
world.beforeEvents.playerInteractWithBlock.subscribe((event) => {
  if (!event.isFirstEvent) return;
  const player = event.player;
  const type = event.block?.typeId;

  if (type === BONDING_BLOCK) {
    event.cancel = true;
    system.run(() => {
      if (player.hasTag(BOND_TAG)) {
        runSignetQuiz(player);
      } else {
        player.sendMessage(NO_BOND_LINE);
      }
    });
    return;
  }

  if (type !== LECTERN_BLOCK) return;

  // No anchor means the college was never built here. Cancel the use so the
  // page screen does not open, and say why instead of failing silently.
  const origin = buildOrigin();
  if (!origin) {
    event.cancel = true;
    system.run(() => {
      player.sendMessage("§7The college is not built here. Run /function basgiath/build first.");
    });
    return;
  }

  const loc = event.block.location;
  const keeper = KEEPERS.find(
    (k) =>
      loc.x === origin.x + k.block.x &&
      loc.y === origin.y + k.block.y &&
      loc.z === origin.z + k.block.z
  );
  if (!keeper) return;

  event.cancel = true;
  openKeeperForm(player, keeper);
});

// Test bypass. It opens the quiz without the bond tag.
system.afterEvents.scriptEventReceive.subscribe((event) => {
  if (event.id !== TEST_EVENT) return;
  const entity = event.sourceEntity;
  if (entity?.typeId !== "minecraft:player") return;
  system.run(() => runSignetQuiz(entity));
});

// Test bypasses for the two keepers. Each opens its own form for the source
// entity without the tag gate, so the keeper paths stay testable.
const KEEPER_EVENTS = {
  "dragon_rider:rider_name": "scroll",
  "dragon_rider:dragon_name": "roll",
};

system.afterEvents.scriptEventReceive.subscribe((event) => {
  const keeperId = KEEPER_EVENTS[event.id];
  if (!keeperId) return;
  const entity = event.sourceEntity;
  if (entity?.typeId !== "minecraft:player") return;
  const keeper = KEEPERS.find((k) => k.id === keeperId);
  if (!keeper) return;
  openKeeperForm(entity, keeper);
});

// A phone does not run tick.json. This runs the same function once per tick.
system.runInterval(() => {
  try {
    world.getDimension("overworld").runCommand("function basgiath/tick");
  } catch (e) {
    // The world can tick before the function files are ready.
  }
}, 1);
