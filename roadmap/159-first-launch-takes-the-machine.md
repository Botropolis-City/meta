# 159. First launch takes up to four cores, starts over after a quit, and shows no progress

**Open. Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the first-launch budget Aria set the same day. Nobody's call — the budget is set; this item meets it.**

Depends on: 157

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
