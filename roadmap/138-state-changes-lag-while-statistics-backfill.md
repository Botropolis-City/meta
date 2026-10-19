# 138. A session's change of state shows seconds late while the statistics backfill runs

**Open, in progress since 2026-10-19 in the session "item 138". Filed 2026-10-19 (r707), from the validation checklist's step 10 run against main before 0.2.0. Nobody's call — a defect, until it is measured as acceptable.**

Depends on: nothing
Landed: slice 1 (`3aa847b`, r725).

Step 10 of the [validation checklist](validation-checklist.md): run a `!` command in a session and the map reads it as working.
Against a daemon built from main (r704) started on an empty state directory, so that it backfilled the statistics store from every transcript on Aria's machine, as the first start of 0.2.0 will (item 116's schema step re-reads every transcript):

- for the first ~30 minutes, a `!` command's `busy` reached `botropolis status` **6–15 s** after the session file said it, and in one run not within 15 s; 0.1.7's daemon, beside it, showed it at once;
- after the backfill settled, main's daemon showed it in 0.15–1.1 s, so step 10 passes.

So the first start after upgrading makes the city slow to say what sessions are doing, for as long as the backfill runs, which is exactly when someone has just installed it and is looking.

## The fix

Measure first: how long the backfill takes on a large home, and whether a rescan triggered by a session file waits behind ingest. Then keep the live state path ahead of the backfill — ingest in its own goroutine at lower priority, in batches that yield to rescans — so a session's state is never late because statistics are being caught up.

Tests: with a slow fake ingest in progress, a change to a session file should reach the model within the debounce plus a small bound; a measure test whose limit is that bound, not today's figure.
