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

import { ItemStack, world, system } from "@minecraft/server";
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

// ---------------------------------------------------------------------------
// The vault desk
//
// The academy bank: a custom block that takes the marks a cadet is carrying and
// keeps a balance per rider, then pays marks back out. The balance is a number
// on the player, so it survives a restart and needs no scoreboard.
//
// Every value is in copper marks and matches the conversion recipes: a silver
// mark is nine copper, a gold mark is nine silver, a note is nine gold.

const VAULT_BLOCK = "dragon_rider:vault_desk";
const BANK_PROPERTY = "dragon_rider:bank";
const VAULT_EVENT = "dragon_rider:vault";

const CURRENCY = [
  { item: "dragon_rider:copper_mark", value: 1 },
  { item: "dragon_rider:silver_mark", value: 9 },
  { item: "dragon_rider:gold_mark", value: 81 },
  { item: "dragon_rider:bank_note", value: 729 },
];

const WITHDRAWALS = [
  { label: "Withdraw a silver mark", item: "dragon_rider:silver_mark", cost: 9 },
  { label: "Withdraw a gold mark", item: "dragon_rider:gold_mark", cost: 81 },
  { label: "Withdraw a bank note", item: "dragon_rider:bank_note", cost: 729 },
];

function bankBalance(player) {
  const raw = player.getDynamicProperty(BANK_PROPERTY);
  return typeof raw === "number" && Number.isFinite(raw) ? raw : 0;
}

function setBankBalance(player, value) {
  player.setDynamicProperty(BANK_PROPERTY, Math.max(0, Math.floor(value)));
}

// What the rider is carrying, and in which slots, so a deposit can empty them.
function carriedMarks(player) {
  const container = player.getComponent("minecraft:inventory")?.container;
  if (!container) return { value: 0, slots: [] };
  let value = 0;
  const slots = [];
  for (let slot = 0; slot < container.size; slot += 1) {
    const stack = container.getItem(slot);
    if (!stack) continue;
    const coin = CURRENCY.find((entry) => entry.item === stack.typeId);
    if (!coin) continue;
    value += coin.value * stack.amount;
    slots.push(slot);
  }
  return { value, slots };
}

function depositAll(player) {
  const container = player.getComponent("minecraft:inventory")?.container;
  if (!container) return 0;
  const { value, slots } = carriedMarks(player);
  for (const slot of slots) container.setItem(slot, undefined);
  if (value > 0) setBankBalance(player, bankBalance(player) + value);
  return value;
}

// Charge only what the pack accepts: a full inventory must not cost marks.
function withdraw(player, entry) {
  if (bankBalance(player) < entry.cost) return false;
  const container = player.getComponent("minecraft:inventory")?.container;
  if (!container) return false;
  if (container.addItem(new ItemStack(entry.item, 1))) return false;
  setBankBalance(player, bankBalance(player) - entry.cost);
  return true;
}

async function runVaultForm(player) {
  const carried = carriedMarks(player).value;
  const balance = bankBalance(player);

  const form = new ActionFormData()
    .title("Vault Desk")
    .body(`You carry ${carried} in marks.\nThe vault holds ${balance}.`)
    .button("Deposit carried marks");
  for (const entry of WITHDRAWALS) {
    form.button(`${entry.label} (${entry.cost})`);
  }

  const response = await form.show(player);
  if (response.canceled) return;

  if (response.selection === 0) {
    const banked = depositAll(player);
    player.sendMessage(
      banked > 0
        ? `§7The desk counts §f${banked}§7 into the vault. It holds §f${bankBalance(player)}§7.`
        : "§7There is nothing in your hands to bank."
    );
    return;
  }

  const entry = WITHDRAWALS[response.selection - 1];
  if (!entry) return;
  player.sendMessage(
    withdraw(player, entry)
      ? `§7The desk pays out. The vault holds §f${bankBalance(player)}§7.`
      : "§7The vault cannot cover that, or your hands are full."
  );
}

function openVaultForm(player) {
  system.run(() => {
    runVaultForm(player).catch(() => {
      try {
        player.sendMessage("§7The desk cannot open right now. Try again.");
      } catch (e) {
        // The player is gone. Nothing left to say.
      }
    });
  });
}

// ---------------------------------------------------------------------------
// The codices
//
// Readable items. Using one opens its pages: paginated content, which is the
// K283 extract, without depending on the vanilla book screen and its page
// limit. Every line is original fan writing. No passage from any book, and no
// character name: docs/CANON.md holds the denylist, and the release check
// scans this file for it.

