# 211. The statistics store adds about 21 MiB of the daemon's memory at 2,000 sessions

**Open. Filed 2026-10-23 (r928), from item 205. Nobody's call — the budget is set (daemon ≤ 64 MiB of `Private_Dirty`, settled).**

Depends on: nothing

With [item 208](208-the-daemon-keeps-its-start-up-peak-until-a-hook-fires.md)'s release in, the daemon settled on the synthetic home plus 2,000 small sessions at **42 MiB with the statistics store off, and 63 MiB with it on** (heap live 22 MB, peak 44), against a budget of 64. [Item 205](205-a-daemon-load-reads-every-stopped-transcript-again.md) made its acceptance gates run the daemon as production does (store and ledger open), which is what showed the difference. So the store costs about 21 MiB at that size, outside the Go heap: most likely SQLite's page cache for each pooled connection, and the write-ahead log.
Item 205 lands that gate as "skip while over 64, fail over 80", naming this item, because a plain gate 1 MiB under its budget would fail landings at random.

## The fix

Find what the store holds (`PRAGMA cache_size` per connection, the pool's size, the WAL's size and checkpointing) and bound it: a smaller cache, fewer idle connections, a WAL checkpoint after the first ingest. Measure what each costs in ingest speed.

Tests: the 2,000-session gate becomes a plain gate at 64 MiB with margin (report it); a test that the store's connections stay within their configured cache.
