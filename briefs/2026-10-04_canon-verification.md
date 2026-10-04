# Canon verification — 2026-10-04

Two free models checked `docs/CANON.md`. Both are independent of this session.

## Lanes used

| Lane | Model | How |
|------|-------|-----|
| DeepSeek harness (official `dsh`) | `deepseek-flash` | `claude-ds -Prompt "..."` in the Terminal panel |
| OpenRouter free pool | `openrouter/free` | `pwsh -File scripts/ask-openrouter.ps1 "..."` |

Note: opencli was tried first. The sandbox blocks its browser daemon, so it is not usable from inside this session.

## Check 1 — DeepSeek, the twelve core facts

Prompt: check twelve facts and list only the wrong ones.

Result: **all twelve correct.** No errors.

The model added two caveats:

- The September 29 and October 1 dates are fan-wiki consensus. The books tie Presentation to the Gauntlet instead of printing a calendar date.
- Sources conflict on where Presentation happens. Some say the flight field. One says the Vale.

## Check 2 — DeepSeek, the open questions

Prompt: answer five open questions and say "unknown" where sources disagree.

Result:

1. **The keep arch words.** The model gave the line, and attributed it to Chapter 3. The same line is the Chapter 1 epigraph, credited to Article One, Section One of the Dragon Rider's Codex. **This is book text.** `docs/IP-RULES.md` rule 4 bans book text in the map. Write an original line.
2. **Gauntlet numbers.** 171 first-years attempt it. 169 finish, so two die on the course. The novel says **101** dragons are willing to bond. The wiki says 100. By Threshing the group is down to **147**.
3. **Parapet length.** Unknown. No source gives it. Only the width (18 inches) and the height (200 feet) are stated.
4. **Presentation Day date.** Not in the books. It is a fan-wiki reconstruction. The text only ties Presentation to the last Gauntlet practice.
5. **Threshing on October 1.** Yes, and this one is explicit in the text. The line says the date holds whatever weekday it falls on.

## Check 3 — OpenRouter free, independent second opinion

Prompt: the same twelve facts.

Result: flagged **one** item.

> "3 Presentation Day is September 30 (not September 29)."

Overall confidence: high.

## The one real conflict

The Presentation Day date. Three positions:

| Source | Date |
|--------|------|
| Empyrean Wiki | September 29 |
| OpenRouter free model | September 30 |
| The books | no date given |

The wiki date fits the "two days before Threshing" rule. The model date does not. Keep September 29 as the working date, but mark it as uncertain. The **order** and the **two-day gap** are not in doubt.

## Changes made to `docs/CANON.md`

- The Presentation date is now marked as a fan reconstruction, not canon.
- The keep arch line is now marked as book text. Do not carve it.
- The dragon count now says "about 100", with the 101-versus-100 conflict noted.
- The Gauntlet numbers now note that 147 reach Threshing.
- The open-questions list is updated.
