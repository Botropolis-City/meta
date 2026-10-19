# 128. An interrupted gamepad open at start-up ends the city

**Open, in progress since 2026-10-18 in the session "item 128". Filed 2026-10-18 (r655), from what item 125 found. Nobody's call — a defect.**

Under load, a city can exit with status 1 and "gamepad: Open failed: interrupted system call" as it starts.
Ebitengine v2.10.2's `openGamepad` opens every `/dev/input/event*` at start-up and returns `EINTR` from the game loop instead of retrying the open, so a signal arriving during one of those opens ends the city.
Item 125 saw it in 2 of 360 runs at a load of 50 to 70; it reads the host's own input devices, so it can end a real desktop's city as well as a test's, and it keeps item 125's opt-in teardown soak from passing outright.

## The fix

Find whether the city can stop Ebitengine opening gamepads at all — Botropolis reads no gamepad — or retry the open on `EINTR` by a supported option or a newer Ebitengine; failing both, say what is upstream and what we carry.

Tests: a city started while signals arrive repeatedly should start every time; and the teardown soak (`make soak-teardown`) should exit 0 on every run.

## Answered while building

- **Nothing upstream to switch off or upgrade to** (item 128's session, 2026-10-18): no option, environment variable or build tag stops Ebitengine opening `/dev/input` on Linux, and the newest releases handle the open identically. The open takes the evdev device's lock interruptibly, so a signal reaching the opening thread while another process holds it returns `EINTR`, which restarting cannot help; Ebitengine opens on the main thread, where Go delivers its preemption signals.
- **The fix** (manager, 2026-10-18): asynchronous signals are blocked on that one thread for the life of the game loop and the old mask restored after, on Linux; process-directed signals still reach the program through its other threads, and synchronous ones stay unblocked. The proof under signals is an opt-in soak beside the teardown soak, red before and green after, and it says so when it skips for want of an input device.
