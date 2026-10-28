# 314. A soak watcher that wakes past its ceiling misreads the soak, and a failed hide reads as no frames drawn

**Fixed 2026-10-28 (`29cdbcf`, r1161 of meta). Filed 2026-10-28 (r1196), from 0.3.3's soaks, through the performance manager's report (`90f6787`). Nobody's call — two defects.**

Aria's laptop slept, lid closed, from 19:38 to 01:03 on 2026-10-27, which froze the runner watching soak 5 (server 3101537).
The soak ended on the box at about 19:47, inside its ceiling of 21:41; the runner woke at 01:03, already past the ceiling, declared *the run reached its ceiling … with the soak still running* without fetching again, and cancelled.
Aria ruled (2026-10-28): the laptop keeps sleeping as usual; the runner catches up when it wakes, and the booked cancellation caps the worst case — the soak depends on the box, not on the laptop staying awake.

Separately, `judge_soak` (`performance/tools/perf.py`, about line 632) reads `frames_at_hide` whenever a hide was asked for, but a failed hide never writes it, so soak 5's report says *the visible phase drew no frames* beside `frames_at_end: 863640`.

## The fix

1. On every wake of its watch loop, and before acting on the ceiling, the runner fetches the bucket once and acts on what the soak actually did: an ended soak is reported as ended, with its report, and then cancelled.
2. The runner notices a gap in its own clock (a sleep) and says so in its log, with how long.
3. When `hide_failed_at_s` is set, the visible phase is the whole run, and `judge_soak` uses `frames_at_end`.
4. Tests: a watcher whose clock jumps past the ceiling while the bucket holds an ended soak reports it ended and cancels once; one whose bucket shows a soak still running reports that; `perf_test.py` covers a failed hide with frames drawn.

## Fixed

`29cdbcf` (r1161 of meta):

- `watch()` in `testing/machines/machines` reads the bucket first on every turn and acts on the ceiling only after.
  An ended soak returns its exit code, so the run fetches its report and cancels the box once.
  At the ceiling, a soak the bucket shows running is reported still running,
  and a bucket that cannot be read is reported as not knowing whether the soak ended, rather than as still running.
- `watch()` takes an injected clock.
  A sleep is wall time the monotonic clock did not see, since Linux's monotonic clock stops in suspend;
  over a minute, the runner logs *this runner slept for H h M min, from … to …*.
- `judge_soak` counts `frames_at_end` when `hide_failed_at_s` is set.

Tests: `testing/machines/watch_test.py` drives `watch()` on a fake clock and bucket, with no sleeps: a jump past the ceiling with an ended soak, a running one, and an unreadable bucket, a run with no gap, and the gap measure.
An acceptance case in `machines_test.py` whose ceiling (36 ms) passes during the stubbed set-up, with an ended soak in the bucket, exits 0, fetches the report and cancels once; the old runner exited non-zero there.
`perf_test.py` covers a failed hide with frames and with none.

Deviations, for Aria:

- The ended-soak messages repeat a little: the watcher says the soak ended and `run_soak` still says *perf-soak exited N*.
- The new acceptance case failed once (two failures, one error) in its first run after the change, then passed 18 times running alone and once in the full `make test`; the cause was not found.
