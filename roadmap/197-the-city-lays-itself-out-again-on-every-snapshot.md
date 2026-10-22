# 197. The city lays itself out again on every daemon snapshot, even hidden

**Open, in progress since 2026-10-21 in the session "item 197". Filed 2026-10-21 (r876), from the laptop benchmark at r871. Nobody's call — a defect against the city's CPU budgets.**

Depends on: nothing
Landed: slice 1 (`ccca0c7`, r878).

A 60 s profile of the city on the real history (265U iGPU, `458454f`, r871, [report](../performance/reports/2026-10-21-ultra7-265u-igpu-r871.md)) puts **76% of an unfocused or hidden city's CPU in `Scene.SetSnapshot` → `city.build`**, which lays the whole city out again for every snapshot the daemon sends, whether or not anything that shapes the city changed. Within it:

- `group.Order`: 38% — regular expressions run over every site's words, and one regular expression **compiled per site and version** in `tagged`;
- `plan.Make` → `plantGround`: 29%.

It is most of [item 163](163-a-hidden-city-keeps-all-of-its-memory.md)'s CPU (a hidden city at 7.9% of a core, spikes to 34%, against 1%) and part of [item 161](161-drawing-a-frame-costs-41-ms-of-cpu.md)'s (a focused city at 83% of a core against 10%).

## The fix

Make a snapshot cost what changed in it: compile the regular expressions once; keep the ordering and the plan between snapshots and redo them only when their inputs change (sessions joining or leaving, groups, the layout); and, while the city is hidden, take snapshots without laying out until it is shown again.
From-scratch layout stays available as the oracle, as item 158 did for grouping.

Tests: a snapshot that changes only a session's state (working → waiting) lays out nothing again, and the city it draws equals the one built from scratch; a benchmark of `SetSnapshot` on a city the size of the real history (about 200 sessions in 150 projects) before and after; and an acceptance measure of a hidden city's **process CPU** under a stream of snapshots, against the 1% budget.

## Slices

Measured first with `BenchmarkSetSnapshot` (a synthetic city of 200 sessions in 150 projects, eight groups whose sessions carry 40 order lines each, 265U): 1.42 s a snapshot, 79% of it in `group.Order` and 13% in `plan.Make`.
Inside `group.Order`, `released` ran again for every pair of sites, `bumps` ran two expressions over every line for every version, and `waitsFor` and `tagged` compiled an expression on every call.

1. **`group.Order` reads each site once** (r878): 4.6 s to 28 ms for a group of 25 sites, and 1.42 s to 136 ms a snapshot.
   The order before is kept in `pkg/group/order_oracle_test.go`, and 400 generated groups read the same through both.
2. **The scene remembers its plans and its groups' orders**, and makes or reads them again only when their inputs change; a wait on a site being done follows the site's state on every snapshot.
3. **A city nobody is watching holds its snapshots**, and lays out the newest once when it is watched again; the window title follows every snapshot.
   Nobody watching includes unfocused, because item 22 decided an unfocused city draws nothing, against the budget for a minimised or unfocused city (the roadmap manager, for Aria, 2026-10-21).
   So the acceptance measure runs the city unfocused.
