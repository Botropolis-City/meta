# 159. First launch takes up to four cores, starts over after a quit, and shows no progress

**Open, in progress since 2026-10-21 in the session "item 159". Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the first-launch budget Aria set the same day. Nobody's call — the budget is set; this item meets it.**

Depends on: 157
Landed: slice 1 (`e0b4d05`, r876).
Landed: slice 2 (`e1eed8e`, r877).
Landed: slice 3 (`e8c170a`, r881).
Landed: slice 4 (`a6bbb78`, r898).

Aria, 2026-10-19: first launch must never overwhelm the machine, even to build a cache.
Throttle it, run it in the background, make it resumable, show a map within 5 s, and show a loading bar with real progress for any wait before the first frame.
Someone whose laptop stalls the first time will not open the app again.

**What 0.2.2 does on a first launch**, with an empty state directory (`perf-daemon-ab --cold`):

| rig | history | seconds busy | peak CPU | CPU-seconds | read | report |
| --- | --- | --- | --- | --- | --- | --- |
| Core Ultra 7 255H | 1.2 GiB | ~8 | 391% | 26.5 | 954 MiB | [laptop](../performance/reports/2026-10-19-laptop-igpu-0.2.2.md) |
| Core Ultra 7 265U | 2.4 GiB | 15 | 358% | 32.0 | 3,645 MiB | [265U](../performance/reports/2026-10-19-ultra7-265u-igpu-0.2.2.md) |

0.2.3, on the 265U on 2026-10-21, as a real first launch after the store was removed (item 190): 30 s at half a core or more, a peak of 414%, 103 CPU-seconds, 4,526 MiB read, `Private_Dirty` at most 25 MiB.

On a four-core machine with a slower disk that is the whole machine for much longer, and it grows with the history.

**Where the cores come from.** The ingest itself is one goroutine on a locked thread (`storedHefts.pass`, `pkg/state/storedheft.go`, and `wholeRead.pass`, `pkg/state/wholeread.go`).
The other cores are the garbage collector working against the 16 MiB heap cap: with `GOMEMLIMIT=256MiB` the same cold start peaks at 115% and spends 10.8 CPU-seconds.
So item 157 comes first, and this item is what is left after it.

**Background priority is only half there.** `backgroundPriority` (`pkg/state/priority_linux.go`) sets the thread's I/O class to idle and nothing else, and on macOS it is a no-op (`priority_other.go`).
Item 138 removed nice 19 on purpose: with a collection a hundred times a second, every stop-the-world waited for the nice-19 thread, and the whole daemon stalled.
Once item 157 has cut the collections, CPU priority can come back without that inversion, and should be measured for it.

**It is not resumable in practice.** On the 265U, a cold 0.2.2 daemon stopped at 6 s had read 1,547 MiB; relaunched on the same state, it read 3,236 MiB more, about 89% of the 3,645 MiB an uninterrupted run reads.
The statistics store resumes per file (`Store.Ingest` keeps `read_to`), but the whole-read heft cache is in memory only (`wholeRead.hefts`), so a restart reads every stopped transcript whole again.
0.2.2 also re-read live transcripts whole on every change, which is part of why it reads 1.4× the history; item 141 fixed that at r747, after 0.2.2, so measure at HEAD before attributing the rest.

**No progress is shown.** Nothing reports how far the ingest has got, so the city cannot show a percentage, and the window shows the map's background colour (`colorVoid`) while item 70's page-by-page upload runs, which is a blank window by the budget's definition.

**The budgets** ([budgets.md](../performance/budgets.md), *First launch*): ≤ 1 core in all at background priority whatever `GOMAXPROCS` is; ≤ 256 MiB `Private_Dirty` at any point; a map within 5 s of opening the city with what is known so far and a percentage for the rest; a loading bar with real progress for any wait before the first frame; quitting part-way loses nothing.

## The fix, in slices

1. **Throttle**: the ingest and the whole read take at most one core between them, by pacing reads (bytes per second, or a duty cycle per `YieldEvery`), at background CPU and I/O priority on Linux and macOS.
2. **Resume**: persist the whole-read hefts (the statistics store already has the shape), so a relaunch reads only what it had not.
3. **Progress**: the daemon reports bytes done and bytes known over the protocol, and the city shows a percentage while the first scan runs, with the map drawn from what is known so far within 5 s.
4. **Loading bar**: any wait before the first frame, including the atlas upload, draws a bar with real progress instead of `colorVoid`.

Tests: a measure test of a cold start over a synthetic history of a few GB whose limits are the budget's (peak CPU ≤ 100% of a core, `Private_Dirty` ≤ 256 MiB); a test that a daemon stopped part-way and restarted reads no byte twice; a test that the city's first frame arrives within 5 s with a percentage on it.
Judge it with `perf-daemon-ab --cold` and the quit-and-relaunch comparison above, and write the numbers into a new report.

## Baseline after item 157

From [the 2026-10-21 report](../performance/reports/2026-10-21-ultra7-265u-igpu-item-157.md), on the Core Ultra 7 265U with 3.2 GiB of history and item sessions working, r873 against r871 (before item 157):

- **cold start, until idle**: 73 CPU-seconds and a peak of 114% of a core in 1-second samples (r871: 265 and 394%), against ≤ 1 core in all; 509 collections (r871: 23,956);
- the whole 3.2 GiB history read in about 250 s, 4.2 GiB read in all;
- `Private_Dirty` peaked at 33 MiB, against ≤ 256 MiB.

## What landed