const CODICES = {
  "dragon_rider:flight_manual": {
    title: "Flight Manual",
    pages: [
      "A wing answers the air, not the reins. Sit your weight forward and let the shoulders carry you. The animal reads the shift before you have finished making it.",
      "Climb in long lines, not sharp ones. A hard turn costs more than a climb, and a climb costs more than patience. Most first-month falls are a turn taken too late.",
      "When the wind turns against you, spend the height you have and wait it out. Nothing on the field is worth a broken neck before the season is out.",
    ],
  },
  "dragon_rider:dragon_codex": {
    title: "Dragon Codex",
    pages: [
      "The animal chooses before you do. Stand still, keep your hands down, and let it walk its circle. A circle means it is still deciding.",
      "A bond is not a leash. You will not command it and it will not obey. What the two of you build is a habit of glancing the same way at the same time.",
      "Feed it away from the others. A dragon crowded at its meal learns to guard the plate, and a guarding dragon is a danger to every rider nearby.",
    ],
  },
  "dragon_rider:academy_archive": {
    title: "Academy Archive",
    pages: [
      "The Parapet has been rebuilt twice. The first crossing was walked at night, in a storm, and the cadet who walked it came back along the span rather than over the gap.",
      "The flight field floods every spring. That is why it sits where it does: the ground there is flat, and flat ground is rare on this side of the Vale.",
      "Old riders say the Gauntlet measures a person. It measures only whether you stop at the far edge, which is a different question and a shorter one.",
    ],
  },
};

async function runCodex(player, codex) {
  let page = 0;
  for (;;) {
    const last = page === codex.pages.length - 1;
    const actions = [];
    if (!last) actions.push("next");
    if (page > 0) actions.push("back");
    actions.push("close");

    const form = new ActionFormData()
      .title(`${codex.title} - page ${page + 1} of ${codex.pages.length}`)
      .body(codex.pages[page]);
    for (const action of actions) {
      form.button(action === "next" ? "Next page" : action === "back" ? "Previous page" : "Close");
    }

    const response = await form.show(player);
    if (response.canceled) return;
    const action = actions[response.selection];
    if (action === "next") page += 1;
    else if (action === "back") page -= 1;
    else return;
  }
}

