#!/usr/bin/env bash
# Offline world-state test.
#
# STATUS (2026-10-06): the READER half works and is proven -- it reads a
# log-only world database and decodes the server's own scoreboard record.
# The WRITER half does NOT work yet. Two problems, both reproducible with this
# script:
#   1. write_record adds a journal file at a number above the manifest's
#      log_number. The server then fails to open the database, drops the
#      scoreboard ("No objective was found by the name 'map_state'") and starts
#      a fresh world. Appending to the log the manifest names, or adding a
#      VersionEdit for the new log, is the next thing to try.
#   2. After a second boot compacts the database into an .ldb table, read_db no
#      longer returns the scoreboard key, so table reading is incomplete.
# The control boot (no edit) passes, which is what isolates the write.
#
# Proves scripts/leveldb_le.py can read and write the Bedrock world database
# without a client. Run scripts/bench_bds.sh first: it boots the server once,
# which creates db/. This script then:
#
#   1. boots the server again with NO edit, and asks whether the scoreboard the
#      first boot wrote is still there. If it is not, the database is not
#      surviving a restart and the write test below means nothing.
#   2. edits the scoreboard offline, boots again, and asserts the server reads
#      the edit.
#
# Linux only, like bench_bds.sh: the server binary does not run on macOS.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${BENCH_BDS_WORK:-/tmp/basgiath-bds}"
BDS="$WORK/bds"
DB="$BDS/worlds/Basgiath/db"
RESULT="$WORK/writer-result.txt"
MARK_X=0
MARK_Y=79
MARK_Z=0

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

# Boot the server, run an if-score probe against the marker cell, and report
# whether the marker was placed. The marker is only placed when the score
# matches, and the probe reports whether a block is really there.
boot_and_probe() {
  local label="$1" target="$2" expected="$3"
  local log="$WORK/writer-$label.log" fifo="$WORK/writer-$label.fifo"

  cd "$BDS"
  rm -f "$fifo" "$log"
  mkfifo "$fifo"
  sleep 120 > "$fifo" &
  local hold=$!
  (
    export LD_LIBRARY_PATH=.
    stdbuf -oL -eL tail -n +1 -f "$fifo" | stdbuf -oL -eL ./bedrock_server > "$log" 2>&1
  ) &
  local server=$!

  local started=0
  for _ in $(seq 1 90); do
    grep -q "Server started" "$log" 2>/dev/null && { started=1; break; }
    sleep 1
  done
  if [ "$started" -ne 1 ]; then
    echo "  $label: server did not start" >&2
    tail -n 20 "$log" >&2 || true
    kill "$server" "$hold" >/dev/null 2>&1 || true
    echo "false"
    return
  fi

  printf "%s\n" "setblock ${MARK_X} ${MARK_Y} ${MARK_Z} air" > "$fifo"; sleep 1
  printf "%s\n" "execute if score ${target} map_state matches ${expected} run setblock ${MARK_X} ${MARK_Y} ${MARK_Z} gold_block" > "$fifo"
  sleep 2
  local start
  start="$(wc -l < "$log" | tr -d ' ')"
  printf "%s\n" "execute unless block ${MARK_X} ${MARK_Y} ${MARK_Z} gold_block run say MISS_${label}" > "$fifo"
  sleep 2
  if tail -n +"$((start + 1))" "$log" | grep -q "unless block test failed"; then
    echo "true"
  else
    echo "false"
  fi

  kill "$server" "$hold" >/dev/null 2>&1 || true
  wait "$server" 2>/dev/null || true
  wait "$hold" 2>/dev/null || true
  echo "  $label: see $log" >&2
}

echo "=== control: does the scoreboard survive a restart at all? ==="
echo "    (no edit; the first boot set bg_twenty to 20)"
BEFORE="$(boot_and_probe before bg_twenty 20)"
echo "    control result: $BEFORE"

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
original = before["scoreboard"]
name, node = L.decode_typed(original)

# Decode then re-encode the record untouched. If that is not byte-identical,
# the typed codec is lossy and any edit it writes is suspect.
again_bytes = L.encode_typed(name, node)
print(f"  round-trip identical: {again_bytes == original} "
      f"({len(original)} vs {len(again_bytes)} bytes)")
if again_bytes != original:
    for i, (a, b) in enumerate(zip(original, again_bytes)):
        if a != b:
            print(f"  first difference at {i}: {a:#04x} vs {b:#04x}")
            break
node = L.decode_typed(original)[1]

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
            print(f"  bg_twenty map_state: {L.node_value(L.compound_get(score, 'Score'))} -> 999")
            L.compound_set(score, "Score", (L.TAG_INT, 999))
            changed += 1
if changed != 1:
    raise SystemExit(f"expected exactly one score to change, changed {changed}")

path = L.write_record(db, "scoreboard", L.encode_typed("", node))
L.journal_records(path.read_bytes(), strict=True)
print(f"  wrote {path.name}, checksum verified")
PY

echo "=== does the server read our edit? ==="
AFTER="$(boot_and_probe after bg_twenty 999)"

{
  echo "scoreboard_survives_restart=$BEFORE"
  echo "offline_edit_read_by_server=$AFTER"
} | tee "$RESULT"

echo
if [ "$BEFORE" = "true" ] && [ "$AFTER" = "true" ]; then
  echo "world db writer ok"
else
  echo "world db writer: before=$BEFORE after=$AFTER" >&2
  exit 1
fi
