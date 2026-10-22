# 204. The ingest shares the daemon's process, so its CPU priority can't be lowered safely on macOS

**Open. Filed 2026-10-22 (r901), from item 200's closing deviation, so it is not lost when item 200 closes. Nobody's call — a known way to meet "at background priority" on macOS.**

Depends on: 200

[Item 200](200-first-launch-runs-at-full-priority-on-macos.md) measured every macOS priority option against [item 138](138-state-changes-lag-while-statistics-backfill.md)'s inversion on CI's two macOS runners, three runs a cell. The background-band policies froze the daemon on Apple silicon: `PRIO_DARWIN_BG` and QoS background in 3 of 3 runs, `PRIO_DARWIN_BG` + `IOPOL_THROTTLE` in 2 of 3 (and starved in the third), because Go's stop-the-world waits on the starved ingest thread and the whole process stops. What shipped is `IOPOL_THROTTLE` alone: disk reads throttled, CPU priority left as it is.
So [item 159](159-first-launch-takes-the-machine.md)'s "at background priority" holds on macOS for I/O and not for CPU.

## The fix

Run the first-launch ingest (and the settled passes, if they fit) in a **child process** at background priority, writing to the statistics store, so its threads never share a garbage collector with the daemon's serving: a starved child can't stop the daemon. On Linux it would also let the child run at nice 19, not 10.

Tests: item 138's inversion test, on Linux and on CI's macOS runners, with the child at full background priority (`PRIO_DARWIN_BG` on macOS): the state-change bound holds and the ingest makes progress; a child killed part-way leaves the store consistent (item 159's checkpoints); the daemon restarts a child that dies. Background variants that need Apple silicon's efficiency cores still need one run on a real Mac, as item 200 records.
