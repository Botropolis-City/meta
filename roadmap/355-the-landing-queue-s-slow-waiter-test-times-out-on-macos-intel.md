# 355. The landing queue's slow-waiter test times out on the Intel macOS runner

**Open. Filed 2026-11-06 (r1268), from CI on main. Nobody's call — a flaky test.**

`tools/land-queue`'s `TestRun` case *"when the waiter next in line is slow to wake, and a later one arrives as the lock frees"* failed on the `macos-26-intel` job of two pushes in a row on 2026-11-06, runs 42194912566 and 42196168441, after 30 s each, with `main_test.go:261: the later waiter neither queued nor ran`.
It passed on Linux and on Apple-silicon macOS in the same runs, and on every run before them.

## Where it stands

The case stops the first waiter's process group with `SIGSTOP`, releases the holder, starts a later waiter, and waits with `eventually` for the later one either to write its ticket or to run.
On the Intel runner it did neither within the wait.
That is either the runner being slow enough to outlast `eventually`'s bound,
or a new arrival that blocks before writing its ticket while the stopped waiter holds something it needs, such as the queue file's own lock.
The second would be a defect in the queue, not the test, and is the one to rule out first.

## The fix

Reproduce it under load on macOS, or with the stopped waiter held longer on Linux, name which of the two it is, and fix that:
a bound taken from what the case needs rather than the runner's speed, or a queue that never blocks a new arrival on a stopped waiter.
Item 295 built the queue and item 332 put its tests under a make target.

## Seen since

- 2026-11-06, on main: `pkg/daemon`'s `TestRequestRescan` (*"when the watcher has just rescanned and a background pass asks for another"*) on `macos-26-intel`, run 42265186145; `pkg/measure`'s `TestThread` (*"it should count at least 80% of the CPU the process spent"*) on `macos-26-intel`, run 42284185651; and `TestWatch` (*"when a subagent transcript appears under a live session"*) on `macos-26`, the same run.
  Each passed on a rerun and on Linux, so the Intel runner's timing is the common thread, and this item may be the place to fix them together.
- 2026-11-08, on main at `c8cb3e82`: this item's own slow-waiter case again on `macos-26-intel`, run 42431337078, after 30.16 s.
