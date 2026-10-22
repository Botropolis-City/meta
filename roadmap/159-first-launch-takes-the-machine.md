# 159. First launch takes up to four cores, starts over after a quit, and shows no progress

**Open, in progress since 2026-10-21 in the session "item 159". Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the first-launch budget Aria set the same day. Nobody's call — the budget is set; this item meets it.**

Depends on: 157
Landed: slice 1 (`e0b4d05`, r876).

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

## Deviations

- **macOS has the pacer but no background CPU priority yet** (manager, 2026-10-21).
  The only call that needs no cgo, `setpriority(PRIO_DARWIN_THREAD, 0, PRIO_DARWIN_BG)`, throttles a thread at least as hard as nice 19, which is the inversion item 138 hit.
  So item 138's inversion test is to be ported to darwin and run on CI's macOS runners with it applied; it ships only if it holds the bound there.
  Until then the pacer alone keeps the pass to half a core on macOS.
- **With statistics off, a relaunch reads stopped transcripts whole again** (manager, 2026-10-21, from what is already ruled), instead of persisting the whole read's hefts.
  Someone who turned statistics off chose to have Botropolis keep no store of their history, and a heft cache would be that store under another name.
  The re-read is paced and at background priority.
  "Quitting part-way loses nothing" holds with statistics on, which is the default.
- **A possible follow-up:** a pacer that raises its share while the machine is otherwise idle would make the first read fast and still never take the machine.
  Worth filing if the wait feels long once progress shows.
