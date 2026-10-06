#!/usr/bin/env node
// Check the flight readout's easing curve and stamina bar, using the shipped
// source. The functions are lifted out of main.js and evaluated, so this tests
// the code that ships rather than a copy of it.
//
// This is not a visual check. It cannot say whether the readout looks right on
// a screen; only a client can. It checks the maths the display depends on.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const source = readFileSync(
  join(root, "addon/behavior_pack/scripts/main.js"),
  "utf8"
);

// The function text, up to the first brace that closes it back at column 0.
function extract(name) {
  const at = source.indexOf(`function ${name}(`);
  if (at < 0) throw new Error(`main.js has no ${name}()`);
  const end = source.indexOf("\n}\n", at);
  if (end < 0) throw new Error(`${name}() is not closed`);
  return source.slice(at, end + 2);
}

const constants = (name) => {
  const found = source.match(new RegExp(`^const ${name} = (-?[\\d.]+);`, "m"));
  if (!found) throw new Error(`main.js has no ${name}`);
  return found[0];
};

const code = [
  constants("HUD_BAR_CELLS"),
  constants("STAMINA_MAX"),
  extract("easeInOutCubic"),
  extract("clamp"),
  extract("staminaBar"),
].join("\n");

const { easeInOutCubic, staminaBar } = new Function(
  `${code}\nreturn { easeInOutCubic, staminaBar };`
)();

let failed = 0;
function check(name, ok, detail = "") {
  if (!ok) failed++;
  console.log(`${ok ? "ok   " : "FAIL "}${name}${ok ? "" : `  ${detail}`}`);
}

// --- the easing curve ---
check("ease f(0) = 0", easeInOutCubic(0) === 0);
check("ease f(1) = 1", easeInOutCubic(1) === 1);
check("ease f(0.5) = 0.5", Math.abs(easeInOutCubic(0.5) - 0.5) < 1e-9);
check("ease clamps below 0", easeInOutCubic(-1) === 0);
check("ease clamps above 1", easeInOutCubic(2) === 1);

let monotonic = true;
let symmetric = true;
for (let i = 1; i <= 200; i++) {
  if (easeInOutCubic(i / 200) < easeInOutCubic((i - 1) / 200) - 1e-12) {
    monotonic = false;
  }
}
for (let i = 0; i <= 20; i++) {
  const t = i / 20;
  if (Math.abs(easeInOutCubic(t) + easeInOutCubic(1 - t) - 1) > 1e-9) {
    symmetric = false;
  }
}
check("ease is monotonic", monotonic);
check("ease is symmetric about (0.5, 0.5)", symmetric);
check(
  "ease eases in (f(0.1) < 0.1)",
  easeInOutCubic(0.1) < 0.1,
  `f(0.1)=${easeInOutCubic(0.1)}`
);
check(
  "ease eases out (f(0.9) > 0.9)",
  easeInOutCubic(0.9) > 0.9,
  `f(0.9)=${easeInOutCubic(0.9)}`
);

// The curve must be gentler than a straight line at both ends, which is what
// makes a change read as a settle rather than a slide.
let gentlerEnds = true;
for (const t of [0.05, 0.1, 0.15, 0.85, 0.9, 0.95]) {
  const linearDistance = t < 0.5 ? t : 1 - t;
  const easedDistance = t < 0.5 ? easeInOutCubic(t) : 1 - easeInOutCubic(t);
  if (easedDistance > linearDistance) gentlerEnds = false;
}
check("ease is gentler than linear near both ends", gentlerEnds);

// --- the bar ---
const cells = (bar) => bar.replace(/§./g, "").length;
check("bar is 10 cells", cells(staminaBar(0)) === 10 && cells(staminaBar(100)) === 10);
check(
  "empty bar is all dark",
  staminaBar(0) === "§a" + "§8" + "|".repeat(10),
  staminaBar(0)
);
check(
  "full bar is all lit",
  staminaBar(100) === "§a" + "|".repeat(10) + "§8",
  staminaBar(100)
);
check(
  "half bar is half lit",
  staminaBar(50) === "§a" + "|".repeat(5) + "§8" + "|".repeat(5),
  staminaBar(50)
);
check("bar clamps above the maximum", staminaBar(999) === staminaBar(100));
check("bar clamps below zero", staminaBar(-5) === staminaBar(0));

console.log(failed ? `\n${failed} check(s) failed` : "\nflight readout ok");
process.exit(failed ? 1 : 0);
