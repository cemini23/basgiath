# Voxel consistency metric for the world-gen test bench

## WorkDir

`/Users/claudiobarone/Projects/dragon-rider-map`

## Where this came from

Image-gen wiki ingest 2026-10-06. arXiv:2610.03636 (**LoGo**, Caltech + World Labs) designs a reward for long-horizon video generation. The reward is not what matters here. The **metric** underneath it is, because it turns "does the world still look right after the camera moves?" into a number, and that is exactly the question an unattended Basgiath release check has to answer.

Wiki page: `wiki/sources/arxiv-2610-03636-logo-video-consistency.md`

## The problem this addresses

The stated Basgiath goal is a test bench that validates a release **without a human clicking through Minecraft**. The hard part is not asserting "the add-on loaded" — it is asserting **structural permanence**: that a structure does not develop holes, and that blocks do not pop in and out, as the player moves through the world.

A single-thumbnail or single-pose screenshot cannot see that. LoGo's metric can.

## The technique

1. Render a camera flythrough of the generated or loaded world (a fixed path, so runs are comparable).
2. Reconstruct a point cloud from keyframes with a geometry model — LoGo uses **VGGT-Ω**; a Bedrock-appropriate substitute may be needed since the input is blocky render output, not photographs.
3. **Voxelize** the 3D space. LoGo uses voxel size = 0.1 x P90 depth, roughly 3,000 voxels per 240-frame clip.
4. Compute **per-voxel reprojection error** (RGB and depth) against the reconstruction. The mean is the global score; the per-voxel map is the local score.
5. Track the **per-voxel map over time**. A voxel that is occupied and correct at frame 50 and wrong at frame 200 is a popping or hole defect, and it is localized — you get coordinates, not just "the video got worse".

## Why the local part matters

LoGo's central finding is that a **global scalar is too coarse**: it beats its own global-only ablation. For the test bench this is the difference between "consistency score 0.81" and "hole at (412, 64, -190) appearing after frame 150". Only the second one is actionable in a release check.

## What is reusable, and what is not

**Reusable:** the voxel-space consistency metric as a concept. It is a measurement, and measurements transfer.

**Not reusable:** the LoGo implementation. It trains reward models on 64 H100s against 14B camera-controlled backbones (Lingbot2, Lyra2, UniWorld) that are not in this project's stack. The paper claims code and checkpoints are released but **prints no repository URL and states no licence**, so treat the release as unconfirmed. Do not plan around it.

## Suggested next step

Prototype the metric on a **known-good** flythrough first, and confirm it reports low error. A metric that has never seen a passing case cannot certify a failing one. Cheap version to try first: a depth-based occupancy grid instead of full VGGT reconstruction, since the input is already voxel-structured.

## Note

LoGo's benchmark, TrajectoryBench, stylizes about 20% of its scenes in a "Minecraft" style — the authors found blocky scenes a useful consistency stress case. That is a weak signal, not a reason to adopt.

## Sources

- arXiv:2610.03636 — LoGo: Local-Global Rewards for Consistent Long-Horizon Video Generation
- `wiki/sources/arxiv-2610-03636-logo-video-consistency.md` (image-gen wiki)
