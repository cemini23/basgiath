#!/usr/bin/env bash
# Regenerate the model and the map, then zip the packs and the world.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"
OUT="$DIST/basgiath.mcaddon"

# Fail once, early, with a readable message. A bare Ubuntu image has neither
# of these: the build needs Pillow to write the dragon texture, and zip to
# bundle the packs. Without this check the run dies later with a traceback.
if ! command -v zip >/dev/null 2>&1; then
  echo "package.sh needs the zip tool to bundle the packs. Install it (Ubuntu: apt-get install -y zip)." >&2
  exit 1
fi

if ! python3 -c "import PIL" >/dev/null 2>&1; then
  echo "package.sh needs Pillow for the dragon texture. Install it (python3 -m pip install Pillow, or Ubuntu: apt-get install -y python3-pil)." >&2
  exit 1
fi

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
