# 220. A large island gets a second bridge

**Open. Filed 2026-10-24 (r966) at Aria's request. Nobody's call — Aria set the threshold on 2026-10-25, below.**

Depends on: 218

Aria, 2026-10-24: *"it could expand once if there's a lot of traffic or if the island starts to get really large we could add a second bridge."*

## The want

When the island passes a size threshold, a second bridge leaves from another coast, so a large city shows its growth and trucks from the far districts take the nearer bridge. It is placed once and anchored as item 218 anchors the first.
Widening a bridge for traffic was discussed and held: "a lot of traffic" needs a measure and a threshold, and a second lane is hard to see at the fitted view; revisit once a second bridge exists.

**For Aria:** the threshold (rows of island, number of districts, or sessions), and which coast the second bridge takes.

Tests: below the threshold one bridge, above it two; a truck takes the bridge nearer its building; both stay put as the island grows; a frame of a large city with both bridges.

## Answered while building

- **The threshold and the coast** (Aria, 2026-10-25, asked by the manager): by districts, on the far coast. A second bridge appears once the island holds 16 or more districts and leaves from the coast opposite the first; each truck takes whichever bridge is nearer its building.
