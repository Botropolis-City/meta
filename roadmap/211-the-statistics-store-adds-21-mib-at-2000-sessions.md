# 211. The statistics store adds about 21 MiB of the daemon's memory at 2,000 sessions

**Fixed 2026-10-23 (`e8c395b`, r951). Filed 2026-10-23 (r928), from item 205. Nobody's call — the budget is set (daemon ≤ 64 MiB of `Private_Dirty`, settled).**

Depends on: nothing
Landed: slice 1 (`e8c395b`, r951).

With [item 208](208-the-daemon-keeps-its-start-up-peak-until-a-hook-fires.md)'s release in, the daemon settled on the synthetic home plus 2,000 small sessions at **42 MiB with the statistics store off, and 63 MiB with it on** (heap live 22 MB, peak 44), against a budget of 64. [Item 205](205-a-daemon-load-reads-every-stopped-transcript-again.md) made its acceptance gates run the daemon as production does (store and ledger open), which is what showed the difference. So the store costs about 21 MiB at that size, outside the Go heap: most likely SQLite's page cache for each pooled connection, and the write-ahead log.
Item 205 lands that gate as "skip while over 64, fail over 80", naming this item, because a plain gate 1 MiB under its budget would fail landings at random.

## The fix

Find what the store holds (`PRAGMA cache_size` per connection, the pool's size, the WAL's size and checkpointing) and bound it: a smaller cache, fewer idle connections, a WAL checkpoint after the first ingest. Measure what each costs in ingest speed.

Tests: the 2,000-session gate becomes a plain gate at 64 MiB with margin (report it); a test that the store's connections stay within their configured cache.

## Closed

**The store never cost 21 MiB: it cost about 4 MiB, and the rest was the gate reading too early.**
Measured with Private_Dirty split by mapping, three runs each, store off against on:

- SQLite's own memory was about 4 MiB: one pooled connection, with SQLite's default 2,000 KiB cache.
  The WAL's `-shm` map is 32 KiB and the WAL itself costs no memory, and the pool never opened a second connection, so checkpointing and idle connections were left alone.
- The store's code pages add another 2–3 MiB, and the daemon's code as a whole 10–13 MiB.
  They count as dirty only because the acceptance tests build the daemon into `/tmp`, which is tmpfs on this machine; installed on disk they are clean.
  They stay counted (the roadmap manager, 2026-10-23), since overstating is the safe direction. **Nobody needs to chase them.**
- The 63 MiB was the gate.
  It read as soon as the first forced collection appeared in the gctrace, but the daemon's first release can come while loading is still finishing.
  In one run the next release, 1.5 s later, took the same daemon from 62 MiB to 50.

`e8c395b` (r951), in botropolis:

- every connection the store opens gets a 512 KiB cache (`stats.CacheKiB`), which halves SQLite's share to about 2 MiB.
  Ingesting 2,000 sessions took 1.9–4.7 s at every cache size from 2,000 KiB down to 256, which is noise on a loaded machine, so no cost could be measured;
- `TestDaemonWithTwoThousandSessions` waits until no release has come for longer than the settle timer, reads once two reads 500 ms apart agree, and fails, saying so, if either never happens.
  It then gates plainly at 64 MiB, with the skip and the 80 MiB ceiling gone.

The tests that show it:
- `TestOpen`: three connections opened at once each report a cache of `CacheKiB`. It is red at SQLite's default.
- The gate settled at **47–51 MiB, 12–16 under the budget**, before item 210, and at **53–57 MiB, 6–10 under**, on top of item 210's kept candidate index (`aad7833`, r950; live heap 24–25 MB, up from 22).
  Without the wait for the last release, it read 62 once, as before.

The same test's CPU leg is item 209's and was not touched.
