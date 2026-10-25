# 254. On CI's Linux runner, the metropolis's history read never moves, so `main` is red

**Open. Filed 2026-10-25 (r1047), found by item 249's session. Nobody's call — a defect.**

Depends on: 249

`main`'s Linux CI has failed `test-lint` on every push since botropolis `73d7d69` ([item 240](240-the-metropolis-demo-reads-as-a-light-user.md)'s metropolis filled with turns at a scenario's pace); the last green run was at `70348ca`.
The failing tests all film the metropolis demo through `frameLog`: `TestTheLooksAFrameKeeps`, `TestTheStillLayerAFrameKeeps` and `TestTheWorkAFrameTakes`.
With [item 249](249-captures-fail-under-load-at-the-30-second-open-ceiling.md)'s stall ceiling in place (CI run 40239163680, at `8602a6f`), every one of their subtests fails with "the read made no progress for 30s", each city at about 34 s: on the runner the read does not run slowly, it never moves at all.
The staged metropolis is 30 files and 4.2 MiB, which no runner needs 30 s to read; locally the same tests pass at a load of 61–67, and on two pinned CPUs at a load of about 80.

Suspects, from item 249's session: the whole read's pass waits on the lane it shares with the later read, which yields to the loader's gate while a 2-second poll's `Load` holds it; or the read's idle I/O class starves on the runner's disk.

## The fix

1. Read the stall message item 249's second slice adds (the sessions still partial, the scan, the snapshots since the read last moved) from the first CI run after it lands, and say here which kind of stall it is: snapshots arriving with nothing read, or no snapshot at all.
2. Reproduce it locally under the runner's conditions (its CPU count, its I/O class behaviour, its disk), then fix the cause rather than the test.
3. Turn CI green, and say which commit did.

Tests: a test that reproduces the stall red before the fix and green after; CI on `main` green.

## Answered while building

- **It is snapshots arriving with one session never read** (item 249's session, 2026-10-25, from CI run 40242782845 at `e1d83be`): all ten failing cities in `TestTheStillLayerAFrameKeeps` and `TestTheWorkAFrameTakes` said "1 sessions' hefts still partial, 0 bytes of the scan done, 18 snapshots since it last moved". So the feed keeps polling every 2 s, the read is below the scan's 32 MiB threshold, and every session but one has its heft read whole. The read does not stall as a whole: one session's heft never resolves on the runner. That points away from the shared lane and the idle I/O class, which would hold back every session, and toward something particular to one staged session, such as a stopped session whose file key changes on every load so each pass reads it again, or a session whose usage is partial but which never reaches the whole read. `TestTheLooksAFrameKeeps` passed in that run.
