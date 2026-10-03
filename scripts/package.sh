#!/usr/bin/env bash
# Zip the two packs into dist/basgiath.mcaddon.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DIST="$ROOT/dist"
OUT="$DIST/basgiath.mcaddon"

mkdir -p "$DIST"
rm -f "$OUT"

(
  cd "$ROOT/addon"
  zip -r -X "$OUT" behavior_pack resource_pack -x "*.DS_Store" -x "__MACOSX/*"
)

echo "wrote $OUT"
