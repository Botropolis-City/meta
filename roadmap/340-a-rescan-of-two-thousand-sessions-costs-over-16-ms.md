# 340. A rescan of two thousand sessions costs over its 16 ms of a core, climbing since 0.3.4

**Open, in progress since 2026-11-07 in the session "item 340". Filed 2026-11-03 (r1256), from 0.4.0's release gate. Nobody's call — the budget is set; the daemon is over it.**

Depends on: nothing
Landed: slice 1 (`d4a9daf6`, r1318).
Landed: slice 2 (`0c2e7fae`, r1319).

`TestARescanAtTwoThousandSessions` read a median of 16.63 ms of a core at the 0.4.0 candidate `cad2504` (16.59, 16.63, 16.63, 16.80, 21.20) against its bar of 16 ms, pinned and settled.
It has climbed a release at a time: 14.6 ms at r1209 (0.3.4), 15.0 at r1230 and r1233, 15.7 at r1245, 16.6 at r1256.
Raw: `~/.local/state/botropolis-perf/test-performance-r1256-cad2504-release-0.4.0-20261103-080606/`.
Core time counts instructions plus kernel time, so I/O drift can move it; an A/B of the test alone at `3acddcf` against `cad2504` tells code from drift, and the suspects in the range are item 333's loader changes (the quiet set, the grouping signature, reviewed groups) that run on every snapshot.

## The fix

Name what the rescan does more of than at r1209 (a CPU profile of the rescan at both), and take it back under 16 ms with margin; the bar does not move.

## Answered while building

- **It is the code, not drift** (item 340's session, 2026-11-07): an A/B at v0.3.4 (r1209) and r1315, three alternating rounds, reads 28.2 M instructions a rescan against 33.2 M (+18%), with kernel time flat; counters around each step put the whole rise in `groupViews`, 4.69 M to 9.84 M, from item 333's slice 1 (`f0fa16c2`) — a suggestion picked and described for each of 1,012 loose sessions on every rescan, by string-built keys, beside a second session index built alongside `titleOf`'s; a pprof of 3,000 rescans at each agrees.
  Raw runs in `~/.local/state/botropolis-perf/item-340-rescan-ab-20261107/`.
- **Two slices, approved** (roadmap manager, 2026-11-07): slice 1 takes `groupViews` back (one presized index shared with `titleOf`, suggestions compared field by field once per detection, one description per member), to about 29.0 M, ~15.2 ms, which meets the bar without margin; slice 2 reads the temporary-directory roots once per pass in `pkg/state/districts.go` instead of once per session, to about 21.5 M, ~11.5 ms, 28% under it.
  Guards: a characterisation of the suggestion order, an allocation bound per group member, an allocation bound for assigning 2,000 settled sessions, and the perf-tier rescan test itself, red today.
