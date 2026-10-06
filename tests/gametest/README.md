# GameTest: the dragon is rideable and flyable

Dev-only. This pack is **not** part of the add-on and is **not** shipped. It
lives under `tests/` on purpose; `addon/` and `dist/basgiath.*` stay untouched.

## What the test proves

`basgiath:dragon_rides` spawns `dragon_rider:dragon` on a small test pad and
asserts, in order:

1. the entity exists after the spawn,
2. it has `minecraft:rideable`, so a cadet can mount it,
3. it has exactly one seat, and seat 0 is the controlling seat, so the mounted
   cadet steers it.

If all three hold, the test calls `test.succeed()`. It is the only test in the
pack. It replaces "a human mounted a dragon in a client and it felt right" with
a check a machine can repeat.

## What it cannot prove, and why

Flight needs a client. `minecraft:input_air_controlled` is the component that
turns a rider's input into flight, but the script API does not bind it, so
`Entity.getComponent` and GameTest's `assertEntityHasComponent` both report it
missing on a dragon that really has it. Asserting it here would fail for the
wrong reason. A human riding the dragon is still the only check for flight.

## Run it in a client

1. Build the test world: `python3 scripts/build_gametest_world.py`
   (writes `dist/gametest.mcworld`).
2. Open the world in Minecraft Bedrock. The world already has the **Beta
   APIs** and **GameTest** experiments on, and both behavior packs plus the
   shipped resource pack enabled.
3. Run `/gametest run basgiath:dragon_rides`.
4. The chat and the content log report the test result.

To drive it from a hand-made Creative flat world instead: turn on the
**Beta APIs** and **GameTest** experiments, enable the shipped behavior pack
and resource pack, then enable this pack
(`tests/gametest/behavior_pack/`), and run the same command.

## Run it on the bench

`scripts/bench_gametest.sh` downloads the official Linux Bedrock dedicated
server, boots it against `dist/gametest.mcworld`, sends
`gametest run basgiath:dragon_rides` on the console, and writes
`gametest_ok=true|false` to `result.txt` in its work directory
(`$BENCH_GAMETEST_WORK/result.txt`, default `/tmp/basgiath-gametest`).

```sh
python3 scripts/build_gametest_world.py
bash scripts/bench_gametest.sh
```

On macOS the script exits 2, like `scripts/bench_bds.sh`: the server binary is
Linux-only. Run it on a Linux box or a RunPod pod.

`result.txt` keeps the last 60 log lines that mention `gametest` or
`dragon_rides`, verbatim. The dedicated server's exact GameTest result wording
is not an API, so the bench reports success only on a `dragon_rides` pass line
with no fail line, and the raw excerpt lets the next run tighten the parser if
the wording differs.
