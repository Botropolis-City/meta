# 206. The city lays itself out whole on snapshots that change nothing it draws

**Fixed 2026-10-23 (`29de039`, r945). Filed 2026-10-22 (r910), from item 201. Nobody's call — the budget is set (an unfocused city ≤ 1% of a core).**

Depends on: nothing
Landed: slice 1 (`66ea0d6`, r931).
Landed: slice 2 (`6fc0674`, r932).
Landed: slice 3 (`3fb64ad`, r941).
Landed: slice 4 (`29de039`, r945).

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
3. **The streets are laid once per plan, heading and walks** (r941).
   With the walks remembered, laying road on the corridors was about a fifth of what was left.
   It reads the walks' paths and otherwise only what the plan decides (corridors, bridge, island, the plan's lamps and trees), so what was laid last for each heading stands while the plan and every path are what they were.
   An activity-only snapshot went from 8.5–12 ms to 7.0–7.3 ms, and one changing a session's state from 10 ms to 4.8–6.8 ms.
   Building the groups' order input (about 2 ms a snapshot here) is left alone unless the real measurement says it matters (the manager, 2026-10-23), since a key over every member's order lines costs about what building it does.
   `Breakdown`'s SQL query is not per snapshot: the ledger reuses a window for `LedgerCache` and the sessions' costs for 30 s.
4. **The gate's city gets roads** like the real history's, with its layout share reported before and after, so the gate is as hard as what users pay (the manager, 2026-10-22).
   The test asserts the daemon made all 80 before it measures, so a change to how edits become roads cannot quietly return it to a roadless fixture (the manager, 2026-10-23).
   Landed r945: 80 of the busy city's sessions edit a file in another project, the same pairs `realSized` joins; with the edits made by a tool the daemon ignores, the test fails at 0 of 80.

## Closed

Fixed in four slices, r931–r945.

**With the real history's roads, the unfocused dashboard spent 22–27% of a core laying out, and now spends 0.8%.**
Measured on the gate's busy city, given its 80 roads, unfocused and visible, a line every 200 ms:

| | share of a core | laying out 16 snapshots | load |
| --- | --- | --- | --- |
| before (pkg/city at `c9f119a`) | 26.6%, 21.9% | 3,994 ms, 3,293 ms | 5–7 |
| after (slices 1–3, `3fb64ad`) | 0.81%, 0.82% | 111 ms, 111 ms | 6–15 |

**The gate passed at 0.72% the whole time, because its city had no roads.**
Neither `realSized` nor the busy city had a single road between projects, so the cost the real history paid most for (walking every road along the avenues again for every snapshot) was the one cost nothing measured.
It is the pattern in `CLAUDE.md` once more: a guard fails where its own inputs come from.
A fixture is an input, and one that is missing a shape the real data has passes every check that iterates over it.
So the gate now asserts its city has its 80 roads before it measures.

A snapshot that moves only activity times now makes no plan, walks no street, lays no road and reads no order, and its city equals one built from scratch (`TestSnapshotLaysOutOnlyWhatChanged`); its buildings are still made fresh, since each carries its session.
`BenchmarkSetSnapshot/activity-only` on `realSized` with roads: 140–285 ms and 43 MB a snapshot became 7.0–7.3 ms and 2.8 MB.
`Scene.GroundGeneration` (slice 2) lets item 207's standing layer skip its dry pass on such snapshots.

**Deviations, for Aria:**

- **The real-history figure is owed by item 207**: one busy-unfocused run on the real history, after 207's slice 3, measures both items against r910, and the benchmark session adds its numbers to both files (the manager, 2026-10-23).
- **Groups' order input is still built on every snapshot**, about 2 ms of the 7; it is left unless that run says it matters.
- **The changelog's entry for item 201 said an unfocused city laid out for under 1% of a core**; that held only without roads, and a new entry says what it costs now.
