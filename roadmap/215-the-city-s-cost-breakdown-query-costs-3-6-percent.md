# 215. The city's cost breakdown re-reads the statistics store and costs 3.6% of a core on a real history

**Open. Filed 2026-10-23 (r954), from the benchmark session's busy run. Nobody's call — Aria's dashboard ruling sets the budget (an unfocused, visible city ≤ 1% of a core).**

Depends on: nothing

The busy run on the real history (211 transcripts linked into a scratch home, **statistics store on**, two writers at 200 ms, city unfocused), r946 against r910: the city used **5.75% of a core against 1%** (r910 6.00%). Drawing fell to a third ([item 207](207-an-unfocused-city-redraws-the-whole-world-per-change.md)), but laying out rose to 4.47% in bursts (p50 0.97%, p95 26.5%), and **10.7 s of r946's 13.4 s in `city.build` is `City.Breakdown` → `stats.(*Ledger).Window`: 3.6% of a core on its own** (2.6% on r910), plus 2.4 s in `priceSessions`.
[Item 206](206-the-city-lays-out-whole-on-snapshots-that-shape-nothing.md) recorded that the window is reused for 30 s, so this is the refresh's own cost: a query over the whole store, every 30 s, which on a real history is heavy enough to spike. No earlier busy run saw it, because those daemons ran with `--home` and opened no store.

## The fix

Make the window cheap to keep current: update it from the messages added since the last refresh (the store already knows what's new) instead of re-reading the whole window, or have the daemon compute it once and send it with the snapshot rather than every city querying the store. Price sessions incrementally the same way.

Tests: a benchmark of `Breakdown` on a store the size of the real history (a full refresh and an incremental one); an equality oracle that the incremental window equals the full query after any sequence of ingests; and the busy-unfocused measure with the store on, against 1% (with [item 214](214-the-dashboards-layout-sits-at-its-budget.md)'s layout share beside it).
