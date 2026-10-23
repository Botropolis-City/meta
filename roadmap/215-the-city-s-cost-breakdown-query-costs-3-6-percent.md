# 215. The city's cost breakdown re-reads the statistics store and costs 3.6% of a core on a real history

**Fixed 2026-10-23 (`26b2faa`, r963). Filed 2026-10-23 (r954), from the benchmark session's busy run. Nobody's call — Aria's dashboard ruling sets the budget (an unfocused, visible city ≤ 1% of a core).**

Depends on: nothing
Landed: slice 1 (`8c97161`, r958).
Landed: slice 2 (`26b2faa`, r963).

The busy run on the real history (211 transcripts linked into a scratch home, **statistics store on**, two writers at 200 ms, city unfocused), r946 against r910: the city used **5.75% of a core against 1%** (r910 6.00%). Drawing fell to a third ([item 207](207-an-unfocused-city-redraws-the-whole-world-per-change.md)), but laying out rose to 4.47% in bursts (p50 0.97%, p95 26.5%), and **10.7 s of r946's 13.4 s in `city.build` is `City.Breakdown` → `stats.(*Ledger).Window`: 3.6% of a core on its own** (2.6% on r910), plus 2.4 s in `priceSessions`.
[Item 206](206-the-city-lays-out-whole-on-snapshots-that-shape-nothing.md) recorded that the window is reused for 30 s, so this is the refresh's own cost: a query over the whole store, every 30 s, which on a real history is heavy enough to spike. No earlier busy run saw it, because those daemons ran with `--home` and opened no store.

## The fix

Make the window cheap to keep current: update it from the messages added since the last refresh (the store already knows what's new) instead of re-reading the whole window, or have the daemon compute it once and send it with the snapshot rather than every city querying the store. Price sessions incrementally the same way.

Tests: a benchmark of `Breakdown` on a store the size of the real history (a full refresh and an incremental one); an equality oracle that the incremental window equals the full query after any sequence of ingests; and the busy-unfocused measure with the store on, against 1% (with [item 214](214-the-dashboards-layout-sits-at-its-budget.md)'s layout share beside it).

## Slices

Planned with the roadmap manager on 2026-10-23, which approved the test trees and ruled on the questions below.

**The window was reused for 2 s, not 30.**
`LedgerCache` was 2 s; the 30 s was `LedgerSessions`, every session's cost. So while snapshots streamed, the build read the 24 h window again every 2 s.
On the real store (31,587 messages, 4,230 in the last day), a refresh costs about 700 ms: `Store.Window` about 270 ms in five queries of 37–67 ms, each on its index, and `Store.SessionCosts` over all history about 450 ms.

1. **The ledger reads the store again only when it was written, at most every 30 s** (r958; the manager, 2026-10-23).
   "Written" is SQLite's `data_version`, on a connection the reader keeps for it.
   A window still ages while nothing is written, as messages leave it, so an unchanged store is read again every 5 minutes (`LedgerAging`); session costs do not age and are read again only on a write.
   The changelog says the 24 h cost can lag by up to 30 s, or 5 minutes for messages leaving the window.
   On the busy city with a statistics store the real history's size (30,000 replies over 7 days, about 4,300 in the last day), unfocused, one session writing every 200 ms: **16.0% of a core** with the 2 s cache (15 s), **3.0%** with this (65 s).
   A 15 s stream read 0.70%, because it can fall between two 30 s refreshes and see none, so the store-on gate streams for 65 s.
   That is over item 209's 2% ceiling, so the gate lands with slice 2 (the manager: option A, ship the 5× cut now).
2. **The ledger brings its window and session costs up to date from the store's change log** (Aria, 2026-10-23: in 0.3.0).
   The writer logs every message and every session a write changes in `changed_messages` and `changed_sessions`, one row each under a seq from one counter in `meta`, made on every open like item 196's `moved`.
   One row each is the bound the manager asked for: an older build fires the triggers and never reads the log, and it still holds at most one row per message (tested).
   The ledger keeps a window's messages in memory and reads again only those the log names, and prices again only the sessions it names; a store with no log is read whole.
   `Store.Window` and `Store.SessionCosts` stay as the oracle: 50 seeds of 40 random ingests (new messages, growth, forks, a shorter rewrite, a forget, the clock moving) over 1 h, 24 h and 7 d windows, equal after every step, counters exactly and costs to a relative 1e-9.
   Mutated red three ways: never dropping a changed message (37 failures), updates not bumping their sessions (all 50 seeds), and always reading whole (both counting tests).
   `BenchmarkBreakdown` on 31,600 messages: 72.5 ms, 3.2 MB read whole; 12.5 ms, 194 KB brought up to date, 8 ms of it adding the day's 4,500 messages up in Go, left simple at one refresh per 30 s.
   **The store-on unfocused gate: 0.65% of a core** over 65 s (laying out 397 ms, against 1,948 after slice 1), so it is a plain 1% gate; it asserts the city holds `stats.db` open.
   The triggers cost the daemon a little, measured back to back: a stream 0.24% → 0.30%, settled 0.96/1.08% → 1.14/1.31%, inside its 2%.

## Closed

Fixed in two slices, r958 and r963, both in 0.3.0 (Aria, 2026-10-23).

**With a statistics store the real history's size open, the unfocused dashboard spent 16% of a core and now spends 0.65%**, against its 1%.
Measured by the unfocused gate's new variant: the busy city with 30,000 replies over 7 days behind it, the daemon and the city on one scratch home, one session writing every 200 ms, streamed 65 s so a 30 s refresh always falls inside it:

| | share of a core | laying out |
| --- | --- | --- |
| the 2 s cache (r954) | 16.0% | 2,407 ms in 15 s |
| slice 1, reading again only when written, at most every 30 s | 3.0% | 1,948 ms in 65 s |
| slice 2, bringing it up to date from the change log | 0.65% | 397 ms in 65 s |

**No earlier gate saw it, because no earlier gate opened a store**: every busy city ran with `--home`, and a city that cannot read the store counts its breakdown from memory, which costs nothing like reading it.
So the variant asserts the city holds `stats.db` open before its number counts, the same shape as item 206's roads: a fixture missing what the real data has passes every check that iterates over it.

`BenchmarkBreakdown` (`pkg/city`) on 31,600 messages: 72.5 ms read whole, 12.5 ms brought up to date.
`TestLedgerIncremental` (`pkg/stats`) is the equality oracle; `TestChangeLog` holds the log to one row per message whatever writes it.

**Deviations, for Aria:**
- The item said the window was reused for 30 s; it was 2 s (`LedgerCache`), and 30 s was every session's cost. Slice 1 made 30 s the window's cadence too, and 5 minutes while nothing is written, since messages still age out of the 24 h: the strip's 24 h cost can lag by up to 30 s, or 5 minutes for messages leaving the window, and the changelog says so.
- The fix chose the change log the writer keeps over having the daemon send the window with each snapshot (the manager, 2026-10-23): the city stays a read-only reader and the snapshot protocol is unchanged. It costs the daemon about 0.2% of a core settled, inside its 2%.
- Slice 1's landing pushed a meta commit while `make publishable` was failing, because its output was piped; the failure was another branch on the meta remote (`process-groups`), not this item, and the commit was text only.
