#!/usr/bin/env python3
"""Validate the two pack manifests, and the .mcaddon they ship inside.

A duplicate, malformed, or dangling UUID makes the Bedrock import dialog
reject the pack, and the player never sees the world. A script API or engine
version the game cannot serve fails the same way, silently. This check runs
before the zip is written, so a broken manifest never reaches dist/.

Usage:
    python3 scripts/validate_manifests.py
    python3 scripts/validate_manifests.py --mcaddon dist/basgiath.mcaddon
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BEHAVIOR = ROOT / "addon/behavior_pack/manifest.json"
RESOURCE = ROOT / "addon/resource_pack/manifest.json"
# The two packs that ship, keyed by the name the zip uses for the folder.
PACKS = {"behavior_pack": BEHAVIOR, "resource_pack": RESOURCE}
# The folder each pack keeps inside the .mcaddon. package.sh zips the two
# folders from addon/ at the archive root.
ZIP_DIR = {"behavior_pack": "behavior_pack", "resource_pack": "resource_pack"}

# The script API contract. Both modules are stable at 2.0.0. A bump changes
# the runtime the script is written against, so it must be a deliberate edit,
# never a side effect of a tool or a merge.
SCRIPT_MODULES = {"@minecraft/server": "2.0.0", "@minecraft/server-ui": "2.0.0"}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def world_target() -> tuple[int, int, int]:
    """The Bedrock release the shipped world targets.

    build_world.py writes it into InventoryVersion and the client version
    fields. min_engine_version must not exceed it, or a client the world
    accepts will silently refuse the pack.
    """
    src = (ROOT / "scripts/build_world.py").read_text(encoding="utf-8")
    match = re.search(r'"InventoryVersion":\s*"(\d+\.\d+\.\d+)"', src)
    if not match:
        fail("cannot read the world target from scripts/build_world.py")
    return tuple(int(part) for part in match.group(1).split("."))


def version_vector(value: object, what: str) -> tuple[int, int, int]:
    if (
        not isinstance(value, list)
        or len(value) != 3
        or not all(isinstance(n, int) and n >= 0 for n in value)
    ):
        fail(f"{what} is not a version vector [a, b, c]: {value!r}")
    return (value[0], value[1], value[2])


def check_pack_set() -> dict[str, dict]:
    """Exactly two packs, each with the header and module fields the game reads."""
    found = {path.resolve() for path in (ROOT / "addon").rglob("manifest.json")}
    expected = {path.resolve() for path in PACKS.values()}
    if found != expected:
        extra = sorted(str(path.relative_to(ROOT)) for path in found - expected)
        missing = sorted(str(path.relative_to(ROOT)) for path in expected - found)
        fail(f"expected exactly two packs; extra={extra} missing={missing}")

    manifests: dict[str, dict] = {}
    for name, path in PACKS.items():
        data = json.loads(path.read_text(encoding="utf-8"))
        header = data.get("header")
        if not isinstance(header, dict):
            fail(f"{name} has no header")
        if not header.get("uuid"):
            fail(f"{name} header has no uuid")
        if not data.get("modules"):
            fail(f"{name} declares no modules")
        manifests[name] = data
    return manifests


def check_uuids(manifests: dict[str, dict]) -> None:
    """Every header and module UUID is valid, and unique across both packs."""
    seen: dict[str, str] = {}
    for name, data in manifests.items():
        entries = [("header", data["header"]["uuid"])]
        entries += [(f"module[{i}]", module.get("uuid", "")) for i, module in enumerate(data["modules"])]
        for where, raw in entries:
            try:
                parsed = str(uuid.UUID(raw))
            except (ValueError, AttributeError, TypeError):
                fail(f"{name} {where} uuid is not a valid UUID: {raw!r}")
            if parsed in seen:
                fail(f"uuid {parsed} is used by both {seen[parsed]} and {name} {where}")
            seen[parsed] = f"{name} {where}"


def check_links(manifests: dict[str, dict]) -> None:
    """The behavior pack links to the resource pack, and no dependency dangles.

    A pack dependency names the other pack by its header UUID. Bedrock loads
    the dependency when the required version is at or below the version the
    other pack ships, so writing the current version is a floor, not a pin to
    one exact build.
    """
    headers = {str(uuid.UUID(data["header"]["uuid"])): name for name, data in manifests.items()}
    for name, data in manifests.items():
        for dep in data.get("dependencies", []):
            raw = dep.get("uuid")
            if raw is None:
                continue  # a module dependency, handled by check_script_modules
            try:
                dep_uuid = str(uuid.UUID(raw))
            except (ValueError, AttributeError, TypeError):
                fail(f"{name} declares a dependency on an invalid uuid: {raw!r}")
            if dep_uuid not in headers:
                fail(f"{name} depends on uuid {dep_uuid}, which is not a pack in this add-on")
            if dep_uuid == str(uuid.UUID(data["header"]["uuid"])):
                fail(f"{name} depends on itself")
            target = headers[dep_uuid]
            required = version_vector(dep.get("version"), f"{name} dependency on {target} version")
            available = version_vector(manifests[target]["header"].get("version"), f"{target} header version")
            if required > available:
                fail(f"{name} requires {target} version {required}, but it ships {available}")

    # The behavior pack must name the resource pack, so a player who enables
    # only the behavior pack still loads the textures and models.
    behavior = manifests["behavior_pack"]
    resource_uuid = str(uuid.UUID(manifests["resource_pack"]["header"]["uuid"]))
    declared = {
        str(uuid.UUID(dep["uuid"]))
        for dep in behavior.get("dependencies", [])
        if dep.get("uuid")
    }
    if resource_uuid not in declared:
        fail("the behavior pack does not depend on the resource pack uuid")


def check_script_modules(manifests: dict[str, dict]) -> None:
    """The script API is pinned at 2.0.0, and nothing bumps it."""
    declared: dict[str, list[tuple[str, object]]] = {}
    for name, data in manifests.items():
        for dep in data.get("dependencies", []):
            module = dep.get("module_name")
            if module:
                declared.setdefault(module, []).append((name, dep.get("version")))
    for module, expected in SCRIPT_MODULES.items():
        packs = {name for name, _ in declared.get(module, [])}
        if "behavior_pack" not in packs:
            fail(f"the behavior pack must declare a dependency on {module} at {expected}")
        for name, version in declared[module]:
            if version != expected:
                fail(f"{name} pins {module} at {version!r}, not {expected!r}")


def check_engine(manifests: dict[str, dict]) -> None:
    """min_engine_version is a vector at or below the release the world targets."""
    target = world_target()
    for name, data in manifests.items():
        value = data["header"].get("min_engine_version")
        engine = version_vector(value, f"{name} min_engine_version")
        if engine > target:
            fail(
                f"{name} min_engine_version {engine} is above the world target {target}; "
                "an older client would silently refuse the pack"
            )


def check_mcaddon(path: Path, manifests: dict[str, dict]) -> None:
    """The .mcaddon holds both packs, and matches the manifests just checked."""
    if not path.exists():
        fail(f"mcaddon not found: {path}")
    with zipfile.ZipFile(path) as bundle:
        names = set(bundle.namelist())
        for name, data in manifests.items():
            member = f"{ZIP_DIR[name]}/manifest.json"
            if member not in names:
                fail(f"the .mcaddon does not contain {member}")
            inside = json.loads(bundle.read(member))
            if inside["header"]["uuid"] != data["header"]["uuid"]:
                fail(f"{member} uuid does not match addon/{name}/manifest.json")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcaddon", type=Path, help="also verify this .mcaddon holds both packs")
    args = parser.parse_args()

    manifests = check_pack_set()
    check_uuids(manifests)
    check_links(manifests)
    check_script_modules(manifests)
    check_engine(manifests)
    if args.mcaddon:
        check_mcaddon(args.mcaddon, manifests)
    total = sum(1 + len(data["modules"]) for data in manifests.values())
    print(f"manifests ok: 2 packs, {total} unique UUIDs, script API pinned at 2.0.0")
    if args.mcaddon:
        print(f"mcaddon ok: {args.mcaddon}")


if __name__ == "__main__":
    main()
