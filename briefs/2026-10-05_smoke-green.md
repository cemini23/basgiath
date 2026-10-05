# Smoke test — green on the official Bedrock server

**Commit:** `0152ae4` · **Ran:** 2026-10-05, 02:10 UTC

`scripts/bench_bds.sh` boots the official **Bedrock dedicated server** and asks it about the built world. A Mac cannot run that binary, so this ran on a RunPod x86_64 CPU pod. The pod cloned `cemini23/basgiath` over HTTPS, ran `scripts/package.sh`, then ran the bench.

## Result

```
server_started=yes
pack_error=none
TICK_SPAN=false
CTRL_STONE=true
CTRL_NOT_GOLD=false
SPAN=true
GAP45=true
GAP46=true
COLUMN=true
LECTERN_SCROLL=true
LECTERN_ROLL=true
blocks_ok=true
bds bench ok
BENCH_EXIT=0
```

## What this proves

- **`pack_error=none`** — the behavior pack loads clean on the current Bedrock release. No manifest error, no script error, no bad command.
- **`server_started=yes`** — the `.mcworld` loads.
- **`SPAN`, `GAP45`, `GAP46`, `COLUMN`** — the Parapet deck is `stone_bricks`, both gap blocks are air, and the column above is clear.
- **`CTRL_STONE=true`** and **`CTRL_NOT_GOLD=false`** — the probes read real blocks. The control is placed after the build and probed immediately, so it proves the probe mechanism, not the map.
- **`LECTERN_SCROLL` and `LECTERN_ROLL`** — a lectern stands at both keeper spots, `(128, 81, 34)` and `(50, 79, 123)` in absolute terms. These are the two naming desks.

`TICK_SPAN=false` is expected. The tick-driven build waits on a player, the bench has none, and the script falls back to calling every stage function directly. That fallback now counts the stages rather than naming 20 of them.

## One warning to expect

The log carries lines like this:

```
[JJJJ-MM-DD HH:MM:SS:mmm ERROR] Detect position: 128 81 34 is out of range.
Execute subcommand unless block test failed.
```

The first line is a warning that the probe position sits outside the bench's ticking area. The second line is the probe succeeding. A lectern is there. Do not read the warning as a failure.

## What this does not prove

The picture, the dragon texture, the signet form, the two keeper forms, flight feel, and a phone crossing. Those need a client. `bench_static.py` and `test_release.py` cover the shape of the code; nothing here has rendered a frame.

## Cost and cleanup

Five-pod history across the debugging. This run: one pod, $0.14/hr, about 90 seconds. Verified `pods now: []`, `pods after: []`.

## How to re-run

On any Linux host, from the repo root:

```
bash scripts/package.sh
bash scripts/bench_bds.sh
```

It needs `python3`, `python3-pil`, `zip`, `unzip`, and `curl`. `package.sh` names whichever is missing.
