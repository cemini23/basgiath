#!/usr/bin/env python3
"""Find, and where it is mechanical fix, pack JSON that a Mojang update broke.

The pack faces breakage whenever Bedrock moves a schema. This is the reusable
part of that: a table of known deprecations, each with a test and, where the
change is mechanical, a rewrite. Every entry here is a deprecation this pack
actually met on the server, so the table is evidence, not guesswork.

    python3 scripts/migrate_schema.py            # check; exit 1 if any applies
    python3 scripts/migrate_schema.py --write    # apply the mechanical fixes
    python3 scripts/migrate_schema.py --list     # describe the table

Bedrock only. The tool reads the pack's own JSON; it never touches the game.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDON = ROOT / "addon"
# The release the shipped world targets. A file below this may be read through
# a compatibility path that a future update drops.
TARGET_FORMAT = (1, 21, 90)


class Finding:
    def __init__(self, migration: str, path: Path, where: str, detail: str) -> None:
        self.migration = migration
        self.path = path
        self.where = where
        self.detail = detail

    def __str__(self) -> str:
        return f"{self.path.relative_to(ROOT)}: {self.where}: {self.detail} ({self.migration})"


def _walk(node, where=""):
    """Yield (json path, value) for every dict and list in a document."""
    if isinstance(node, dict):
        yield where or ".", node
        for key, value in node.items():
            yield from _walk(value, f"{where}.{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _walk(value, f"{where}[{index}]")


def check_icon_shape(path: Path, data) -> list[Finding]:
    """An item icon must be {"textures": {"default": ...}}, not {"texture": ...}.

    The old single-texture form was the shape that failed on 1.26.
    """
    found = []
    for where, node in _walk(data):
        if not isinstance(node, dict) or "minecraft:icon" not in node:
            continue
        icon = node["minecraft:icon"]
        if isinstance(icon, dict) and "texture" in icon and "textures" not in icon:
            found.append(
                Finding("icon-shape", path, f"{where}.minecraft:icon",
                        'uses {"texture": ...}; needs {"textures": {"default": ...}}')
            )
    return found


def fix_icon_shape(data) -> int:
    changed = 0
    for _where, node in _walk(data):
        if isinstance(node, dict) and isinstance(node.get("minecraft:icon"), dict):
            icon = node["minecraft:icon"]
            if "texture" in icon and "textures" not in icon:
                node["minecraft:icon"] = {"textures": {"default": icon["texture"]}}
                changed += 1
    return changed


def check_recipe_unlock(path: Path, data) -> list[Finding]:
    """A 1.20+ recipe needs unlock data, or the game drops it.

    The server logs "1.20+ Recipes require unlock data" and the conversion never
    appears.
    """
    found = []
    if "minecraft:recipe_shaped" in data or "minecraft:recipe_shapeless" in data:
        body = data.get("minecraft:recipe_shaped") or data.get("minecraft:recipe_shapeless")
        if isinstance(body, dict) and "unlock" not in body:
            found.append(
                Finding("recipe-unlock", path, "recipe",
                        "has no unlock data; 1.20+ drops a recipe without it")
            )
    return found


def fix_recipe_unlock(data) -> int:
    changed = 0
    for key in ("minecraft:recipe_shaped", "minecraft:recipe_shapeless"):
        body = data.get(key)
        if isinstance(body, dict) and "unlock" not in body:
            rebuilt = {}
            for field, value in body.items():
                rebuilt[field] = value
                if field == "description":
                    rebuilt["unlock"] = {"context": "AlwaysUnlocked"}
            data[key] = rebuilt
            changed += 1
    return changed


def check_format_version(path: Path, data) -> list[Finding]:
    """Report a behavior-pack format_version below the release the world targets.

    A resource pack has its own version ladder -- an entity client file can
    legitimately sit at 1.10.0 while the game is at 1.21 -- so this reads only
    the behavior pack, where the version tracks the game.
    """
    found = []
    if "resource_pack" in path.parts:
        return found
    raw = data.get("format_version")
    if isinstance(raw, str) and raw.count(".") == 2:
        parts = tuple(int(p) for p in raw.split("."))
        if parts < TARGET_FORMAT:
            found.append(
                Finding("format-version", path, "format_version",
                        f"{raw} is below the target {'.'.join(map(str, TARGET_FORMAT))}")
            )
    return found


# (name, check, fix or None, whether the fix is mechanical, whether a finding
# should fail the check). A deprecation that breaks the content is fatal. An
# older format_version is not: the game reads it through a compatibility path,
# so it is reported and not failed.
MIGRATIONS = (
    ("icon-shape", check_icon_shape, fix_icon_shape, True, True),
    ("recipe-unlock", check_recipe_unlock, fix_recipe_unlock, True, True),
    ("format-version", check_format_version, None, False, False),
)


def pack_json() -> list[Path]:
    return sorted(
        path
        for path in ADDON.rglob("*.json")
        if "__pycache__" not in path.parts
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="apply the mechanical fixes")
    parser.add_argument("--list", action="store_true", help="describe the table")
    args = parser.parse_args()

    if args.list:
        for name, _check, fix, mechanical, fatal in MIGRATIONS:
            print(f"{name:16} mechanical={str(mechanical).lower()} "
                  f"fatal={str(fatal).lower()} fix={fix.__name__ if fix else 'none'}")
        return

    findings: list[Finding] = []
    fatal_names = {name for name, _c, _f, _m, fatal in MIGRATIONS if fatal}
    changed = 0
    for path in pack_json():
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue  # not a schema document; validate.sh owns parse errors
        if args.write:
            touched = 0
            for _name, _check, fix, mechanical, _fatal in MIGRATIONS:
                if mechanical and fix:
                    touched += fix(data)
            # Write only a file this pass changed. Rewriting every document
            # reformats the ones with nothing wrong, which buries the real
            # change in a large diff.
            if touched:
                path.write_text(json.dumps(data, indent=2) + "\n")
                changed += touched
        for name, check, _fix, _mechanical, _fatal in MIGRATIONS:
            findings.extend(check(path, data))

    if args.write:
        print(f"applied {changed} mechanical fix(es)")

    blocking = [f for f in findings if f.migration in fatal_names]
    if not findings:
        print(f"schema ok: {len(pack_json())} pack JSON files, no known deprecation")
        return

    for finding in findings:
        print(finding, file=sys.stderr)
    if not blocking:
        print(f"{len(findings)} advisory finding(s); nothing broken", file=sys.stderr)
        return
    print(f"{len(blocking)} blocking schema finding(s); run --write for the "
          "mechanical ones", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
