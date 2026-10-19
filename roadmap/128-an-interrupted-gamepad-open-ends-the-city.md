# 128. An interrupted gamepad open at start-up ends the city

**Open, in progress since 2026-10-18 in the session "item 128". Filed 2026-10-18 (r655), from what item 125 found. Nobody's call — a defect.**

Under load, a city can exit with status 1 and "gamepad: Open failed: interrupted system call" as it starts.
Ebitengine v2.10.2's `openGamepad` opens every `/dev/input/event*` at start-up and returns `EINTR` from the game loop instead of retrying the open, so a signal arriving during one of those opens ends the city.
Item 125 saw it in 2 of 360 runs at a load of 50 to 70; it reads the host's own input devices, so it can end a real desktop's city as well as a test's, and it keeps item 125's opt-in teardown soak from passing outright.

## The fix

Find whether the city can stop Ebitengine opening gamepads at all — Botropolis reads no gamepad — or retry the open on `EINTR` by a supported option or a newer Ebitengine; failing both, say what is upstream and what we carry.

Tests: a city started while signals arrive repeatedly should start every time; and the teardown soak (`make soak-teardown`) should exit 0 on every run.
