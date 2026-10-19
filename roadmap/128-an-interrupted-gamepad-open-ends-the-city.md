# 128. An interrupted gamepad open at start-up ends the city

**Fixed 2026-10-18 (`bb837cb`, r666). Filed 2026-10-18 (r655), from what item 125 found. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`bb837cb`, r666).

Under load, a city can exit with status 1 and "gamepad: Open failed: interrupted system call" as it starts.
Ebitengine v2.10.2's `openGamepad` opens every `/dev/input/event*` at start-up and returns `EINTR` from the game loop instead of retrying the open, so a signal arriving during one of those opens ends the city.
Item 125 saw it in 2 of 360 runs at a load of 50 to 70; it reads the host's own input devices, so it can end a real desktop's city as well as a test's, and it keeps item 125's opt-in teardown soak from passing outright.

## The fix

Find whether the city can stop Ebitengine opening gamepads at all — Botropolis reads no gamepad — or retry the open on `EINTR` by a supported option or a newer Ebitengine; failing both, say what is upstream and what we carry.

Tests: a city started while signals arrive repeatedly should start every time; and the teardown soak (`make soak-teardown`) should exit 0 on every run.

## Answered while building

- **Nothing upstream to switch off or upgrade to** (item 128's session, 2026-10-18): no option, environment variable or build tag stops Ebitengine opening `/dev/input` on Linux, and the newest releases handle the open identically. The open takes the evdev device's lock interruptibly, so a signal reaching the opening thread while another process holds it returns `EINTR`, which restarting cannot help; Ebitengine opens on the main thread, where Go delivers its preemption signals.
- **The fix** (manager, 2026-10-18): asynchronous signals are blocked on that one thread for the life of the game loop and the old mask restored after, on Linux; process-directed signals still reach the program through its other threads, and synchronous ones stay unblocked. The proof under signals is an opt-in soak beside the teardown soak, red before and green after, and it says so when it skips for want of an input device.

## What was measured

Ebitengine has a mode that never opens `/dev/input`, its virtual gamepads, but only its VM-guest backend uses it: the desktop loop always asks for real devices (`internal/ui/ui_glfw.go`, `gamepad.Update(nativeWindow, nil)`).
`openGamepad` is unchanged in v2.10.5, the newest patch release, and in v2.11.0-alpha.
Nothing was reported upstream, at Aria's word.

The kernel side is `evdev_open`, which takes the device's mutex with `mutex_lock_interruptible`: a signal pending on the opening thread while it waits returns `EINTR`, and `SA_RESTART` does not restart it.
A probe outside the repository kept four processes opening every `/dev/input/event*` while it flooded its own main thread with `SIGURG` by `tgkill`.
Unblocked, it hit 3, 0, 2 and 5 `EINTR`s in about 270 opens per five-second run; with `SIGURG` blocked on that thread, none in four runs.

What we carry is `pkg/sighold`, one function that blocks the standard asynchronous signals on the calling thread and returns the restore, which `render.Run` wraps around `RunGameWithOptions`.
Synchronous signals and the real-time ones are left alone, and on any other system it does nothing.

`make soak-gamepad` (`TestStartUnderSignals`) starts 40 `--home` screenshot cities one after another while the test keeps the input devices busy and floods each city's main thread with `SIGURG`.
Before the fix, 12 of 40 exited 1 with "gamepad: Open failed: interrupted system call"; after it, 40 of 40 exited 0.
`make soak-teardown` then passed three times running, 360 of 360 runs, at a load of 65 to 88.

## Closed

Fixed in botropolis `bb837cb` (r666): the city's main thread holds asynchronous signals for the life of the game loop, so an open of an input device can no longer be interrupted.
`make soak-gamepad` shows it, 12 failures in 40 before and none after, and `make soak-teardown` now exits 0, 360 runs of 360.
No deviation from what the item asked: Ebitengine still opens the gamepads, because nothing upstream lets the city stop it, and what we carry is `pkg/sighold`, about twenty lines.
The gamepad soak is opt-in like the teardown soak, at the manager's word, so `pkg/sighold`'s unit test is what guards the fix on every run.
