#!/usr/bin/env python3
"""Prove the voxel-consistency metric on a known-good flythrough, then a bad one.

A metric that has never seen a passing case cannot certify a failing one, so
this runs both:

  good  a render of the built scene. Every pixel must agree with the depth the
        world data predicts, so the score must be zero.
  bad   the same path, but the render is missing one block -- what a hole or a
        popping block looks like from the camera. The score must rise, and the
        worst voxel must be that block's.

The renders here are synthetic: cast through the voxel scene, with the defect
injected into the render rather than the data, which is how a client defect
reaches the checker. A real flythrough needs a client to draw it; the metric is
what this checks.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from voxel_consistency import Pose, depth_residual, render, worst  # noqa: E402

WIDTH, HEIGHT = 48, 36
FOV = 70.0
# Smaller than a block, so a residual names a patch of surface.
VOXEL_SIZE = 0.5

# A floor and a back wall, so the camera sees a surface throughout the path.
FLOOR = {(x, 0, z) for x in range(-6, 7) for z in range(-2, 12)}
WALL = {(x, y, 10) for x in range(-6, 7) for y in range(1, 7)}
SCENE = FLOOR | WALL

# The block the defective render omits.
MISSING = (2, 3, 10)

# A straight pass in front of the wall, always facing it.
PATH = [Pose(x=0.5, y=2.5, z=-1.0 + step, yaw=90.0) for step in range(0, 9)]


def _cell_of(block) -> tuple[int, int, int]:
    return tuple(math.floor(axis / VOXEL_SIZE) for axis in block)


def _to_block(cell) -> tuple[float, float, float]:
    return tuple(round(axis * VOXEL_SIZE, 2) for axis in cell)


def _chebyshev(a, b) -> int:
    return max(abs(a[i] - b[i]) for i in range(3))


def main() -> None:
    good = [(pose, render(SCENE, pose, WIDTH, HEIGHT, FOV)) for pose in PATH]
    # The renderer fails to draw one block for the whole pass.
    bad = [(pose, render(SCENE - {MISSING}, pose, WIDTH, HEIGHT, FOV)) for pose in PATH]

    good_rms, good_map = depth_residual(SCENE, good, WIDTH, HEIGHT, FOV, VOXEL_SIZE)
    bad_rms, bad_map = depth_residual(SCENE, bad, WIDTH, HEIGHT, FOV, VOXEL_SIZE)

    holes = sum(1 for e in bad_map.values() if not math.isfinite(e))
    print(f"good flythrough: rms={good_rms:.4f} over {len(good_map)} voxels")
    print(f"bad flythrough:  rms={_fmt(bad_rms)} over {len(bad_map)} voxels, "
          f"{holes} hole voxel(s)")
    print("worst voxels in the bad run:")
    for cell, error in worst(bad_map, 5):
        print(f"  {_to_block(cell)}  error={_fmt(error)}")

    failures = []
    if good_rms != 0.0:
        failures.append(f"a render of the built scene reads {good_rms:.4f}, not zero")
    if not math.isinf(bad_rms) and bad_rms < 0.5:
        failures.append(f"the missing block barely moved the score ({bad_rms:.4f})")
    if holes < 1:
        failures.append("the missing block did not register as a hole")
    top = worst(bad_map, 1)
    if not top or _chebyshev(top[0][0], _cell_of(MISSING)) > 2:
        found = _to_block(top[0][0]) if top else None
        failures.append(f"the worst voxel {found} is not the missing block {MISSING}")

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        sys.exit(1)
    print("\nvoxel consistency ok: a correct render reads zero, a missing "
          "block is found at its own coordinates")


def _fmt(value) -> str:
    return "hole" if not math.isfinite(value) else f"{value:.3f}"


if __name__ == "__main__":
    main()
