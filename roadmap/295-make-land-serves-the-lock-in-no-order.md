# 295. `make land` serves its lock in no order, so a landing can wait behind later ones

**Fixed 2026-10-26 (`4658259`, r1144). Filed 2026-10-26 (r1136), from the manager's and the performance manager's watch on the landing queue. Nobody's call — a defect in the landing process.**

`make land` takes `/tmp/botropolis-land.lock` with `flock` (item 186).
`flock` is not first come, first served: when the lock is released, any waiter may get it.
On 2026-10-26, with up to eight landings queued, the performance manager's `make test-performance` waited 25 minutes behind later arrivals, and item 284's landing, which two other items wait on, was passed over repeatedly, so the manager had to hold every landing by message to let one through.

## The fix

A fair queue: `make land` (and `make test-acceptance-locked` and the performance tier, which take the same lock) take a ticket on arrival and are served in ticket order, a waiter that dies leaving the queue; for instance a numbered ticket file per waiter under `/tmp/botropolis-land.queue/`, the lowest live ticket proceeding, with the existing `flock` kept as the mutual exclusion beneath it.
`make land-queue` prints the queue: who is waiting, since when, from which worktree.
It stays one plain command, never wrapped (the worktree guard, `../CLAUDE.md`).
Tests: three waiters arriving in order are served in order; a waiter killed while queued is skipped; a holder killed while holding releases to the next; the queue listing names each waiter's worktree.

## Closed

**Fixed** (`4658259`, r1144).
`tools/land-queue` gives each arrival a numbered ticket in `/tmp/botropolis-land.queue/` and holds a flock on it for as long as it lives, so a ticket whose lock can be taken belongs to a waiter that died, and the next waiter to look clears it.
The lowest live ticket takes `/tmp/botropolis-land.lock` itself, kept as the mutual exclusion beneath the queue, so a make still on the old recipe is excluded, if not ordered.
`make land`, `make test-acceptance-locked`, `make test-performance` and `make demo-media-locked` all queue through it, each still one plain command with nothing piped.
`make land-queue` lists who holds and who waits: since when, the target, the worktree and its head (the manager's addition), and it takes no lock beyond non-blocking probes.
The queue's path follows `LAND_LOCK`, so a test that moves the lock cannot touch the real queue.

Tests: `tools/land-queue/main_test.go` runs the built tool as real processes against a temp-dir lock: three waiters served in order, a killed waiter skipped and its ticket cleared, a killed holder releasing to the next, a lock held outside the queue waited for, the command's exit code kept, and the listing's worktree, target, head and holder.
`testing/acceptance/land_test.go` lands three sessions behind a holder in arrival order through `make land`, lists them with `make land-queue`, and checks that all four recipes queue and take no bare flock.

**Deviation, for the record:** the three-in-order test passed with ordering switched off, three runs of three, because Linux wakes waiters that arrived spaced apart roughly in order on a quiet machine.
So the order is proven by a second test that freezes the waiter next in line (SIGSTOP) as the lock frees and lets a later one arrive.
With ordering off, the later one went first, as on 2026-10-26; with the queue, it waits.
flock(1) is no longer needed, so the "make land needs flock" check and its test went, as the manager agreed.
