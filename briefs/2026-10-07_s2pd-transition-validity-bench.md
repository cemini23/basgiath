# Transition-validity bench for world generation

## WorkDir

`/Users/claudiobarone/Projects/dragon-rider-map`

## Where this came from

Image-gen wiki ingest 2026-10-07. arXiv:2610.06847 (**S2PD**, University of Cambridge + Toyota Motor Europe).

Unlike the previous Basgiath brief (LoGo, 2026-10-06), **this one ships released code, datasets and weights** — so it is checkable today rather than aspirational. Licence is unstated; check before any commercial use.

Wiki pages: `wiki/sources/arxiv-2610-06847-s2pd.md`, `wiki/concepts/serial-to-parallel-diffusion-schedule.md`

## The problem this addresses

The stated Basgiath goal is a test bench that validates a release **without a human clicking through Minecraft**. The hard part is not "did it load" — it is **structural permanence**: terrain does not develop holes, structures do not pop, and a later chunk stays valid given the earlier ones.

S2PD's contribution to that is not a generator. It is a way to **turn "is this consistent?" into a countable defect number**.

## The technique: invalid transitions per rollout

S2PD works on board games and physics toys, and measures consistency like this:

1. Parse the generator's output into **symbolic states** (for Conway: which cells are alive; for chess: the board position).
2. Define the **permitted transitions** between states as an explicit rule set.
3. Generate a rollout and **count how many transitions violated the rules**.

The headline result is Conway **9.4 invalid transitions per rollout (bidirectional) to 0.0**. Chess moves 51.0 to 12.3; puzzle moves 59.1 to 12.7.

The point for Basgiath is the **metric**, not the score. "Invalid transitions per rollout" is a single number that goes up when the world breaks, and it needs no human eye. It also localizes: the transition where the count increments tells you *when* and *where* the failure happened.

## Applying it to a Bedrock world

Bedrock terrain is already symbolic, which makes this easier than the video case rather than harder.

- **State** — chunk contents, block IDs in a vertical slice, structure bounding boxes, biome labels.
- **Permitted transitions** — what may legitimately follow what. Examples: no floating unsupported blocks after settle; no structure interior voided; no biome boundary discontinuity beyond a threshold; no block appearing in a region the generator never touched.
- **Rollout** — walk a fixed camera or player path and sample state at fixed intervals.
- **Metric** — derived blocks or violated adjacencies per rollout, and which transition index they first appeared at.

This complements the voxel-reprojection metric in the LoGo brief. Where that one reads *rendered* output and catches visual popping, this one reads *world data* and catches rule violations. Running both gives a visual check and a symbolic check.

## The second, more speculative hook

S2PD's actual generation change — **denoise serially at high noise, then in parallel at low noise** — has an analogue in autoregressive terrain synthesis: commit to coarse structure serially, where causality matters, then refine detail in parallel, where it does not. Recorded as a design idea only. Adopting it would require a block-causally trained generator, and Basgiath's world-gen pipeline is not one.

## Suggested next step

Write down the **permitted-transition rules for the Basgiath world** before writing any code. That rule list is the actual deliverable — it is the definition of a valid world, and it is useful regardless of what generates the world. Then the bench is a checker over that list.

Start with the cheapest rules that a human currently checks by eye. Those are the ones worth automating first.

## Sources

- arXiv:2610.06847 — S2PD: Serial-to-Parallel Diffusion for Physically and Logically Consistent Video Generation
- `wiki/sources/arxiv-2610-06847-s2pd.md`, `wiki/concepts/serial-to-parallel-diffusion-schedule.md` (image-gen wiki)
