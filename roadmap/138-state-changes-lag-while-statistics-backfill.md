# 138. A session's change of state shows seconds late while the statistics backfill runs

**Fixed 2026-10-19 (`d7dcef6`, r731). Filed 2026-10-19 (r707), from the validation checklist's step 10 run against main before 0.2.0. Nobody's call — a defect, until it is measured as acceptable.**

Depends on: nothing
Landed: slice 1 (`3aa847b`, r725).
Landed: slice 2 (`d7dcef6`, r731).

Step 10 of the [validation checklist](validation-checklist.md): run a `!` command in a session and the map reads it as working.
Against a daemon built from main (r704) started on an empty state directory, so that it backfilled the statistics store from every transcript on Aria's machine, as the first start of 0.2.0 will (item 116's schema step re-reads every transcript):

- for the first ~30 minutes, a `!` command's `busy` reached `botropolis status` **6–15 s** after the session file said it, and in one run not within 15 s; 0.1.7's daemon, beside it, showed it at once;
- after the backfill settled, main's daemon showed it in 0.15–1.1 s, so step 10 passes.

So the first start after upgrading makes the city slow to say what sessions are doing, for as long as the backfill runs, which is exactly when someone has just installed it and is looking.

## The fix

Measure first: how long the backfill takes on a large home, and whether a rescan triggered by a session file waits behind ingest. Then keep the live state path ahead of the backfill — ingest in its own goroutine at lower priority, in batches that yield to rescans — so a session's state is never late because statistics are being caught up.

Tests: with a slow fake ingest in progress, a change to a session file should reach the model within the debounce plus a small bound; a measure test whose limit is that bound, not today's figure.

## Measured

The real loader over Aria's `~/.claude` (2.1 GB) with a fresh store, timing each load while the backfill ran.

- On an idle machine the backfill took 27 s and loads 30–580 ms: no lag to speak of.
  The machine has to be busy, as hers was at a load of 30 on 14 cores.
- Pinned to two cores with four busy loops, at nice 19 as shipped: loads took 1–12 s while using 60 ms of CPU each, stop-the-world pauses reached 335 ms, 9 s of the whole process was frozen in 35 s, and the backfill had not finished at 4 minutes.
- The same without nice 19: pauses at most 50 ms, and the backfill finished in 2m19s.

Three causes, in order of size:

1. **Priority inversion.** The pass ran on a thread at nice 19, and Go stops every thread for each garbage collection — about a hundred a second, because ingest allocated a fresh buffer per line against a 1 MB heap.
   On a busy machine the kernel rarely runs a nice-19 thread, and the whole daemon waited for it every time.
   Nice was the cause, not the remedy.
2. **Ingest shared the CPU with the load**, file after file, with nothing that gave way.
3. **A live transcript is re-read whole on every change** — one load spent 3.7 s of CPU re-reading a 339 MB one.
   That is present with statistics off too, so it is [item 141](141-a-live-transcript-is-re-read-whole-on-every-change.md) rather than a slice here.

## What landed

- **Slice 1:** both background passes keep the process's CPU priority and go into Linux's idle I/O class instead, which cannot hold anyone up, because a thread blocked in a read is already stopped as far as the collector is concerned.
  `pkg/daemon/backfill_linux_test.go` is the measure test: it re-runs itself pinned to one core beside four busy loops, with a fake ingest churning garbage on the pass's thread, and holds a session file's change to the debounce plus 500 ms.
  It measured 170–210 ms after the fix and 0.9–1.8 s at nice 19.
- **Slice 2:** `Store.Ingest(projectsDir, now, yield)` yields before each transcript and after every megabyte inside one, and the loader holds a gate for each load that the yield waits at, so a load never shares the CPU with the backfill.
  Lines are read through a reused buffer.
  On the two busy cores again: loads that read no transcript whole took 110–260 ms and pauses at most 41 ms.
  The loads still slow were all item 141's whole re-reads, 8–15 s each, and because loads now come first, back-to-back slow loads hold the backfill back until item 141 lands.
- **Changelog:** under *Fixed*, `d7d565b`.

**One deviation, for Aria:** the whole read that runs when statistics are off (item 109) got slice 1's priority fix but not slice 2's yield.
It reads stopped transcripts once, after the first load, rather than backfilling a store, and no test could hold a load and that pass in a known order without changing it more than this item asked.
