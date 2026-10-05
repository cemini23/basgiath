# Bench and build-dependency fixes

## WorkDir

`/Users/claudiobarone/Projects/dragon-rider-map`

## Context

A real smoke test ran on a RunPod CPU pod against the **official Bedrock dedicated server, `bedrock-server-1.26.52.3`**. The pack and the world both passed:

```
server_started=yes
pack_error=none
SPAN=true   GAP45=true   GAP46=true   COLUMN=true
```

Pack load is clean and the span, both gaps, and the column are correct on the real server.

`blocks_ok=false` comes from the bench itself. Four defects, all in the test and build tooling, none in the world.

## Plan

### 1. The control probe is invalid — `scripts/bench_bds.sh`

The script sets a control stone at `(0,79,0)`, **then** runs the build, **then** probes it. But `_ground()` in `scripts/zones/parapet.py` fills relative `y=-1` — absolute 79 with the anchor at `(0,80,0)` — with `grass_block` across the whole 171×151 footprint. The build overwrites the control, so `CTRL_STONE` can never be true.

Move the control **set** to immediately before its **probe**, after the build has run:

```bash
send "setblock 0 79 0 stone"
sleep 1
probe CTRL_STONE 0 79 0 stone
```

The control still proves what it is for: that the probe detects a block that is actually there. Keep `CTRL_NOT_GOLD` where it is.

### 2. The fallback calls a hard-coded stage count — `scripts/bench_bds.sh`

`for n in $(seq -w 1 20)` is stale. The build has **32** stages, so 21 to 32 never run in the fallback path. This is the same defect class already fixed in `scripts/test_release.py`, still live here.

Derive the count from the extracted pack, right after the world is unzipped and before it is moved:

```bash
STAGES="$(find worlds/Basgiath/behavior_pack/functions/basgiath -name 'stage_*.mcfunction' | wc -l | tr -d ' ')"
if [ "$STAGES" -lt 1 ]; then echo "no stage functions in the world" >&2; exit 1; fi
```

Then loop `for n in $(seq -w 1 "$STAGES")`. Adjust the padding if a run needs more than two digits.

### 3. The build needs Pillow — document and check it

`scripts/build_dragon_model.py` imports `PIL`. On a bare Ubuntu image:

```
ModuleNotFoundError: No module named 'PIL'
```

Add the requirement to `README.md`'s build steps (`python3 -m pip install Pillow`, or the distro package `python3-pil`), and make `scripts/package.sh` check for it and exit with a clear message instead of a traceback.

### 4. The build needs zip — document and check it

`scripts/package.sh` line 17 calls `zip`. On a bare Ubuntu image:

```
scripts/package.sh: line 17: zip: command not found
```

Add the requirement to `README.md` and check for it in `package.sh` with a clear message.

Put the two dependency checks together, near the top of `package.sh`, so a clean machine fails once with a readable message rather than twice with tracebacks.

## Success criteria

1. `bash scripts/package.sh` still exits 0 on this machine and writes both artifacts.
2. On a machine without `zip`, `package.sh` prints a clear message naming the missing tool, and exits non-zero. Do not silently continue.
3. `bench_bds.sh` sets the control after the build and derives the stage count. No `1 20` remains.
4. `grep -c 'seq -w 1 20' scripts/bench_bds.sh` returns 0.
5. All gates pass: `validate.sh`, `node --check main.js`, `package.sh`, `test_release.py`, `bench_static.py`.

## Verify

```
python3 scripts/build_map.py
bash scripts/validate.sh
node --check addon/behavior_pack/scripts/main.js
bash scripts/package.sh
python3 scripts/test_release.py
python3 scripts/bench_static.py
```

`bench_bds.sh` cannot run on this Mac. It is verified by the re-run on RunPod, not here.

## NEVER

- Do not change `addon/behavior_pack/manifest.json`. Keep the two 2.0.0 deps. No Beta APIs.
- Do not weaken a check to make it pass. Fix the check, not the result.
- Do not remove the control probes. A control is required.
- Do not use a person name, a dragon name, or book text.
- Do not print, write, or commit a key.
- Do not commit or push.
