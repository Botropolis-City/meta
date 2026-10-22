# 206. The city lays itself out whole on snapshots that change nothing it draws

**Open. Filed 2026-10-22 (r910), from item 201. Nobody's call — the budget is set (an unfocused city ≤ 1% of a core).**

Depends on: nothing

[Item 197](197-the-city-lays-itself-out-again-on-every-snapshot.md) made the city reuse its plan and group orders between snapshots, and [item 201](201-the-daemon-sends-the-whole-snapshot-on-every-update.md) sent only what changed. But `city.build` still runs whole on every snapshot, even one where only activity times moved: about 7 ms a snapshot on item 197's city, so laying out was 0.85% of a core of the unfocused dashboard's 1%. Item 201 took a fifth of it out (`DistrictNames`) and the gate passes at 0.72%, with `placeGroups`, `placeLines`, `orderSites` and the collector left — thin margin for a gate everyone's landings run.

## The fix

Skip or narrow the build when a snapshot changes nothing that shapes the city (activity times, counters, scan progress), and reuse placed groups and lines while their inputs are equal; a from-scratch build stays the oracle.

Tests: a snapshot that moves only activity times builds nothing again and draws what a from-scratch build draws; item 201's unfocused gate's measured layout share falls (report before and after).
