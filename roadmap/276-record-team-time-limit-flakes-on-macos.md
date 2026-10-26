# 276. TestRecordTeam's time-limit case can pass the limit without failing, on macOS CI

**Open. Filed 2026-10-26 (r1112), from CI on `main`. Nobody's call — a flaky test.**

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
Check the stop path too: when the limit passes, `record` must return the time-out error whatever else ends the run at the same moment.
Red first: make the case fail on demand by ordering the clock so the teammate's end and the limit coincide.
