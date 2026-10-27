# 295. `make land` serves its lock in no order, so a landing can wait behind later ones

**Open, in progress since 2026-10-26 in the session "item 295". Filed 2026-10-26 (r1136), from the manager's and the performance manager's watch on the landing queue. Nobody's call — a defect in the landing process.**

`make land` takes `/tmp/botropolis-land.lock` with `flock` (item 186).
`flock` is not first come, first served: when the lock is released, any waiter may get it.
On 2026-10-26, with up to eight landings queued, the performance manager's `make test-performance` waited 25 minutes behind later arrivals, and item 284's landing, which two other items wait on, was passed over repeatedly, so the manager had to hold every landing by message to let one through.

## The fix

A fair queue: `make land` (and `make test-acceptance-locked` and the performance tier, which take the same lock) take a ticket on arrival and are served in ticket order, a waiter that dies leaving the queue; for instance a numbered ticket file per waiter under `/tmp/botropolis-land.queue/`, the lowest live ticket proceeding, with the existing `flock` kept as the mutual exclusion beneath it.
`make land-queue` prints the queue: who is waiting, since when, from which worktree.
It stays one plain command, never wrapped (the worktree guard, `../CLAUDE.md`).
Tests: three waiters arriving in order are served in order; a waiter killed while queued is skipped; a holder killed while holding releases to the next; the queue listing names each waiter's worktree.
