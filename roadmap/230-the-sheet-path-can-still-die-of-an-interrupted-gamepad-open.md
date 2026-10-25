# 230. The sheet path can still die of an interrupted gamepad open

**Open. Filed 2026-10-24 (r969), found by item 226's session when a landing failed. Nobody's call — a defect.**

Item 226's landing of the [item 227](227-testtoolchainpins-fails-when-the-machines-go-is-not-the-pin.md) fix failed in `TestTheStillCityMatchesTheCityDrawnDirectly` (night): `botropolis-demo` exited 1 with `gamepad: Open failed: interrupted system call`, at a load average of about 11.

**The mechanism.** [Item 128](128-an-interrupted-gamepad-open-ends-the-city.md) fixed this for the city: `pkg/render/run.go` takes `sighold.Hold()` around `ebiten.RunGameWithOptions`, so a signal cannot interrupt the gamepad's `open` of `/dev/input` at start-up.
`pkg/render/sheet.go:178`, the sheet and `--check-frames` path that `botropolis-demo` runs, calls `ebiten.RunGame` with no hold, so it can still fail the same way.
It will fail more often once [item 226](226-the-acceptance-suite-takes-sixteen-minutes-to-land.md)'s slice 2 runs behaviour tests in parallel, since more processes open `/dev/input` at once.

**The fix.** The same hold around the sheet's `RunGame`, released as `run.go` releases it.
Its red test is item 128's soak (`make soak-gamepad`) pointed at the sheet path.
Look for any other `ebiten.RunGame` call without the hold, and fix it in the same commit.

Item 226's session fixes it, since it is in that item's landing path, and cites this item in the commit.

## Answered while building

- **What counts as the green proof** (manager, 2026-10-24): with the fix, a soak run waits out the evdev mutex the soak's four openers hammer instead of failing, so one run takes about 7 minutes against about 85 s unfixed, and 40 runs would hold the landing lock about five hours. So 12 clean runs, at a moment when no landing is queued: unfixed failed 17 of 40 (42%), so 12 clean runs leave about a 0.1% chance a broken fix passes. Before them, a sheet draw with no soak running, before and after the fix, shows the fix does not slow a normal start; if it does, that is a regression to bring back. Item 128's city soak also does not finish 40 runs in 20 minutes on this machine at its current device count, which this item records rather than fixes.
- **The rest of the green proof** (manager, 2026-10-24): two clean signalled sheet draws so far against 17 of 40 failing unfixed; the bar stays at 12 consecutive clean runs. The day never had the hour or more of quiet lock it needs, so the performance manager, which already runs measurements in quiet windows, runs the remaining runs in the first one (`SOAK_GAMEPAD_RUN=TestStartUnderSignals/when_the_demo_tool flock /tmp/botropolis-land.lock make soak-gamepad`, which logs each run), records them here, and the item closes only when twelve in a row pass.
- **Soak runs, continuing** (the performance manager, 2026-10-24, holding the lock, at `76b7597`; log `~/.local/state/botropolis-perf/soak-230-76b7597-20261024-183528/`): runs 0–6 clean, in 4m43s to 5m33s each, 9 consecutive clean with the two before. A Go test timeout partway through the invocation is not a failed start and does not break the count; the item closes at 12 consecutive clean starts.
