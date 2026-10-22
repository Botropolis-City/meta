# 196. A settled daemon bursts to several cores on rescans, far over its CPU budget

**Open, in progress since 2026-10-21 in the session "item 196". Filed 2026-10-21 (r873), from item 158's live profile. Nobody's call — the budget is set (daemon ≤ 2% of a core, mean, settled); this item meets it.**

Depends on: 157, 158

After [item 157](157-the-daemon-s-heap-cap-keeps-it-collecting.md) (the collector) and [item 158](158-group-detection-reruns-pairwise-on-every-prompt.md) (grouping), the daemon's settled mean is still far over budget.
In a 600 s A/B under `perf-daemon-ab` with item sessions working on the machine, both builds **burst together to 100–300% CPU for 30–60 s at the same moments, reading up to 70 MB/s, and sit at 0% between**: means of 23% and 20% of a core against a budget of 2%.
A 300 s live profile (item 158's build, before 157 landed, so the collector is still about half of it) puts `storedHefts.pass` at 18% of the daemon's CPU, driven from `Daemon.Rescan` / `Watch`:

- `claude.FindTranscript` through `filepath.Glob`: ~9.6%;
- `stats.(*Store).Hefts` SQLite row reads: ~8.6%.

So a rescan in a settled daemon looks for every transcript by globbing and reads every heft row again, and something triggers it for the whole history at once. This is not [item 159](159-first-launch-takes-the-machine.md), which is the first launch with an empty store; this is the daemon that has already ingested everything.

## The fix

Find what triggers the bursts first (which event, how often, and why it is all sessions rather than the one that changed), then make a settled rescan cost what changed: transcripts located once and kept (invalidated by the watcher), heft rows read for the sessions that moved, not all of them. The ingest's read of 70 MB/s at a moment nothing new was written says the store is re-reading what it already has.

Tests: an acceptance measure like item 157's — a daemon on a copy of the synthetic fixture with one session writing, measured by **process CPU time** (not load), ≤ 2% of a core mean over the run, plus "it should read no transcript that did not change". Re-measure with `perf-daemon-ab` (settled) and record it in `performance/reports/`.

## Baseline after item 157

From [the 2026-10-21 report](../performance/reports/2026-10-21-ultra7-265u-igpu-item-157.md), on the Core Ultra 7 265U with 3.2 GiB of history and item sessions working, r873 against r871 (before item 157):

- **settled, 600 s**: CPU 7.6% of a core mean and 65% at p95 (r871: 23.8% and 140%), against ≤ 2% and ≤ 25%; 38 collections a minute (r871: 1,104); `Private_Dirty` 26 MiB mean;
- without the first minute, 4.7% mean, with minutes 3–5, when sessions were busiest, at 10–16%;
- the collector's share of the CPU is 0% in gctrace, so what remains is the rescans' own work.
