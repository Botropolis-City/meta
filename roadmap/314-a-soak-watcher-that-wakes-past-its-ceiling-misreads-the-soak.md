# 314. A soak watcher that wakes past its ceiling misreads the soak, and a failed hide reads as no frames drawn

**Open, in progress since 2026-10-28 in the session "item 314". Filed 2026-10-28 (r1196), from 0.3.3's soaks, through the performance manager's report (`90f6787`). Nobody's call — two defects.**

Aria's laptop slept, lid closed, from 19:38 to 01:03 on 2026-10-27, which froze the runner watching soak 5 (server 3101537).
The soak ended on the box at about 19:47, inside its ceiling of 21:41; the runner woke at 01:03, already past the ceiling, declared *the run reached its ceiling … with the soak still running* without fetching again, and cancelled.
Aria ruled (2026-10-28): the laptop keeps sleeping as usual; the runner catches up when it wakes, and the booked cancellation caps the worst case — the soak depends on the box, not on the laptop staying awake.

Separately, `judge_soak` (`performance/tools/perf.py`, about line 632) reads `frames_at_hide` whenever a hide was asked for, but a failed hide never writes it, so soak 5's report says *the visible phase drew no frames* beside `frames_at_end: 863640`.

## The fix

1. On every wake of its watch loop, and before acting on the ceiling, the runner fetches the bucket once and acts on what the soak actually did: an ended soak is reported as ended, with its report, and then cancelled.
2. The runner notices a gap in its own clock (a sleep) and says so in its log, with how long.
3. When `hide_failed_at_s` is set, the visible phase is the whole run, and `judge_soak` uses `frames_at_end`.
4. Tests: a watcher whose clock jumps past the ceiling while the bucket holds an ended soak reports it ended and cancels once; one whose bucket shows a soak still running reports that; `perf_test.py` covers a failed hide with frames drawn.
