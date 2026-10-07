#!/usr/bin/env python3
"""Check the textures on disk against the ones in the last commit, by pixel.

`git diff --exit-code` is the right gate for the generated text — the `.mcfunction`
files and the model JSON are byte-for-byte reproducible anywhere. It is the wrong
gate for a PNG.

Pillow hands a PNG to whatever zlib the platform links against, and macOS and
Ubuntu do not agree on the compressed bytes. The images are identical; only the
encoding differs. So a byte comparison reports a difference on every CI run and on
no developer machine, which is the worst kind of failing test: it is always red for
everyone and never reproducible locally.

This compares the decoded pixels and the dimensions instead. That is the property
the check was ever trying to protect — that the committed art is the art the script
makes. The encoding is allowed to differ, because it carries no meaning.

Run from the repo root, after regenerating:

    python3 scripts/build_textures.py
    python3 scripts/check_textures.py
"""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Every generated PNG, in both trees. The Java copies are byte copies of the
# Bedrock ones, so they inherit the same encoding question.
GLOBS = (
    "addon/resource_pack/textures",
    "java/src/main/resources/assets/basgiath/textures",
)

FAILURES: list[str] = []


def committed_bytes(path: str) -> bytes | None:
    """The file as of HEAD, or None when it is not in the commit yet."""
    result = subprocess.run(
        ["git", "show", f"HEAD:{path}"],
        cwd=ROOT, capture_output=True,
    )
    return result.stdout if result.returncode == 0 else None


def pixels(data: bytes):
    from PIL import Image

    with Image.open(io.BytesIO(data)) as image:
        rgba = image.convert("RGBA")
        return rgba.size, rgba.tobytes()


def main() -> None:
    checked = 0
    for pattern in GLOBS:
        for path in sorted((ROOT / pattern).rglob("*.png")):
            relative = path.relative_to(ROOT).as_posix()
            old = committed_bytes(relative)
            if old is None:
                # New art. Nothing to compare against; the commit will carry it.
                continue
            try:
                committed = pixels(old)
                current = pixels(path.read_bytes())
            except Exception as error:  # noqa: BLE001 - report, never crash
                FAILURES.append(f"{relative}: not readable as an image ({error})")
                continue
            checked += 1
            if committed[0] != current[0]:
                FAILURES.append(
                    f"{relative}: size changed, {committed[0]} committed vs {current[0]} on disk")
            elif committed[1] != current[1]:
                differing = sum(
                    1 for a, b in zip(committed[1], current[1]) if a != b)
                FAILURES.append(
                    f"{relative}: {differing} channel values differ between the committed "
                    "image and the generated one")

    if FAILURES:
        print(f"textures: {len(FAILURES)} failure(s)")
        for item in FAILURES:
            print(f"  - {item}")
        raise SystemExit(1)
    print(f"textures ok: {checked} images match the commit, pixel for pixel")


if __name__ == "__main__":
    main()