world.afterEvents.itemUse.subscribe((event) => {
  const codex = CODICES[event.itemStack?.typeId];
  if (!codex) return;
  const player = event.source;
  if (player?.typeId !== "minecraft:player") return;
  system.run(() => {
    runCodex(player, codex).catch(() => {
      try {
        player.sendMessage("§7The pages will not open right now. Try again.");
      } catch (e) {
        // The player is gone. Nothing left to say.
      }
    });
  });
});

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

  if (type === VAULT_BLOCK) {
    event.cancel = true;
    openVaultForm(player);
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

// Test bypass for the vault desk, so the bank is reachable without placing the
// block.
system.afterEvents.scriptEventReceive.subscribe((event) => {
  if (event.id !== VAULT_EVENT) return;
  const entity = event.sourceEntity;
  if (entity?.typeId !== "minecraft:player") return;
  openVaultForm(entity);
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

// ---------------------------------------------------------------------------
// Flight readout
//
// The rider's dragon readout on the action bar: speed, altitude and stamina.
// The whole point is the easing. A reading taken every tick changes constantly
// and reads as noise, so each number tweens toward its new value on an
// ease-in-out curve: the display settles, and a change is visible as a change
// rather than a flicker.
//
// This is deliberately not JSON UI. A ui/ file is client-side, so the bench
// and the content log cannot check it, and a malformed one breaks a player's
// HUD. Nothing here can do that. The custom panel goes in once a client can
// confirm it.
//
// Speed is read from the dragon's own movement, not from a velocity API, so it
// needs nothing the script API does not already expose.

const DRAGON_TYPE = "dragon_rider:dragon";
const HUD_INTERVAL = 4; // ticks between redraws, so 5 Hz
const HUD_TWEEN_DRAWS = 5; // redraws an eased change takes
const HUD_BAR_CELLS = 10;
const HUD_FAST = 20; // blocks per second that counts as full work
const STAMINA_MAX = 100;
const STAMINA_DRAIN = 3.0; // per draw, at full work
const STAMINA_RECOVER = 1.2; // per draw, below the work threshold
const STAMINA_WORK = 0.35;
const HUD_TEST_EVENT = "dragon_rider:hud";

// Slow at both ends, fast through the middle. A linear walk reads as a slide;
// this reads as a settle.
function easeInOutCubic(t) {
  if (t <= 0) return 0;
  if (t >= 1) return 1;
  return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

function clamp(value, low, high) {
  return value < low ? low : value > high ? high : value;
}

// A number that slides to a new target instead of jumping to it. Re-aiming
// restarts the curve from wherever the value has reached, so a target that
// moves mid-tween does not snap back.
class Eased {
  constructor(value) {
    this.value = value;
    this.from = value;
    this.to = value;
    this.step = HUD_TWEEN_DRAWS;
  }

  aim(target) {
    if (target !== this.to) {
      this.from = this.value;
      this.to = target;
      this.step = 0;
    }
  }

  advance() {
    if (this.step < HUD_TWEEN_DRAWS) this.step += 1;
    const t = this.step / HUD_TWEEN_DRAWS;
    this.value = this.from + (this.to - this.from) * easeInOutCubic(t);
    return this.value;
  }
}

// Colour carries the fill, so any font renders the bar. A block glyph would
// depend on the font having it.
function staminaBar(value) {
  const filled = Math.round(clamp(value / STAMINA_MAX, 0, 1) * HUD_BAR_CELLS);
  return "§a" + "|".repeat(filled) + "§8" + "|".repeat(HUD_BAR_CELLS - filled);
}

const flightReadouts = new Map();

// The live reading, or null when the player is not on a dragon. Speed is the
// distance the dragon moved since the last draw, over the elapsed time, which
// needs no velocity API.
function readFlight(player, state) {
  let mount = null;
  try {
    mount = player.getComponent("minecraft:riding")?.entityRidingOn ?? null;
  } catch (e) {
    mount = null;
  }
  if (!mount || mount.typeId !== DRAGON_TYPE) {
    state.last = null;
    return null;
  }

  const here = mount.location;
  let speed = 0;
  if (state.last) {
    const dx = here.x - state.last.x;
    const dy = here.y - state.last.y;
    const dz = here.z - state.last.z;
    speed = Math.sqrt(dx * dx + dy * dy + dz * dz) / (HUD_INTERVAL / 20);
  }
  state.last = { x: here.x, y: here.y, z: here.z };
  return { speed, altitude: here.y };
}

function drawFlightHud(player, forced) {
  let state = flightReadouts.get(player.id);
  if (!state) {
    state = {
      speed: new Eased(0),
      altitude: new Eased(0),
      stamina: new Eased(STAMINA_MAX),
      bar: STAMINA_MAX,
      last: null,
      shown: false,
    };
    flightReadouts.set(player.id, state);
  }

  const reading = forced ?? readFlight(player, state);
  if (!reading) {
    if (state.shown) {
      player.onScreenDisplay.setActionBar("§7");
      state.shown = false;
    }
    return;
  }

  state.shown = true;
  state.speed.aim(reading.speed);
  state.altitude.aim(reading.altitude);

  const work = clamp(reading.speed / HUD_FAST, 0, 1);
  state.bar = clamp(
    state.bar + (work > STAMINA_WORK ? -STAMINA_DRAIN * work : STAMINA_RECOVER),
    0,
    STAMINA_MAX
  );
  state.stamina.aim(state.bar);

  const speed = state.speed.advance();
  const altitude = state.altitude.advance();
  const stamina = state.stamina.advance();

  player.onScreenDisplay.setActionBar(
    `§bSpeed §f${speed.toFixed(1)}§7 b/s  ` +
      `§bAlt §f${Math.round(altitude)}  ` +
      `§bStamina §r${staminaBar(stamina)}`
  );
}

system.runInterval(() => {
  for (const player of world.getAllPlayers()) {
    try {
      drawFlightHud(player);
    } catch (e) {
      // One player's readout must never take the tick loop down.
    }
  }
}, HUD_INTERVAL);

// Test bypass, in the style of the other events here: draw the readout for the
// caller with values that climb on every call, so the easing is visible on a
// client without a dragon to ride. Not shipped behaviour: it needs the caller
// to run the scriptevent.
let hudDemoStep = 0;
system.afterEvents.scriptEventReceive.subscribe((event) => {
  if (event.id !== HUD_TEST_EVENT) return;
  const entity = event.sourceEntity;
  if (entity?.typeId !== "minecraft:player") return;
  hudDemoStep = (hudDemoStep + 1) % 4;
  const speeds = [0, 8, 22, 3];
  system.run(() =>
    drawFlightHud(entity, { speed: speeds[hudDemoStep], altitude: 96 + hudDemoStep * 4 })
  );
});
