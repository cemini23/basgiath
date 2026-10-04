"""Zone modules for the college generator.

Each module exposes ``build(ctx) -> list[str]``.
``scripts/build_map.py`` calls them. See README.md for the stage ranges.
"""

# Call order for the current world. Canon order is documented in README.md.
# Phase 0 keeps this order so the emitted commands stay the same.
CURRENT_ORDER = ("parapet", "quad", "dorms", "valley")
