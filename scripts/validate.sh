#!/usr/bin/env bash
# Parse every addon JSON file. Fail if any file does not parse.
# Then read the pack UUIDs from the two manifests and fail if any UUID repeats.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

count=0
while IFS= read -r f; do
  if ! python3 -c 'import json,sys; json.load(open(sys.argv[1]))' "$f"; then
    echo "JSON parse failed: $f" >&2
    exit 1
  fi
  count=$((count + 1))
done < <(find addon -type f -name '*.json' | sort)

if [ "$count" -eq 0 ]; then
  echo "no JSON files under addon/" >&2
  exit 1
fi

python3 - "$count" <<'PY'
import json
import sys
from pathlib import Path

parsed = sys.argv[1]
paths = [
    Path("addon/behavior_pack/manifest.json"),
    Path("addon/resource_pack/manifest.json"),
]
uuids = []
for path in paths:
    data = json.loads(path.read_text())
    uuids.append(data["header"]["uuid"])
    for module in data["modules"]:
        uuids.append(module["uuid"])

if len(uuids) != len(set(uuids)):
    print("pack UUIDs are not unique:", ", ".join(uuids), file=sys.stderr)
    sys.exit(1)

print(f"parsed {parsed} JSON files; {len(uuids)} pack UUIDs are unique")
PY

# The fuller manifest contract: exactly two packs, a resolving cross-pack
# dependency, a pinned script API, and an engine minimum at or below the
# release the world targets. This is what the Bedrock import dialog reads.
python3 "$ROOT/scripts/validate_manifests.py"
