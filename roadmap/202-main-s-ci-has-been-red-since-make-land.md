# 202. Main's CI has been red since `make land` landed, and nobody saw

**Open, in progress since 2026-10-22 in the session "item 202". Filed 2026-10-22 (r892) by the roadmap manager, overnight. Nobody's call — a defect; a release cannot be cut while CI is red.**

Depends on: nothing
Landed: slice 1 (`e68c868`, r896).
Landed: slice 2 (`c597409`, r899).

Every `ci` run on `main` since botropolis `4739efc` ([item 186](186-item-sessions-land-side-by-side-and-time-out.md)'s `make land`, 2026-10-20) has failed `test-lint`; the last green run is `c878d4f`. Landings didn't notice because `make land` runs the gate locally, and nothing reads CI afterwards. The release workflow downloads a green run's artifacts, so **no release can be cut until this is fixed**.

Two failures, from `gh run view --log-failed`:

1. **`TestTestTimeouts`, every run since `4739efc`.** The test runs `make -n test-acceptance TEST_TIMEOUT=17m` and expects `-timeout 17m`, but CI's workflow sets `ACCEPTANCE_TIMEOUT: 10m` in the environment, which overrides the Makefile's `ACCEPTANCE_TIMEOUT ?= ${TEST_TIMEOUT}`. So the test depends on the caller's environment. It should run `make` with `ACCEPTANCE_TIMEOUT` (and `TEST_TIMEOUT`) cleared, and also assert that an explicit `ACCEPTANCE_TIMEOUT` wins, which is the behaviour CI relies on.
2. **`TestTheWorkAFrameTakes`, `TestTheLooksAFrameKeeps`, `TestTheStillLayerAFrameKeeps` at `7118d4f`** (run 39752656025), not at `e625afd` before it: the settled metropolis drew 136 commands and 24,312 indices by day — the counts from before [item 193](193-a-still-city-is-redrawn-whole-every-frame.md)'s still layer — against ceilings of 23 and 4,990. Locally, under `make land`, the same tests pass. So on CI's runner the still layer or the look cache is not holding (a key changing every frame on that runner, its clock or time zone, or frames not settling inside [item 194](194-nothing-counts-the-work-a-frame-takes.md)'s window), or the run was flaky. Find which, from CI's own logs, and make the counts hold there as they do here.

## The fix

Fix both, then **make CI's state visible**: `make land` (or the roadmap status line) reports the result of the last `ci` run on `main`, so a red main is seen the day it goes red, not a day later.

Tests: `TestTestTimeouts` passes with `ACCEPTANCE_TIMEOUT` set in the environment and without; the frame tests pass in CI on two consecutive pushes; the last CI result appears where landings look.

## What working it found (2026-10-22)

**The frame counts are flaky on CI, not broken.**
A sweep of 40 `ci` runs on `main` found the frame tests failing at `7118d4f` and again at `e68c868`, with the same counts both times (24,312 indices, 136 commands, 4 switches), and passing in the runs between.
`MostWork` takes each count's maximum per field, so it is one frame drawing 16 of the 30 look runs straight and the next baking them, while the still layer redid three rectangles: one event, sometimes landing inside the settled window.
None of these reproduced it locally: a re-offered identical snapshot from the no-daemon feed's two-second poll, staging the demo 0 to 130 s in the past, `GOMAXPROCS=1`, the light, `litCourse`, or `kill(pid, 0)` liveness.
So slice 2 makes the next failure name its cause: the debug build prints a `look-miss` line with the frame, the tick and the key fields that changed, and the frame tests log those lines for settled frames.
The fix then belongs to the key that flips, not to the test's window (the manager, for Aria).

**A third cause: the acceptance suite outgrew CI's ten-minute timeout.**
Six of the seven runs from `b7e71d3` on ended at 601 s, the package panicking on `ACCEPTANCE_TIMEOUT=10m` with no test hung, and the `--- FAIL` lines that printed before the panic made them look like `TestTestTimeouts` alone.
The suite on CI took 440 s at `4f3ff83`, 423 s at `e8c170a`, 516 to 534 s at `e28335b`, `d100abf` and `e625afd`, 379 s at `7118d4f`, then past 600 s from `b7e71d3` (item 197, slice 3), whose `TestAnUnwatchedCityUnderAStreamOfSnapshots` runs two serial cases of 20 s settling and 30 s streaming.
`ci.yml` still said the suite takes about four and a half minutes.
A test timeout is a hang detector, not a performance target, so CI's goes to 20 minutes, with the comment saying what the suite measures; item 201, which reworks that test, carries a note on its cost (the manager, for Aria).
If the suite keeps climbing, the measuring tests may want a CI job of their own.

**`make land` now says what main's CI last concluded** (slice 3) and records it in botropolis's git common directory, where the status line shows `ci red <commit>`, `ci ?`, or `ci unchecked` when no landing has recorded one, with its age once a record is more than a day old.
