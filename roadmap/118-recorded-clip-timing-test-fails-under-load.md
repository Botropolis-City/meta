# 118. The recorded-clip timing test fails under load

**Open. Filed 2026-10-18 (r628), from what items 102 and 108 found. Nobody's call — a defect.**

`TestRecordedClipKeepsTheScenesTime`, item 113's acceptance test that a 3-second clip recorded at 10 fps advances the city's clock by 3 s within one tick, failed once in a full uncached run in item 102's worktree (at `fa44392`) and once in item 108's under a load of about 29 on 14 cores; each passed when run alone.

Item 113's fix makes frames and ticks one-to-one while recording, so a clip's time should not depend on load at all: a failure under load means either the lockstep leaks somewhere (a draw or an update that slips past the gate when the machine is slow), or the test measures something other than frames — wall time, a timeout, or the recorder's own exit — that load can move.
Either way it is found, not retried: item 104's flaky unstage and item 114's leaked directory were both real bugs.

## Done when

The cause is named here, the test passes `-count=50` with other suites running beside it at a load like the one it failed under, and a clip's reported city time is exactly its frame count over its rate whatever the load.
