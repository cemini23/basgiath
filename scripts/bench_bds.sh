#!/usr/bin/env bash
# Boot the official Bedrock dedicated server and ask it about the world.
# This observes the pack. It does not change the add-on.
# A Mac cannot run the Linux server binary. CI runs scripts/bench_static.py.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORLD="${1:-$ROOT/dist/basgiath.mcworld}"
WORK="${BENCH_BDS_WORK:-/tmp/basgiath-bds}"
LOG="$WORK/server.log"
RESULT="$WORK/result.txt"

if [ "$(uname -s)" != "Linux" ]; then
  echo "bench_bds.sh needs the Linux Bedrock server. This machine is $(uname -s)." >&2
  exit 2
fi

if [ ! -f "$WORLD" ]; then
  echo "mcworld not found: $WORLD" >&2
  exit 1
fi

mkdir -p "$WORK"
cd "$WORK"

if ! command -v unzip >/dev/null || ! command -v curl >/dev/null; then
  if command -v apt-get >/dev/null; then
    apt-get update
    apt-get install -y --no-install-recommends unzip curl ca-certificates libcurl4 libssl3
  else
    echo "unzip and curl are required" >&2
    exit 1
  fi
fi

# The download page no longer embeds the zip URL. The services API does.
URL="$(curl -fsSL -A "Mozilla/5.0" "https://net.web.minecraft-services.net/api/v1.0/download/links" | python3 -c '
import json, sys
links = json.load(sys.stdin).get("result", {}).get("links", [])
for item in links:
    if item.get("downloadType") == "serverBedrockLinux":
        print(item.get("downloadUrl") or "")
        break
')"
if [ -z "$URL" ]; then
  echo "could not find the Linux Bedrock server download" >&2
  exit 1
fi
echo "server zip: $URL"
rm -rf bds worlds
mkdir -p bds
curl -fsSL -A "Mozilla/5.0" -o bedrock-server.zip "$URL"
unzip -q bedrock-server.zip -d bds

mkdir -p worlds/Basgiath
unzip -qo "$WORLD" -d worlds/Basgiath

# Derive the stage count from the extracted pack. A hard-coded count silently
# stops short when a zone grows. A world holds its packs under behavior_packs/,
# so match the tail of the path rather than pinning the whole layout.
STAGES="$(find worlds -path '*/functions/basgiath/stage_*.mcfunction' | wc -l | tr -d ' ')"
if [ "$STAGES" -lt 1 ]; then echo "no stage functions in the world" >&2; exit 1; fi

cat > bds/server.properties <<'EOF'
server-name=Basgiath bench
gamemode=adventure
difficulty=easy
allow-cheats=true
level-name=Basgiath
online-mode=true
server-port=19132
max-players=5
view-distance=6
tick-distance=4
content-log-file-enabled=true
content-log-console-output-enabled=false
EOF

# The dedicated server reads worlds relative to its working directory.
rm -rf bds/worlds
mv worlds bds/worlds

rm -f "$LOG" bds.fifo
mkfifo bds.fifo
# Keep one write end open so tail does not see EOF.
sleep 600 > bds.fifo &
HOLD=$!

# A plain stdin redirect does not deliver console commands.
# tail -f is the pipe dedicated-server images use. stdbuf flushes each line.
(
  cd bds
  export LD_LIBRARY_PATH=.
  stdbuf -oL -eL tail -n +1 -f ../bds.fifo | stdbuf -oL -eL ./bedrock_server > "$LOG" 2>&1
) &
SERVER=$!

cleanup() {
  kill "$SERVER" "$HOLD" >/dev/null 2>&1 || true
  wait "$SERVER" 2>/dev/null || true
  wait "$HOLD" 2>/dev/null || true
}
trap cleanup EXIT

started=0
for _ in $(seq 1 90); do
  if grep -q "Server started" "$LOG" 2>/dev/null; then
    started=1
    break
  fi
  if ! kill -0 "$SERVER" 2>/dev/null; then
    echo "server exited before it started" >&2
    tail -n 80 "$LOG" >&2 || true
    exit 1
  fi
  sleep 1
done

if [ "$started" -ne 1 ]; then
  echo "server did not report Server started" >&2
  tail -n 80 "$LOG" >&2 || true
  exit 1
fi

send() {
  printf "%s\n" "$1" > bds.fifo
  sleep 1
}

# say text does not reach the dedicated-server log.
# A matching block makes "execute unless block" fail, and that failure is logged.
: > "$WORK/probe-deltas.txt"
probe() {
  local name="$1" x="$2" y="$3" z="$4" block="$5"
  local start
  start="$(wc -l < "$LOG" | tr -d " ")"
  printf "%s\n" "execute unless block ${x} ${y} ${z} ${block} run say MISS_${name}" > bds.fifo
  sleep 0.8
  tail -n +"$((start + 1))" "$LOG" >> "$WORK/probe-deltas.txt" || true
  if tail -n +"$((start + 1))" "$LOG" | grep -q "unless block test failed"; then
    echo "${name}=true"
  else
    echo "${name}=false"
  fi
}

