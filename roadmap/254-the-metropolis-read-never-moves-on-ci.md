# 254. On CI's Linux runner, the metropolis's history read never moves, so `main` is red

**Fixed 2026-10-26 (`ce509e8`, r1066). Filed 2026-10-25 (r1047), found by item 249's session. Nobody's call — a defect.**

Depends on: 249
Landed: slice 1 (`e04ae93`, r1060).
Landed: slice 2 (`ce509e8`, r1066).

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

## Answered while building

- **How urgent** (Aria, 2026-10-26): *"we should do immediately. We should always keep ci green."* This item comes before other work, and a red `main` is fixed before anything else lands on top of it.
- **The cause** (item 254's session, 2026-10-26): a headless capture takes a stopped session's heft from the statistics store, whose first ingest pass runs at item 138's background priority, nice 10 and Linux's idle I/O class; every SQLite commit fsyncs from that thread, and on the runner `/tmp` is a real disk whose scheduler honours the idle class, so while parallel cities write frames the pass is never served. Locally `/tmp` is tmpfs and the NVMe scheduler is `none`, so the class does nothing there. The fix (manager, approved): only a pass paced for part of the clock lowers its priority, so a capture's full-speed passes keep normal priority, and the daemon and the windowed city keep the idle class.
- **A second red** (manager, 2026-10-26): `main`'s unit stage also fails on item 105's `TestRecordTeam`, a wall-clock assertion ("661µs is not greater than or equal to 30ms"); this item fixes it first, with an injected clock, so the acceptance stage runs at all.

## Closed

`main`'s CI is green again from `ce509e8` (run 40295691276, every job), and the three metropolis captures pass on the runner: `TestTheLooksAFrameKeeps` in 29.7 s, `TestTheStillLayerAFrameKeeps` in 42.4 s and `TestTheWorkAFrameTakes` in 62.1 s.

The stall was step 1's first kind: snapshots arriving with one session never read.
A headless capture keeps its state private, so it takes a stopped session's heft from the statistics store rather than the whole read, and the metropolis has exactly one partial stopped session; the fourteen live ones resolve through the later read.
A probe staging the metropolis locally showed that one session partial until the store's first ingest pass finished, about three loads in.
That pass ran at item 138's background priority, and each SQLite commit fsyncs from its thread in the idle I/O class, on `/tmp`, which on the runner is a real disk.

Slice 1 (`e04ae93`) fixed the red that hid this one: `TestRecordTeam`'s fake teammate rewrote its transcript at the same size, and the runner's coarse modification times hid the rewrites.
The recorder now runs on a `TeamClock`, and the test asserts in polls on a fake clock with a teammate whose transcript grows.
Its CI run passed the unit stage and failed only the three metropolis captures.

Slice 2 (`ce509e8`) lowers a pass's priority only when its pace is for part of the clock (`pace.lower`, `pkg/state/pace.go`), so a capture's full-speed passes keep normal CPU and I/O priority, and the daemon and the windowed city keep the idle class.
`TestAPaceLowersOnlyAPacedPass` and `TestAFullSpeedLoaderKeepsItsPriority` (`pkg/state/pace_priority_internal_linux_test.go`) were red before the fix, with the store's ingest and the whole read running in the idle class, and green after.

Deviation, flagged for Aria: step 2 asked for the stall to be reproduced under the runner's I/O class behaviour.
This machine's `/tmp` is tmpfs and its NVMe scheduler is `none`, and switching the scheduler needs root, so the red test checks the I/O class the passes run in rather than a starved disk; the runner's green run is the evidence that the class was the cause.
The daemon keeps the idle class on purpose (item 138), so on a disk whose scheduler honours it, a person's statistics store can still wait behind a steadily busy disk; nobody has reported that.
