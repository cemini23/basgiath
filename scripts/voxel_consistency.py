#!/usr/bin/env python3
"""A voxel-space consistency metric, for checking a world without a human.

The K283/Image-gen extract. The reason to want it: a single screenshot cannot
say whether a structure keeps its shape as the camera moves. This turns that
question into a number, and prints where.

Method, after LoGo (arXiv:2610.03636), kept to the part that transfers:

1. take depth renders along a fixed camera path, so two runs compare;
2. unproject every pixel to a world point and bin it into a voxel;
3. for each voxel seen more than once, the reprojection error is the spread of
   the depths recorded for it: a surface point has one depth, whatever the
   viewpoint, so a spread means the surface moved, appeared, or vanished;
4. report the global score (RMS over voxels) and the per-voxel map.

The global number is coarse on purpose; the map is the actionable half. A
popping block puts a large error on its own voxel, which gives coordinates
rather than "the render got worse".

This module takes the depth frames, whatever produced them. A real flythrough
needs a client to render; the prototypes in check_voxel_consistency.py render
synthetic frames from a voxel scene so the metric itself can be tested.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

Vec3 = tuple[float, float, float]
Cell = tuple[int, int, int]


@dataclass(frozen=True)
class Pose:
    """A camera: a position, and the direction it faces, in degrees."""

    x: float
    y: float
    z: float
    yaw: float  # degrees, 0 looks along +X, 90 looks along +Z
    pitch: float = 0.0  # degrees, positive looks up

    def basis(self) -> tuple[Vec3, Vec3, Vec3]:
        """(forward, right, up) unit vectors for this pose."""
        yaw = math.radians(self.yaw)
        pitch = math.radians(self.pitch)
        forward = (
            math.cos(pitch) * math.cos(yaw),
            math.sin(pitch),
            math.cos(pitch) * math.sin(yaw),
        )
        world_up = (0.0, 1.0, 0.0)
        right = _normalise(_cross(forward, world_up))
        up = _normalise(_cross(right, forward))
        return forward, right, up


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _normalise(v: Vec3) -> Vec3:
    length = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    if length == 0:
        return (0.0, 0.0, 0.0)
    return (v[0] / length, v[1] / length, v[2] / length)


def _ray_direction(pose: Pose, screen_x: float, screen_y: float, fov: float) -> Vec3:
    """A ray through a normalised screen point, -1..1 on both axes."""
    forward, right, up = pose.basis()
    half = math.tan(math.radians(fov) / 2)
    d = (forward[0] + right[0] * screen_x * half + up[0] * screen_y * half,
         forward[1] + right[1] * screen_x * half + up[1] * screen_y * half,
         forward[2] + right[2] * screen_x * half + up[2] * screen_y * half)
    return _normalise(d)


def cast(occupancy: set[Cell], pose: Pose, screen_x: float, screen_y: float,
         fov: float, max_distance: float = 400.0, step: float = 0.5) -> float | None:
    """Distance from the camera to the first occupied voxel on this ray.

    Marched in fixed steps, then bisected, so the depth is the crossing point
    and not the last sample before it. A coarse depth would show up as error in
    a still scene.
    """
    direction = _ray_direction(pose, screen_x, screen_y, fov)
    near = 0.0
    t = 0.0
    while t < max_distance:
        t += step
        cell = (math.floor(pose.x + direction[0] * t),
                math.floor(pose.y + direction[1] * t),
                math.floor(pose.z + direction[2] * t))
        if cell in occupancy:
            far = t
            for _ in range(12):  # bisect the surface crossing
                mid = (near + far) / 2
                probe = (math.floor(pose.x + direction[0] * mid),
                         math.floor(pose.y + direction[1] * mid),
                         math.floor(pose.z + direction[2] * mid))
                if probe in occupancy:
                    far = mid
                else:
                    near = mid
            return far
        near = t
    return None


def render(occupancy: set[Cell], pose: Pose, width: int, height: int,
           fov: float = 70.0) -> list[list[float | None]]:
    """A depth image: the distance to the first block on each ray, or None."""
    rows = []
    for j in range(height):
        screen_y = 1 - 2 * (j + 0.5) / height
        row = []
        for i in range(width):
            screen_x = 2 * (i + 0.5) / width - 1
            row.append(cast(occupancy, pose, screen_x, screen_y, fov))
        rows.append(row)
    return rows


def unproject(pose: Pose, i: int, j: int, depth: float,
              width: int, height: int, fov: float) -> Vec3:
    """The world point a pixel saw, from its depth."""
    screen_x = 2 * (i + 0.5) / width - 1
    screen_y = 1 - 2 * (j + 0.5) / height
    direction = _ray_direction(pose, screen_x, screen_y, fov)
    return (pose.x + direction[0] * depth,
            pose.y + direction[1] * depth,
            pose.z + direction[2] * depth)


def project(pose: Pose, point: Vec3, width: int, height: int,
            fov: float) -> tuple[int, int, float] | None:
    """The pixel a world point falls on, and its distance, or None if off screen.

    The inverse of unproject. A point behind the camera, or outside the frame,
    is not visible from this pose.
    """
    forward, right, up = pose.basis()
    delta = (point[0] - pose.x, point[1] - pose.y, point[2] - pose.z)
    depth = delta[0] * forward[0] + delta[1] * forward[1] + delta[2] * forward[2]
    if depth <= 1e-6:
        return None
    across = delta[0] * right[0] + delta[1] * right[1] + delta[2] * right[2]
    above = delta[0] * up[0] + delta[1] * up[1] + delta[2] * up[2]
    half = math.tan(math.radians(fov) / 2)
    ndc_x = across / (depth * half)
    ndc_y = above / (depth * half)
    if abs(ndc_x) > 1 or abs(ndc_y) > 1:
        return None
    i = int((ndc_x + 1) / 2 * width)
    j = int((1 - ndc_y) / 2 * height)
    if not (0 <= i < width and 0 <= j < height):
        return None
    return i, j, depth


def depth_residual(occupancy: set[Cell],
                   frames: list[tuple[Pose, list[list[float | None]]]],
                   width: int, height: int, fov: float = 70.0,
                   voxel_size: float = 0.5) -> tuple[float, dict[Cell, float]]:
    """Compare each rendered frame against the depth the world data predicts.

    This is the release-check question the metric exists to answer: does what
    the client draws match what the build put there? The render comes from a
    client; the depth it is checked against is cast through the world's own
    voxels. A block the renderer failed to draw, or drew in the wrong place,
    shows as a depth residual on that block's voxel.

    Comparing two frames instead does not work. Depth is not an invariant of a
    surface -- a fixed point's depth changes as the camera moves -- so a
    frame-to-frame depth comparison measures the camera path. And at a grazing
    angle a single pixel spans a long stretch of surface, so even a correct
    frame disagrees with a reprojected neighbour there. Against the world data
    both depths come from the same pose and the same pixel, so a correct render
    agrees everywhere, including at grazing angles.

    The voxel is smaller than a block, so a residual names a patch of surface
    rather than a whole block.
    """
    residuals: dict[Cell, list[float]] = {}
    for pose, rendered in frames:
        expected = render(occupancy, pose, width, height, fov)
        for j in range(height):
            for i in range(width):
                seen = rendered[j][i]
                should_be = expected[j][i]
                if seen is None or should_be is None:
                    # A pixel that saw nothing where the world has a block, or
                    # the reverse, is a hole. Record it against the world point.
                    if seen is None and should_be is None:
                        continue
                    depth = should_be if should_be is not None else seen
                    point = unproject(pose, i, j, depth, width, height, fov)
                    cell = (math.floor(point[0] / voxel_size),
                            math.floor(point[1] / voxel_size),
                            math.floor(point[2] / voxel_size))
                    residuals.setdefault(cell, []).append(float("inf"))
                    continue
                # Bin by the world point the pixel should have seen, so the
                # residual lands on the built block, not on empty space.
                point = unproject(pose, i, j, should_be, width, height, fov)
                cell = (math.floor(point[0] / voxel_size),
                        math.floor(point[1] / voxel_size),
                        math.floor(point[2] / voxel_size))
                residuals.setdefault(cell, []).append(abs(seen - should_be))

    per_voxel = {cell: max(values) for cell, values in residuals.items() if values}
    if not per_voxel:
        return 0.0, {}
    if any(not math.isfinite(e) for e in per_voxel.values()):
        # A hole is not a small error, it is a missing surface: the render has
        # nothing where the world has a block. Averaging it in as a large
        # number would hide it behind a plausible score, so it is not a number.
        return float("inf"), per_voxel
    rms = math.sqrt(sum(e * e for e in per_voxel.values()) / len(per_voxel))
    return rms, per_voxel


def worst(per_voxel: dict[Cell, float], count: int = 5) -> list[tuple[Cell, float]]:
    """The voxels with the largest error, worst first."""
    return sorted(per_voxel.items(), key=lambda item: item[1], reverse=True)[:count]
