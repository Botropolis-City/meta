# 203. The daemon's first load runs unpaced and holds back the map for about 9 s

**Open. Filed 2026-10-22 (r898), from item 159's report on Aria's real history. Nobody's call — two budgets are set (first launch ≤ 1 core; a map within 5 s), and this item meets both.**

Depends on: 159

[Item 159](159-first-launch-takes-the-machine.md) paced the first launch's background passes to half a core, and measured it on Aria's 3.3 GiB `~/.claude` (`perf-daemon-ab --cold`, r898 against r873, under the landing lock): from 10 s on, the paced ingest holds 48–55% every second, as designed.
**But the first 9 s run at 100–112% (8 one-second samples over the 1-core budget), and the map can't draw until they end, so on this history it appears at about 9 s against a 5 s budget.** Those 9 s are the daemon's first `Load`, not the ingest: it reads a window of every stored transcript, and every live transcript whole, at about 100 MiB/s, before the paced pass begins. The synthetic home has few transcripts, so its first load is instant, and the suite never saw it.

## The fix

Make the first load smaller, not slower (pacing it would trade the map budget for the core budget):
- before the first snapshot, read only what drawing the map needs — each transcript's window, no whole live reads, which can follow once the map is up;
- on a warm start, serve the stored sessions' catalogue from the statistics store rather than re-reading their transcripts.

Tests: a synthetic home shaped like the real one (several hundred transcripts, a few GB, some live ones large) in the first-launch acceptance test, so the suite sees what the real history does; on it, the first snapshot within the 5 s budget measured as work (CPU-seconds, as item 159's gate does), and no 1 s sample over one core. Re-measure on the real history with `perf-daemon-ab --cold` and add it to `performance/reports/`.
