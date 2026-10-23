# 206. The city lays itself out whole on snapshots that change nothing it draws

**Open, in progress since 2026-10-22 in the session "item 206". Filed 2026-10-22 (r910), from item 201. Nobody's call — the budget is set (an unfocused city ≤ 1% of a core).**

Depends on: nothing
Landed: slice 1 (`66ea0d6`, r931).
Landed: slice 2 (`6fc0674`, r932).

[Item 197](197-the-city-lays-itself-out-again-on-every-snapshot.md) made the city reuse its plan and group orders between snapshots, and [item 201](201-the-daemon-sends-the-whole-snapshot-on-every-update.md) sent only what changed. But `city.build` still runs whole on every snapshot, even one where only activity times moved: about 7 ms a snapshot on item 197's city, so laying out was 0.85% of a core of the unfocused dashboard's 1%. Item 201 took a fifth of it out (`DistrictNames`) and the gate passes at 0.72%, with `placeGroups`, `placeLines`, `orderSites` and the collector left — thin margin for a gate everyone's landings run.

## The fix

Skip or narrow the build when a snapshot changes nothing that shapes the city (activity times, counters, scan progress), and reuse placed groups and lines while their inputs are equal; a from-scratch build stays the oracle.

Tests: a snapshot that moves only activity times builds nothing again and draws what a from-scratch build draws; item 201's unfocused gate's measured layout share falls (report before and after).

**Busy measurement** (benchmark session, 2026-10-22, real GPU, two sessions writing every 200 ms): `city.build` is 22% of an unfocused city's 2.74% of a core. The rest is drawing, filed as item 207.

## Slices

Planned with the roadmap manager on 2026-10-22, which approved the test trees and ruled on the questions below.

**Neither fixture had a road.**
`realSized`, which the benchmark and item 197's from-scratch tests use, and the gate's busy city in `hidden_cost_test.go` had no roads between projects, so the cost the real history pays most for was never measured.
The busy run on the real history logged 41.5 ms of layout a snapshot where the gate saw about 7, and on that run's profile `placeStreets` was 46% of `build`.
With 80 roads added to `realSized`, a snapshot that moves only activity times cost 140–285 ms, almost all of it walking every road along the avenues again.
It is the guard failing where its own inputs come from, once more (the manager, 2026-10-22).

**"Builds nothing again" means lays out nothing again** (the manager, 2026-10-22): no plan made, no street walked, no order read.
The buildings are still made fresh for every snapshot, because each carries its session, and the quiet rung moves with activity times.

1. **A street is walked once per plan and heading** (r931).
   A walk depends only on the plan's avenues, the heading its ties break toward, and its two ends, so the scene's memo keeps each by those.
   Each remembered plan carries an id, and a city on a new plan lets go of every walk on the old one (the manager: test that it holds none).
   That also covers a turned camera, which placed the streets twice a snapshot: once facing the default way in `build`, then again in `Face`.
   `realSized` now has 80 roads, and the from-scratch comparison includes each road's path, the laid street cells and the corridors.
   An activity-only snapshot went from 140–285 ms and 43 MB to 8.3–12 ms and 2.8 MB (`BenchmarkSetSnapshot/activity-only`, 265U, under load).
   Mutated red: without the plan in the key, only the stale-walk test fails, because a new project leaves the avenues the old walks ran on where they were.
2. **The ground has a generation of its own** (r932), for item 207, whose standing layer keyed on `Scene.Generation` and so ran its dry pass on every snapshot.
   `Scene.GroundGeneration` moves only when `ground` moves.
   `ground` is derived from the city after every build, turn and depot release, from exactly the fields item 207 walked from `composeStatic`, MCP calls and road counts included, by root and ID rather than pointer.
   A detail change moves it too.
   It is tested against a from-scratch build in every case; whether the list misses a field `composeStatic` reads is guarded by item 207's randomised render check (the manager, 2026-10-22).
   Landing it failed once on the unfocused gate, at 1.15% inside the full suite at a load of 14, against 0.73% rerun alone; item 209 has since made that case log and skip.
3. **The rest of an activity-only snapshot**: groups' order input, the districts, and the garbage `build` makes.
   `Breakdown`'s SQL query is not in it: the ledger already reuses a window for `LedgerCache` and the sessions' costs for 30 s, so it runs on a timer, not per snapshot.
4. **The gate's city gets roads** like the real history's, with its layout share reported before and after, so the gate is as hard as what users pay (the manager, 2026-10-22).
