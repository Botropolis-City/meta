# 203. The daemon's first load runs unpaced and holds back the map for about 9 s

**Open, in progress since 2026-10-22 in the session "item 203". Filed 2026-10-22 (r898), from item 159's report on Aria's real history. Nobody's call — two budgets are set (first launch ≤ 1 core; a map within 5 s), and this item meets both.**

Depends on: 159
Landed: slice 1 (`846d4b5`, r911).

[Item 159](159-first-launch-takes-the-machine.md) paced the first launch's background passes to half a core, and measured it on Aria's 3.3 GiB `~/.claude` (`perf-daemon-ab --cold`, r898 against r873, under the landing lock): from 10 s on, the paced ingest holds 48–55% every second, as designed.
**But the first 9 s run at 100–112% (8 one-second samples over the 1-core budget), and the map can't draw until they end, so on this history it appears at about 9 s against a 5 s budget.** Those 9 s are the daemon's first `Load`, not the ingest: it reads a window of every stored transcript, and every live transcript whole, at about 100 MiB/s, before the paced pass begins. The synthetic home has few transcripts, so its first load is instant, and the suite never saw it.

## The fix

Make the first load smaller, not slower (pacing it would trade the map budget for the core budget):
- before the first snapshot, read only what drawing the map needs — each transcript's window, no whole live reads, which can follow once the map is up;
- on a warm start, serve the stored sessions' catalogue from the statistics store rather than re-reading their transcripts.

Tests: a synthetic home shaped like the real one (several hundred transcripts, a few GB, some live ones large) in the first-launch acceptance test, so the suite sees what the real history does; on it, the first snapshot within the 5 s budget measured as work (CPU-seconds, as item 159's gate does), and no 1 s sample over one core. Re-measure on the real history with `perf-daemon-ab --cold` and add it to `performance/reports/`.

## Where the 9 s went

On Aria's home (file sizes only, 2026-10-22): 195 transcripts, 3,290 MiB.
The 30 touched in the last day held 708 MiB, which is the first load's ~750 MiB: live transcripts were read whole, and stopped ones active in the plant's day from that day's start, which for an item session is nearly the whole file.
The windows of the other 165 came to about 20 MiB.
The day's work sat mostly in two sessions, of 482 MiB and 116 MiB.

## Slice 1 (`846d4b5`, r911)

With a background pass (the daemon, or a city reading the home itself), the first load reads every transcript through its window, live ones included, and leaves the long reads to a **later read** (`pkg/state/laterread.go`).
It is paced at half a core like item 159's passes, yields every MiB inside a file (`pkg/claude/yield.go`), waits at the load gate, and shares one lane with the statistics ingest and the whole read, ahead of them, so together they stay at one pass's share.
A live transcript's reader is handed to the loads after it, so they carry on from where it stopped.
While it runs, the snapshot carries its progress, so the footer's reading line marks the usage and the plant as filling in (manager, 2026-10-22: the boats carry usage at a glance, and silently low figures after every restart would mislead).

`TestLaterReads` (`pkg/state`) holds the window, the whole usage after, the reader carried on, the plant, the lane, and the reading line during the read and gone after.
`TestFirstLaunchLoad` (`testing/acceptance/firstlaunch_test.go`) starts the daemon on a home modelled on Aria's: 400 stopped sessions of 256 KiB, live sessions of 288 and 16 MiB, and stopped ones active today of 64 and 16 MiB.
Red-checked with the later read off, its hand-over off, and the lane off.

## Deviations

- **The first load is paced lightly, at three quarters of the wall clock** (manager, 2026-10-22), only on the first load and only with a background pass.
  Even all windows, 400 transcripts took about a CPU-second to parse, and with the collector's threads beside it the first 1 s sample reached 111–115% in 3 of 4 runs.
  Paced, five runs peaked at 66–84%, for about a quarter of a second more before the map.
- **The suite gates the first snapshot in bytes, not CPU-seconds** (manager, 2026-10-22).
  No CPU-seconds limit separates the fix from what it fixed:

  | code | CPU-seconds to the first snapshot | bytes read by then |
  | --- | --- | --- |
  | fixed, at a load of 9 | 0.66, 0.79, 0.87, 0.64 | 52 MiB |
  | fixed, at a load of about 30 | 0.71, 1.03, 1.65 | 52 MiB |
  | before the fix | 1.50, 1.57, 2.13 | 434 MiB |

  So the gate is the bytes, at most each transcript's window and 16 MiB (66 MiB), which load cannot move.
  The CPU-seconds are logged every run, and the 2 CPU-second budget is asserted only at a real size, with `BOTROPOLIS_FIRST_LAUNCH_GB` set, for a report.
  Every 1 s sample is still held to one core; the code before the fix broke it at 110–118%.
