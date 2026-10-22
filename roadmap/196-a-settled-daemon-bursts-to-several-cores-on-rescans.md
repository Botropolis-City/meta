# 196. A settled daemon bursts to several cores on rescans, far over its CPU budget

**Fixed 2026-10-22 (`e625afd`, r890). Filed 2026-10-21 (r873), from item 158's live profile. Nobody's call — the budget is set (daemon ≤ 2% of a core, mean, settled); this item meets it.**

Depends on: 157, 158
Landed: slice 1 (`cedcaaf`, r879).
Landed: slice 2 (`4f3ff83`, r880).
Landed: slice 3 (`e625afd`, r890).
Landed: slice 4 (`81f4de8`, r894).

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

## What triggered the bursts

Every watched write (a transcript line, a `sessions/*.json` record) was its own rescan, because the watcher's 100 ms debounce restarts on each event, and every rescan started a stats pass.
On the live home a rescan cost ~75 ms of CPU and the pass ~140 ms (ingest ~60, `Hefts` ~85), so a session writing several lines a second was the 100–300% burst, and nothing written was 0%.
It was all sessions because neither the ingest nor `Hefts` knew what had changed.

## Decided while working

- **Rescans come at most once a second** (the roadmap manager, for Aria, 2026-10-21): the first after a quiet spell still within the 100 ms debounce, and every change within the second coalesced into one, so the last write of a burst is read within a second.
  Hooks still change a building at once; only token counts, the plant and a transcript-only session's first appearance can lag by up to a second.
  This keeps the cost flat however many sessions write: on the acceptance home it was ~1.2% of a core where five rescans a second were ~6%.
- **The store records which sessions moved**, in a `moved` table kept by triggers, so a prune from another process and an older build's writes are caught; it is made on every open and leaves the schema version alone, so an older build opens the file as before (item 149).
- **Directory listings are trusted only a tick after the directory last changed** (2 s), so an entry added in the same modification-time tick as a listing is found; this works on filesystems with no inotify, which invalidating on the watcher's events alone would not.

The test home is the synthetic fixture plus 200 stopped sessions of 300 replies, settled, one session writing every 200 ms: r878 used 8.6–14.5% of a core there, r890 1.2–1.8% with the machine at load 20–26.

## Measured after

On the live home ([the 2026-10-22 report](../performance/reports/2026-10-22-ultra7-265u-igpu-item-196.md)), r890 settled at **0.7% of a core mean and 5.4% at p95**, against ≤ 2% and ≤ 25%, with r873 at 1.6% and 11.9% beside it, and reads fell from 1.0 to 0.1 MiB/s.
That was a quiet night, though: r873 read 7.6% in the busier item 157 run, so 0.7% is not the busy case.
The loaded measure is the acceptance test, where r890 used 1.2–1.8% of a core with the machine at load 20–26, against r878's 8.6–14.5%; it now holds the quieter of two 30 s windows to the 2% limit, since other work only adds to the daemon's CPU time, and logs both.

## Closed

Fixed in four slices in botropolis:
- `cedcaaf` (r879): the store records which sessions moved, and a pass reads only those.
- `4f3ff83` (r880): rescans at most once a second, and transcripts found through a directory index instead of globs.
- `e625afd` (r890): a no-change stats pass went from ~15 ms to ~4 ms, each load allocates a third less, and `TestSettledDaemonUnderAStreamOfChanges` landed.
- `81f4de8` (r894): that test holds the quieter of two windows to the limit.

The test fails on r878 (8.6–14.5% of a core) and passes on r890 (1.2–1.8% under load).
It also asserts that no transcript that did not change is opened, watched with inotify.
The live home settled at 0.7% mean and 5.4% at p95 on a quiet night, in [the 2026-10-22 report](../performance/reports/2026-10-22-ultra7-265u-igpu-item-196.md).

Deviations, all agreed with the roadmap manager:
- The rescan pace of one a second is a change the item did not ask for.
- Listings are invalidated by the directory's modification time, a tick after it last changed, rather than by the watcher's events.
- The CPU test is judged on the quieter of two windows.

Left for later:
- **Making a load incremental per file.** What remains settled is each rescan's `Build`, the catalogue's stat of every stopped transcript, and the collector.
- **Group detection's n² pair cache.** It is [item 198](198-group-detection-s-pair-cache-grows-with-the-square-of-sessions.md).