- **Slice 1, throttle:** both background passes work at most half the wall clock (`pkg/state/pace.go`): at each yield the pass sleeps as long as it worked since the last one, and time waiting at the load gate is not counted as work.
  The other half of a core is left for the collector and the loads, so the process stays under one core whatever `GOMAXPROCS` is.
  The whole read, which had no yield inside a pass, now paces after each file.
  On Linux the pass's thread also goes to nice 10, or stays where it is if the process is already lower.
  Item 138's inversion test (`pkg/daemon/backfill_linux_test.go`: one core, four busy loops, a bound of 600 ms), with its slow ingest now yielding every MiB as the real one does, measured no nice at 101–126 ms, nice 10 at 101–135 ms and nice 19 at 105–271 ms.
  `testing/acceptance/firstlaunch_test.go` starts the daemon on an empty state directory over 256 MiB of synthetic history and holds every 1 s sample to one core and 256 MiB of `Private_Dirty`: 59% and 29 MiB paced, 103% with the pacer off.
  `BOTROPOLIS_FIRST_LAUNCH_GB=3` runs it at this item's size for a report.
- **Slice 2, resume:** with statistics on, the ingest already resumed per transcript, so what a quit lost was the transcript it was reading, from the start, however long.
  It now commits every 16 MiB inside a transcript (`stats.CheckpointEvery`), rows and `read_to` together, and the next ingest reads on from there.
  A reply written on both sides of a checkpoint is upserted, so it is held once, as it was last written.
  `Store.IngestContext` stops at the next yield once its context is done, and `Ingest` wraps it, so `StatsSource` did not change (item 196 is changing it).
  `TestFirstLaunchResumes` kills a daemon 40 MiB into 96 MiB of 48 MiB transcripts and starts it again: 113 MiB read in all, 141 MiB with the checkpoints off, against 103 MiB for one uninterrupted launch.
- **Slice 3, progress:** the statistics store counts, during an ingest, the bytes it has to read and the bytes read so far, and the whole read counts its stopped transcripts the same way.
  The loader puts them on the snapshot as `Scan` while a pass with at least 32 MiB to read is running, so the small pass that every rescan starts shows nothing.
  While one runs, the daemon re-sends its last snapshot once a second with `Scan` moved on, without loading again (`pkg/daemon/progress.go`).
  The footer draws "Reading your history · 42% · about 6 min left · statistics fill in as it reads" over a thin bar filled to the fraction read, on top of the needs-you line, and estimates the time left only once it has watched the rate for 20 s.
  **Aria approved the frame on 2026-10-21** (`botropolis/docs/screenshots/r877-item-159-first-launch-reading.png`, mid-scan): the wording, the footer placement and the bar, and the same line with statistics off.
  `TestFirstLaunchCity` opens the debug city on a daemon mid-scan and holds the percentage on every frame until the read is done, moving and never going backwards (red with the daemon's re-send off).
  Item 197's slice 2 adds the case of a snapshot that carries only progress, which lays nothing out again.
- **Slice 4, the wait before the first frame:** two waits came before the city was drawn: the atlas pages going up, which drew the void, and the daemon's first load, which every request but a hook event waits for (item 143) and which drew an empty island.
  Each now draws a centred panel on the void, over the same thin bar as the footer's.
  "Opening the city" fills by the pages of the zoom's level that are up (`kits.progress`; 2 pages at the usual zoom and 6 from 1.98, since item 162 puts up only the level in use).
  "Reading your sessions · 40 of 120" fills by the sessions the daemon's load has read of those it found: the loader counts as it loads, and the daemon answers a new `loading` request with that count while it holds everything else.
  Where nothing counts (a daemon from before the request, or a city reading the home itself), the line is "Reading your sessions" and the bar sweeps instead of filling.
  No panel shows for a wait under 300 ms, and a daemon of another release still gets item 152's dialog instead.
  **Aria approved the frame on 2026-10-22** (`botropolis/docs/screenshots/r881-item-159-opening-reading-sessions.png`), the sweep included.
  `TestFirstLaunchCityWaiting` opens the debug city on a stand-in daemon that says 40 of 120 and never sends a snapshot: every frame carried the line and none drew the city, against none and 106 before.

## Deviations

- **macOS has the pacer but no background CPU priority yet** (manager, 2026-10-21).
  The only call that needs no cgo, `setpriority(PRIO_DARWIN_THREAD, 0, PRIO_DARWIN_BG)`, throttles a thread at least as hard as nice 19, which is the inversion item 138 hit.
  Measuring it is [item 200](200-first-launch-runs-at-full-priority-on-macos.md), filed on Aria's note so it outlives this item, with research into what macOS offers in its place.
  Until then the pacer alone keeps the pass to half a core on macOS.
- **With statistics off, a relaunch reads stopped transcripts whole again** (manager, 2026-10-21, from what is already ruled), instead of persisting the whole read's hefts.
  Someone who turned statistics off chose to have Botropolis keep no store of their history, and a heft cache would be that store under another name.
  The re-read is paced and at background priority.
  "Quitting part-way loses nothing" holds with statistics on, which is the default.
- **"A map within 5 s" is measured for a report, not gated in wall-clock seconds** (manager, 2026-10-21).
  On this machine at a load of 40, a city on an empty home, with no daemon and no scan, took 12–15 s to draw, so a stopwatch in `make test` would fail other sessions' landings at random.
  The wall-clock limits run only with `BOTROPOLIS_FIRST_LAUNCH_TIMED=1`.
  What gates is work: the CPU-seconds the city spends before it draws the city, read from `/proc`, which load barely moves (0.14–0.29 measured).
  Slice 3 set that limit at 5 CPU-seconds, derived from 5 s on the budget's machine; **Aria's note (2026-10-21) was that a guard with 15× headroom can't fail**, so slice 4 lowers it to 1 CPU-second, about 3.5× the measured worst.
- **A possible follow-up:** a pacer that raises its share while the machine is otherwise idle would make the first read fast and still never take the machine.
  Worth filing if the wait feels long once progress shows.
