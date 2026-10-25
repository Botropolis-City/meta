# 225. TestThreadCPU fails under load

**Fixed 2026-10-25 (`58583b8`, r1022). Filed 2026-10-24 (r967), seen by item 217 while landing. Nobody's call — a defect.**

`botropolis/pkg/daemon/cpu_linux_test.go`'s `TestThreadCPU` spins a thread for 100 ms of wall time and asserts the thread's own CPU clock counted at least 25 ms. At a load average of about 11, item 217's first `make land` failed with "15.92ms is not greater than or equal to 25ms"; the same tree passed on the next run. Under load the scheduler gives the spinning thread less than a quarter of the wall time, so the assertion measures the machine, not the code. [Item 209](209-cost-gates-fail-landings-on-a-busy-machine.md) fixed the same shape in the cost gates by counting work instead of time.

## The fix

Assert on what the code controls: spin until the thread's own clock reads at least 25 ms (with a generous wall-clock timeout that fails loudly), and assert the reported figure is within a small tolerance of an independent reading of the same clock (`CLOCK_THREAD_CPUTIME_ID`, or `/proc/thread-self/stat`), so a load spike lengthens the test instead of failing it. The sleeping case's upper bound is unaffected by load and stays.

Tests: the rewritten test passes with the machine loaded (run it beside `stress-ng --cpu $(nproc)` or the suite) and fails when the thread clock is replaced by the process clock or a constant.

## Answered while building

- **The test tree** (manager, 2026-10-25): approved as sent. The thread spins until its own clock has counted 50 ms while a burner thread runs beside it, failing loudly after 30 s of wall time, and the reported figure is checked against `CLOCK_THREAD_CPUTIME_ID` within a measured tolerance; the sleeping case keeps its upper bound. The load for the green run is a parallel `go test` of other packages, not `stress-ng`, since installing a package is Aria's to approve; the closing section records the worst gap measured and the tolerance chosen.

## Closed

`58583b8` (r1022) rewrites the spinning case as the approved tree says.
The thread spins until `CLOCK_THREAD_CPUTIME_ID` has counted 50 ms, while a second locked thread burns 50 ms of its own so the process clock runs at least twice the thread's, and `ThreadCPU` must agree with the reference within 5 ms.

- **Gap and tolerance:** the worst gap between `getrusage(RUSAGE_THREAD)` and the reference was 0.39 ms over 500 idle runs and 0.20 ms over 300 loaded runs, so the 5 ms tolerance has better than tenfold margin and is still a tenth of what any mutation adds.
- **Under load:** the 300 loaded runs ran beside two parallel `go test -count=6 -p 28 ./pkg/...` (one with `-race`), at a load average rising from 15 to 42 on 14 cores, and all passed, taking up to 416 ms of wall time for 50 ms of thread time.
  The old test, beside the same load, failed 5 of 50 runs ("19.808ms is not greater than or equal to 25ms").
- **Mutations:** the test fails with `RUSAGE_SELF` (reported 105.5 ms against 50.0 ms), a constant 0 (0 s against 58.6 ms) and the wall clock (109.8 ms against 50.0 ms).

No deviation from the item; the spin target is 50 ms rather than 25, for margin over the tolerance.
