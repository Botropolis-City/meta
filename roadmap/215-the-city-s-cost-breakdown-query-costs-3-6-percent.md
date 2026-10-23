# 215. The city's cost breakdown re-reads the statistics store and costs 3.6% of a core on a real history

**Open, in progress since 2026-10-23 in the session "item 215". Filed 2026-10-23 (r954), from the benchmark session's busy run. Nobody's call — Aria's dashboard ruling sets the budget (an unfocused, visible city ≤ 1% of a core).**

Depends on: nothing
Landed: slice 1 (`8c97161`, r958).

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
2. **An incremental ledger**: a change log the writer keeps, one row per message, and a window and session costs brought up to date from it, against `Store.Window` and `Store.SessionCosts` as the oracle; with the store-on unfocused gate.
