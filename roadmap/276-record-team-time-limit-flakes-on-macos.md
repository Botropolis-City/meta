# 276. TestRecordTeam's time-limit case can pass the limit without failing, on macOS CI

**Fixed 2026-10-26 (`b16e71f`, r1117). Filed 2026-10-26 (r1112), from CI on `main`. Nobody's call — a flaky test.**

CI run 40387126839, on `6c3ea21` (item 270, slice 5), failed only in `test-macos (macos-26-intel)`'s `make test-unit`:

```
--- FAIL: TestRecordTeam/and_it_has_not_finished_when_the_time_limit_passes/it_should_fail,_saying_it_ran_out_of_time
    teamrecord_test.go:241: An error is expected but got nil.
```

The next commit's run, on `b87d95c`, passed on every job, and nothing between them touches `pkg/demo`, so the case is flaky rather than broken.

## Where

`pkg/demo/teamrecord_test.go`, the case *and it has not finished when the time limit passes*: it sets `limits.Time` to 50 ms of wall clock and a fake teammate busy for a second, and expects the recording to fail with "ran out of time".
Item 254 moved this test onto the recording's own clock for its other cases; this one still races the real clock, and on a slow runner the recording can end some other way before the limit is checked, returning no error.

## The fix

Drive the time limit from the same injected clock as the rest of `TestRecordTeam`, so the limit passes because the test advances the clock, never because a runner is slow; then the case is deterministic on every runner.
Check the stop path's order too, and pin it: going over budget is checked first, then a team that has fallen quiet is done and its recording kept, then the time limit; a real team that genuinely finishes on the poll the limit passes made a complete recording, so failing it would throw paid-for work away (manager, 2026-10-26, correcting this item's first wording, which had the time-out win over everything).
Red first: make the case fail on demand by ordering the clock so the teammate's end and the limit coincide.

## Answered while building

- **The diagnosis and the tree** (session, approved by the manager, 2026-10-26): the case ran on the real clock with a goroutine rewriting the teammate every 2 ms against a 30 ms quiet, so a starved runner let the lead's ended turn plus 30 ms of quiet read as *done*; the interrupted case had the same shape. Both move onto `fakeTeamClock`, and `fakeTerminal`'s real-time `busy` goroutine goes, so nothing in `TestRecordTeam` reads the wall clock.

## Closed

`b16e71f` changes only `pkg/demo/teamrecord_test.go`: every case of `TestRecordTeam` runs on `fakeTeamClock`, and the time-limit case's teammate writes on every poll, so the team can never fall quiet before the limit.
Two new cases pin the stop path's order on the poll the limit passes: a team that falls quiet then is exported and returns no error, and a team that goes over budget then fails naming the budget.
`recordTeam` itself is unchanged.
Red on demand: checking the time limit first in `recordTeam`'s switch fails both new cases.
Green: 50 runs under `-race`, `pkg/demo`, and `make land`'s full gate.

Deviation, flagged for Aria: the item first asked for the time-out to win over everything; the manager reversed that while it was being built, so a team that finishes on the limit keeps its recording.
