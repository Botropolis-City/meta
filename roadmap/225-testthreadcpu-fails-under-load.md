# 225. TestThreadCPU fails under load

**Open. Filed 2026-10-24 (r967), seen by item 217 while landing. Nobody's call — a defect.**

`botropolis/pkg/daemon/cpu_linux_test.go`'s `TestThreadCPU` spins a thread for 100 ms of wall time and asserts the thread's own CPU clock counted at least 25 ms. At a load average of about 11, item 217's first `make land` failed with "15.92ms is not greater than or equal to 25ms"; the same tree passed on the next run. Under load the scheduler gives the spinning thread less than a quarter of the wall time, so the assertion measures the machine, not the code. [Item 209](209-cost-gates-fail-landings-on-a-busy-machine.md) fixed the same shape in the cost gates by counting work instead of time.

## The fix

Assert on what the code controls: spin until the thread's own clock reads at least 25 ms (with a generous wall-clock timeout that fails loudly), and assert the reported figure is within a small tolerance of an independent reading of the same clock (`CLOCK_THREAD_CPUTIME_ID`, or `/proc/thread-self/stat`), so a load spike lengthens the test instead of failing it. The sleeping case's upper bound is unaffected by load and stays.

Tests: the rewritten test passes with the machine loaded (run it beside `stress-ng --cpu $(nproc)` or the suite) and fails when the thread clock is replaced by the process clock or a constant.
