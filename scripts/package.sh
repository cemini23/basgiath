#!/usr/bin/env bash
# Regenerate the model and the map, then zip the packs and the world.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"
OUT="$DIST/basgiath.mcaddon"

python3 "$ROOT/scripts/build_dragon_model.py"
python3 "$ROOT/scripts/build_map.py"

mkdir -p "$DIST"
rm -f "$OUT"

(
  cd "$ROOT/addon"
  zip -r -X "$OUT" behavior_pack resource_pack -x "*.DS_Store" -x "__MACOSX/*" -x "*/__pycache__/*"
)

python3 "$ROOT/scripts/build_world.py"
echo "wrote $OUT"
