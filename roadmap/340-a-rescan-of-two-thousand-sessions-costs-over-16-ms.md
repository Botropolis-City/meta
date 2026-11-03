# 340. A rescan of two thousand sessions costs over its 16 ms of a core, climbing since 0.3.4

**Open. Filed 2026-11-03 (r1256), from 0.4.0's release gate. Nobody's call — the budget is set; the daemon is over it.**

`TestARescanAtTwoThousandSessions` read a median of 16.63 ms of a core at the 0.4.0 candidate `cad2504` (16.59, 16.63, 16.63, 16.80, 21.20) against its bar of 16 ms, pinned and settled.
It has climbed a release at a time: 14.6 ms at r1209 (0.3.4), 15.0 at r1230 and r1233, 15.7 at r1245, 16.6 at r1256.
Raw: `~/.local/state/botropolis-perf/test-performance-r1256-cad2504-release-0.4.0-20261103-080606/`.
Core time counts instructions plus kernel time, so I/O drift can move it; an A/B of the test alone at `3acddcf` against `cad2504` tells code from drift, and the suspects in the range are item 333's loader changes (the quiet set, the grouping signature, reviewed groups) that run on every snapshot.

## The fix

Name what the rescan does more of than at r1209 (a CPU profile of the rescan at both), and take it back under 16 ms with margin; the bar does not move.
