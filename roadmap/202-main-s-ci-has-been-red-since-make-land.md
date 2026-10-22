# 202. Main's CI has been red since `make land` landed, and nobody saw

**Open, in progress since 2026-10-22 in the session "item 202". Filed 2026-10-22 (r892) by the roadmap manager, overnight. Nobody's call — a defect; a release cannot be cut while CI is red.**

Depends on: nothing
Landed: slice 1 (`e68c868`, r896).

Every `ci` run on `main` since botropolis `4739efc` ([item 186](186-item-sessions-land-side-by-side-and-time-out.md)'s `make land`, 2026-10-20) has failed `test-lint`; the last green run is `c878d4f`. Landings didn't notice because `make land` runs the gate locally, and nothing reads CI afterwards. The release workflow downloads a green run's artifacts, so **no release can be cut until this is fixed**.

Two failures, from `gh run view --log-failed`:

1. **`TestTestTimeouts`, every run since `4739efc`.** The test runs `make -n test-acceptance TEST_TIMEOUT=17m` and expects `-timeout 17m`, but CI's workflow sets `ACCEPTANCE_TIMEOUT: 10m` in the environment, which overrides the Makefile's `ACCEPTANCE_TIMEOUT ?= ${TEST_TIMEOUT}`. So the test depends on the caller's environment. It should run `make` with `ACCEPTANCE_TIMEOUT` (and `TEST_TIMEOUT`) cleared, and also assert that an explicit `ACCEPTANCE_TIMEOUT` wins, which is the behaviour CI relies on.
2. **`TestTheWorkAFrameTakes`, `TestTheLooksAFrameKeeps`, `TestTheStillLayerAFrameKeeps` at `7118d4f`** (run 39752656025), not at `e625afd` before it: the settled metropolis drew 136 commands and 24,312 indices by day — the counts from before [item 193](193-a-still-city-is-redrawn-whole-every-frame.md)'s still layer — against ceilings of 23 and 4,990. Locally, under `make land`, the same tests pass. So on CI's runner the still layer or the look cache is not holding (a key changing every frame on that runner, its clock or time zone, or frames not settling inside [item 194](194-nothing-counts-the-work-a-frame-takes.md)'s window), or the run was flaky. Find which, from CI's own logs, and make the counts hold there as they do here.

## The fix

Fix both, then **make CI's state visible**: `make land` (or the roadmap status line) reports the result of the last `ci` run on `main`, so a red main is seen the day it goes red, not a day later.

Tests: `TestTestTimeouts` passes with `ACCEPTANCE_TIMEOUT` set in the environment and without; the frame tests pass in CI on two consecutive pushes; the last CI result appears where landings look.
