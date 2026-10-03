// Dragon Rider Map — the signet form.
// Target: Minecraft Bedrock 26.x, @minecraft/server 2.x
//
// Trigger: interact with a lodestone (the "Bonding Stone").
// Test:    /scriptevent dragon_rider:signet
//
// Original archetypes only. Do not replace these with the book's signets.

import { world, system } from "@minecraft/server";
import { ActionFormData, MessageFormData } from "@minecraft/server-ui";

const BONDING_BLOCK = "minecraft:lodestone";
const SIGNET_PROPERTY = "dragon_rider:signet";
const TEST_EVENT = "dragon_rider:signet";

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

  wing = wing.filter((entry) => entry && entry.name !== player.name);
  wing.push({ name: player.name, signet: signetKey });
  if (wing.length > 24) wing = wing.slice(-24);

  world.setDynamicProperty("dragon_rider:wing", JSON.stringify(wing));
  return wing.length;
}

async function runSignetQuiz(player) {
  const scores = blankScores();
  let lastSignet = null;

  for (const question of QUESTIONS) {
    const form = new ActionFormData().title("Conscription").body(question.body);
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

world.beforeEvents.playerInteractWithBlock.subscribe((event) => {
  if (!event.isFirstEvent) return;
  if (event.block?.typeId !== BONDING_BLOCK) return;
  const player = event.player;
  event.cancel = true;
  system.run(() => runSignetQuiz(player));
});

system.afterEvents.scriptEventReceive.subscribe((event) => {
  if (event.id !== TEST_EVENT) return;
  const entity = event.sourceEntity;
  if (entity?.typeId !== "minecraft:player") return;
  system.run(() => runSignetQuiz(entity));
});
