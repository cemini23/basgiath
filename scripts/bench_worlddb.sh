#!/usr/bin/env bash
# Offline world-state test.
#
# Edits the world database without a client, then boots the official Bedrock
# server against it and asserts that the server reads the edit. This is the
# writer half of scripts/leveldb_le.py: the reader is proven by decoding what
# the server wrote; this proves a value we wrote is honoured.
#
# Run scripts/bench_bds.sh first. It boots the server once, which creates db/.
# This script then reuses that world directory.
#
# Linux only, like bench_bds.sh: the server binary does not run on macOS.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${BENCH_BDS_WORK:-/tmp/basgiath-bds}"
BDS="$WORK/bds"
WORLD="$BDS/worlds/Basgiath"
DB="$WORLD/db"
RESULT="$WORK/writer-result.txt"
LOG="$WORK/writer-server.log"
TEST_X=0
# The bench writes to (0,79,0) and probes it, so the chunk is loaded and the
# height is writable. A high y is not: the server refuses it silently.
TEST_Y=79
TEST_Z=0

if [ "$(uname -s)" != "Linux" ]; then
  echo "bench_worlddb.sh needs the Linux Bedrock server. This machine is $(uname -s)." >&2
  exit 2
fi

if [ ! -d "$DB" ]; then
  echo "no world database at $DB; run scripts/bench_bds.sh first" >&2
  exit 1
fi
if [ ! -x "$BDS/bedrock_server" ]; then
  echo "no server binary at $BDS/bedrock_server" >&2
  exit 1
fi

# ---------------------------------------------------------------- edit offline

echo "=== editing the scoreboard offline ==="
python3 - "$ROOT" "$DB" <<'PY'
import sys
from pathlib import Path

root, db_arg = sys.argv[1], sys.argv[2]
sys.path.insert(0, str(Path(root) / "scripts"))
import leveldb_le as L

db = Path(db_arg)
before = L.read_db(db)
if "scoreboard" not in before:
    raise SystemExit("the world database has no scoreboard record")

_name, node = L.decode_typed(before["scoreboard"])

# Find the fake player the bench sets, then that player's row in map_state.
target_id = None
for entry in L.compound_get(node, "Entries")[1][1]:
    if L.node_value(L.compound_get(entry, "FakePlayerName")) == "bg_twenty":
        target_id = L.node_value(L.compound_get(entry, "ScoreboardId"))
if target_id is None:
    raise SystemExit("bg_twenty is not in the scoreboard Entries")

changed = 0
for objective in L.compound_get(node, "Objectives")[1][1]:
    if L.node_value(L.compound_get(objective, "Name")) != "map_state":
        continue
    for score in L.compound_get(objective, "Scores")[1][1]:
        if L.node_value(L.compound_get(score, "ScoreboardId")) == target_id:
            old = L.node_value(L.compound_get(score, "Score"))
            L.compound_set(score, "Score", (L.TAG_INT, 999))
            changed += 1
            print(f"bg_twenty map_state: {old} -> 999")
if changed != 1:
    raise SystemExit(f"expected exactly one score to change, changed {changed}")

path = L.write_record(db, "scoreboard", L.encode_typed("", node))
print(f"wrote {path.name}")

# The server drops a journal record whose checksum is wrong, so verify the one
# we just wrote before trusting the in-game assert.
L.journal_records(path.read_bytes(), strict=True)
print("journal checksum verified")

# Re-read through the reader, as the server would on the next open.
again = L.read_db(db)
_name2, node2 = L.decode_typed(again["scoreboard"])
for objective in L.compound_get(node2, "Objectives")[1][1]:
    if L.node_value(L.compound_get(objective, "Name")) == "map_state":
        rows = [
            (L.node_value(L.compound_get(s, "ScoreboardId")), L.node_value(L.compound_get(s, "Score")))
            for s in L.compound_get(objective, "Scores")[1][1]
        ]
        print("scores after write:", rows)
PY

# ------------------------------------------------------- boot and assert in-game

echo "=== booting the server against the edited db ==="

cd "$BDS"
rm -f fifo "$LOG"
mkfifo fifo
# Keep one write end open so tail does not see EOF.
sleep 300 > fifo &
HOLD=$!

(
  export LD_LIBRARY_PATH=.
  stdbuf -oL -eL tail -n +1 -f fifo | stdbuf -oL -eL ./bedrock_server > "$LOG" 2>&1
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
  if grep -q "Server started" "$LOG" 2>/dev/null; then started=1; break; fi
  sleep 1
done
if [ "$started" -ne 1 ]; then
  echo "server did not start; last log lines:" >&2
  tail -n 40 "$LOG" >&2 || true
  exit 1
fi

send() {
  printf "%s\n" "$1" > fifo
  sleep 1
}

# A block probe. The marker is placed only when the score matches, and the
# probe reports whether a gold block is really there. This is the bench's
# method: a command that fails loudly when the condition holds.
mark_clear() {
  printf "%s\n" "setblock ${TEST_X} ${TEST_Y} ${TEST_Z} air" > fifo
  sleep 0.5
}

mark_check() {
  local start
  start="$(wc -l < "$LOG" | tr -d ' ')"
  printf "%s\n" "execute unless block ${TEST_X} ${TEST_Y} ${TEST_Z} gold_block run say MISS_MARK" > fifo
  sleep 1
  if tail -n +"$((start + 1))" "$LOG" | grep -q "unless block test failed"; then
    echo "true"
  else
    echo "false"
  fi
}

score_marker() {
  printf "%s\n" "execute if score $1 map_state matches $2 run setblock ${TEST_X} ${TEST_Y} ${TEST_Z} gold_block" > fifo
  sleep 1
}

# The probe must be able to report a false. This is the negative control: with
# the marker cleared, the probe has to say the block is absent.
mark_clear
PROBE_FALSE="$(mark_check)"

# Can the marker be placed at all here? If this fails, the position or the
# probe is wrong and the later results mean nothing.
mark_clear
send "setblock ${TEST_X} ${TEST_Y} ${TEST_Z} gold_block"
MARKER_PLACE="$(mark_check)"

# Positive control: a score set over the console, read back immediately. If
# this fails, the score test is broken, not the database write.
mark_clear
send "scoreboard players set bg_probe map_state 123"
score_marker bg_probe 123
PROBE_TRUE="$(mark_check)"

# The real question: does the score the server loaded match what we wrote to
# the database offline?
mark_clear
score_marker bg_twenty 999
WRITER_READ="$(mark_check)"

{
  echo "probe_reports_false_when_absent=$PROBE_FALSE"
  echo "marker_places_unconditionally=$MARKER_PLACE"
  echo "probe_reports_true_when_present=$PROBE_TRUE"
  echo "writer_read=$WRITER_READ"
  if [ "$WRITER_READ" = "true" ] && [ "$PROBE_TRUE" = "true" ] && [ "$PROBE_FALSE" = "false" ]; then
    echo "db_write_ok=true"
  else
    echo "db_write_ok=false"
  fi
} | tee "$RESULT"

echo
echo "=== server log: errors and scoreboard lines ==="
grep -iE "error|unknown|objective|not found|invalid|failed" "$LOG" 2>/dev/null \
  | grep -v "unless block test failed" | tail -25 || true
echo "=== server log: last 12 lines ==="
tail -n 12 "$LOG" 2>/dev/null || true
echo

if grep -q '^db_write_ok=true$' "$RESULT"; then
  echo "world db writer ok"
else
  echo "world db writer failed; see $RESULT and $LOG" >&2
  exit 1
fi