# The college is not in the flat world. Summon the same anchor the player
# function uses. tick.json may not run with zero players.
# The stone at (0,79,0) is the anchor's floor. An armor stand has gravity,
# so without it the anchor drops and every relative coordinate shifts.
send "tickingarea add circle 0 80 0 4 bench"
send "setblock 0 79 0 stone"
send "summon armor_stand \"build_anchor\" 0 80 0"
send "effect @e[type=armor_stand,name=\"build_anchor\"] resistance 999999 255 true"
send "scoreboard objectives add map_state dummy"
send "scoreboard players set #stage map_state 1"
sleep 3
tick_line="$(probe TICK_SPAN 20 112 20 stone_bricks)"
echo "tick path ${tick_line}" >&2

if [ "$tick_line" != "TICK_SPAN=true" ]; then
  echo "tick path missed the span; calling stage functions" >&2
  for n in $(seq -w 1 "$STAGES"); do
    send "execute as @e[type=armor_stand,name=\"build_anchor\",c=1] at @s run function basgiath/stage_${n}"
  done
  sleep 2
fi

# The live pass. Nothing above this line runs it, which is why a malformed
# command inside basgiath/live has never surfaced here: the stage path places
# blocks and the live path scores, and a bad scoreboard or titleraw line only
# logs an error when the command is actually executed. Call it a few times and
# capture the log delta. Every gate_* objective has to exist first, because
# the build function creates them and the stage loop above skips build.mcfunction.
LIVE_ERRORS="$WORK/live-errors.txt"
: > "$LIVE_ERRORS"
for gate in gate_time gate_start gate_pen gate_best; do
  send "scoreboard objectives add ${gate} dummy"
done
for _ in 1 2 3; do
  start="$(wc -l < "$LOG" | tr -d " ")"
  send "function basgiath/live"
  sleep 1
  tail -n +"$((start + 1))" "$LOG" >> "$LIVE_ERRORS" || true
done
# Keep only real command errors. The probe mechanism itself logs
# "unless block test failed" on every run, and a probe position outside the
# ticking area logs "Detect position"; neither is a command error.
grep -iE 'syntax error|unknown command|failed to execute|malformed' "$LIVE_ERRORS" \
  | grep -viE 'unless block test failed|detect position' > "$LIVE_ERRORS.real" || true
# The pipe is true even when the first grep finds nothing, so the file may not
# exist yet. Create it rather than let the result step fail to read it.
: >> "$LIVE_ERRORS.real"
LIVE_ERROR_COUNT="$(wc -l < "$LIVE_ERRORS.real" | tr -d ' ')"
if [ "$LIVE_ERROR_COUNT" != "0" ]; then
  echo "the live pass logged command errors:" >&2
  cat "$LIVE_ERRORS.real" >&2
  exit 1
fi
echo "live pass ran clean: 3 calls, no command error" >&2

{
  echo "$tick_line"
  # Re-set the control now the build is done. _ground() fills y=79 across the
  # whole footprint, so the block laid down for the anchor's floor is grass by
  # now. Setting it again here and probing it straight away proves the probe
  # reads a block that is really there.
  send "setblock 0 79 0 stone"
  probe CTRL_STONE 0 79 0 stone
  probe CTRL_NOT_GOLD 0 79 0 gold_block
  probe SPAN 20 112 20 stone_bricks
  probe GAP45 45 112 20 air
  probe GAP46 46 112 20 air
  probe COLUMN 20 100 20 air
  # The two keeper lecterns. The anchor sits at (0, 80, 0), so a lectern at
  # relative (128, 1, 34) is absolute (128, 81, 34) and relative (50, -1, 123)
  # is absolute (50, 79, 123).
  probe LECTERN_SCROLL 128 81 34 lectern
  probe LECTERN_ROLL 50 79 123 lectern
} > "$WORK/probe-results.txt"

python3 - "$LOG" "$RESULT" "$WORK/probe-results.txt" "$WORK/probe-deltas.txt" "$WORK/live-errors.real" <<'PY'
import sys
from pathlib import Path

log = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
result = Path(sys.argv[2])
probes = Path(sys.argv[3]).read_text(encoding="utf-8", errors="replace").splitlines()
deltas = Path(sys.argv[4]).read_text(encoding="utf-8", errors="replace").splitlines()
live_errors = Path(sys.argv[5]).read_text(encoding="utf-8", errors="replace").splitlines()
pack_error = None
for line in log.splitlines():
    text = line.lower()
    if "failed to load" in text and "pack" in text:
        pack_error = line
        break
values = {}
for line in probes:
    if "=" in line:
        key, value = line.split("=", 1)
        values[key] = value.strip()
need_true = ("CTRL_STONE", "SPAN", "GAP45", "GAP46", "COLUMN", "LECTERN_SCROLL", "LECTERN_ROLL")
lines = ["server_started=yes", f"pack_error={pack_error or 'none'}"]
lines.extend(probes)
ok = (not pack_error) and all(values.get(name) == "true" for name in need_true)
ok = ok and values.get("CTRL_NOT_GOLD") == "false"
live_ok = not live_errors
ok = ok and live_ok
lines.append(f"live_pass_clean={str(live_ok).lower()}")
lines.append(f"live_pass_errors={len(live_errors)}")
lines.append(f"blocks_ok={str(ok).lower()}")
lines.append("probe_deltas_begin")
lines.extend(deltas[-80:])
lines.append("probe_deltas_end")
result.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
if not ok:
    sys.exit(1)
PY
echo "bds bench ok"
