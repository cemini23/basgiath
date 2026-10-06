#!/usr/bin/env bash
# Boot the official Linux Bedrock dedicated server against the GameTest world
# and run basgiath:dragon_rides on its console.
#
# This observes the dev test world. It does not change the add-on and it does
# not touch the shipped world. A Mac cannot run the Linux server binary, so
# this exits 2 there; the static gates cover the Mac.
#
# The exact GameTest result string in the dedicated-server log is not pinned
# by an API, so the parser below looks for a dragon_rides line that reports a
# pass. The last 60 log lines that mention gametest or dragon_rides are copied
# into result.txt verbatim, so a first run on a fresh server reveals the real
# format even when the pass/fail guess is wrong.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORLD="${1:-$ROOT/dist/gametest.mcworld}"
WORK="${BENCH_GAMETEST_WORK:-/tmp/basgiath-gametest}"
LOG="$WORK/server.log"
RESULT="$WORK/result.txt"
TEST_NAME="basgiath:dragon_rides"

if [ "$(uname -s)" != "Linux" ]; then
  echo "bench_gametest.sh needs the Linux Bedrock server. This machine is $(uname -s)." >&2
  exit 2
fi

if [ ! -f "$WORLD" ]; then
  echo "mcworld not found: $WORLD (run scripts/build_gametest_world.py first)" >&2
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

# The GameTest pack has to be inside the world the server boots, or the run
# below only reports an unknown test and never proves anything.
TEST_SCRIPT="worlds/Basgiath/behavior_packs/basgiath_tests/scripts/dragon_test.js"
if [ ! -f "$TEST_SCRIPT" ]; then
  echo "the world does not carry the GameTest pack ($TEST_SCRIPT missing)" >&2
  exit 1
fi

cat > bds/server.properties <<'EOF'
server-name=Basgiath GameTest
gamemode=creative
difficulty=easy
allow-cheats=true
level-name=Basgiath
online-mode=true
server-port=19132
max-players=5
view-distance=6
tick-distance=4
content-log-file-enabled=true
content-log-console-output-enabled=true
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

send "gametest run ${TEST_NAME}"
sleep 20
# The framework runs the test on the next ticks. If the result line has not
# landed yet, give it a bounded extra window before deciding.
for _ in $(seq 1 40); do
  if grep -qiE "dragon_rides.*(pass|fail|error|succeed)" "$LOG" 2>/dev/null; then
    break
  fi
  sleep 1
done

python3 - "$LOG" "$RESULT" "$TEST_NAME" <<'PY'
import re
import sys
from pathlib import Path

log_path = Path(sys.argv[1])
result_path = Path(sys.argv[2])
test_name = sys.argv[3]
test_short = test_name.split(":", 1)[-1]

log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
# Keep the raw evidence. The dedicated server's GameTest wording is not pinned
# by an API, so a mis-parse is diagnosable from result.txt alone.
interesting = [
    line for line in log.splitlines() if re.search(r"gametest|dragon_rides", line, re.I)
][-60:]

test_lines = [line for line in interesting if re.search(re.escape(test_short), line, re.I)]
pass_re = re.compile(r"(passed|pass\b|succeed|success)", re.I)
fail_re = re.compile(r"(failed|fail\b|error|exception|not found|unknown|no such|invalid)", re.I)

passes = [line for line in test_lines if pass_re.search(line)]
# A pass line can carry a harmless failure word ("passed, 0 errors"), so a line
# already read as a pass is never also read as a fail.
fails = [line for line in test_lines if fail_re.search(line) and line not in passes]
# A gametest-scoped failure with no mention of the test name still counts.
fails += [
    line
    for line in interesting
    if re.search(r"gametest", line, re.I) and fail_re.search(line) and line not in passes
]
fails = list(dict.fromkeys(fails))

ok = bool(passes) and not fails
lines = [
    f"gametest_ok={'true' if ok else 'false'}",
    f"gametest_name={test_name}",
    f"gametest_pass_lines={len(passes)}",
    f"gametest_fail_lines={len(fails)}",
]
# First pass line, verbatim, for a stable machine-readable result.
if passes:
    lines.append(f"gametest_result={passes[0]}")
lines.append("gametest_log_begin")
lines.extend(interesting)
lines.append("gametest_log_end")

result_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
PY

if grep -q '^gametest_ok=true$' "$RESULT"; then
  echo "gametest bench ok"
else
  echo "gametest bench failed; raw log excerpt is in $RESULT" >&2
  exit 1
fi
