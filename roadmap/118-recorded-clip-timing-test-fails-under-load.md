# 118. The recorded-clip timing test fails under load

**Fixed 2026-10-18 (`5a99911`, r655; `aa46d34`, r668). Filed 2026-10-18 (r628), from what items 102 and 108 found. Nobody's call — a defect.**

`TestRecordedClipKeepsTheScenesTime`, item 113's acceptance test that a 3-second clip recorded at 10 fps advances the city's clock by 3 s within one tick, failed once in a full uncached run in item 102's worktree (at `fa44392`) and once in item 108's under a load of about 29 on 14 cores; each passed when run alone.

Item 113's fix makes frames and ticks one-to-one while recording, so a clip's time should not depend on load at all: a failure under load means either the lockstep leaks somewhere (a draw or an update that slips past the gate when the machine is slow), or the test measures something other than frames — wall time, a timeout, or the recorder's own exit — that load can move.
Either way it is found, not retried: item 104's flaky unstage and item 114's leaked directory were both real bugs.

## Done when

The cause is named here, the test passes `-count=50` with other suites running beside it at a load like the one it failed under, and a clip's reported city time is exactly its frame count over its rate whatever the load.

## The cause

**Not a leak in the lockstep: the city segfaulted at teardown, which is item 125** (item 118's session, 2026-10-18).
`coredumpctl` holds exactly two core dumps whose command line is this test's own (`city --record …/TestRecordedClipKeepsTheScenesTime…/frames --seconds 3 --fps 10`), at 15:21 and 16:16 MDT on 2026-10-18, both before this item was filed at 16:32 and either side of item 102's `fa44392` at 16:00.
Both faulted on a thread libc started, executing code in a mapping that was no longer there, at the same page offsets (`…17a507`, `…e2704d`, `…dddb1e`) as the item 125 dumps from screenshot and `--home` runs: llvmpipe drawing the last frame while GLFW unloaded EGL under it.
So the city exited 139 and the test's `require.NoError` failed; the clip's timing was never what failed, and item 125's fix (`5a99911`, r655) already covers it.
Reading the lockstep, no path counts a draw without a tick or a tick without a draw, and the report counts ticks, not wall time.

Also measured, not a cause: at a load of about 70 a 3-second clip takes 70–120 s of wall time, so `-count=15` alone overruns `go test`'s default 10-minute package timeout.
A long soak of this test needs `-timeout`.

## Answered while building

- **The diagnosis, and the test tightened rather than code changed** (manager, 2026-10-18): approved — the filed cause was not it, so the fix is item 125's commit plus asserting the clip's city time exactly, with a red mutation and a soak at load beside other suites.

## Measured

- **Red**: with both halves of the lockstep removed — `startTick`'s hold and `SyncWithFPS` — 30 frames spanned 14.867 s of the city's clock under load, five times fast.
  With either half alone the test stays green, so each is enough by itself and they are belt and braces.
- **The soak**: `-count=50` on main with item 125's fix, beside `go test ./pkg/...` and `./testing/integration/...` looping the whole time, at a load of 25 to 97 (mean 65) on 14 cores: 50 of 50 passed, each reporting exactly 3.000 s for its 30 frames, in 36 minutes.
  The integration suite beside it failed 10 of 211 runs at item 124's unstage deadline, because the soak's tree predated item 124's fix (`e2037b2`); none were this test.

## Closed

Fixed by item 125's `5a99911` (r655), which is what the two failures were, and by `aa46d34` (r668), which tightens the test to the item's "exactly".
`TestRecordedClipKeepsTheScenesTime` now asserts that the reported city time equals the written frames over the rate, where it allowed a tick either way.
The soak and the red are under *Measured*: 50 of 50 at a load of 25 to 97 beside the unit and integration suites, and red at 14.867 s for 30 frames with the lockstep removed.
No code changed, since the lockstep never leaked.

For Aria: a full acceptance run with this change, at load, failed only `TestHeadlessCitiesStartedTogether`, on item 128's gamepad `interrupted system call`, not this test.
