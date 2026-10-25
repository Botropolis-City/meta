# 220. A large island gets a second bridge

**Open, in progress since 2026-10-25 in the session "item 220". Filed 2026-10-24 (r966) at Aria's request. Nobody's call — Aria set the threshold on 2026-10-25, below.**

Depends on: 218

Aria, 2026-10-24: *"it could expand once if there's a lot of traffic or if the island starts to get really large we could add a second bridge."*

## The want

When the island passes a size threshold, a second bridge leaves from another coast, so a large city shows its growth and trucks from the far districts take the nearer bridge. It is placed once and anchored as item 218 anchors the first.
Widening a bridge for traffic was discussed and held: "a lot of traffic" needs a measure and a threshold, and a second lane is hard to see at the fitted view; revisit once a second bridge exists.

**For Aria:** the threshold (rows of island, number of districts, or sessions), and which coast the second bridge takes.

Tests: below the threshold one bridge, above it two; a truck takes the bridge nearer its building; both stay put as the island grows; a frame of a large city with both bridges.

## Answered while building

- **The threshold and the coast** (Aria, 2026-10-25, asked by the manager): by districts, on the far coast. A second bridge appears once the island holds 16 or more districts and leaves from the coast opposite the first; each truck takes whichever bridge is nearer its building.
- **Which way the far coast goes** (Aria, 2026-10-25, asked by the manager): east, over the river. The first bridge leaves west, so the second is a raised deck over the east road, the rail, the river and the land beyond it, out to sea, with boats passing under and its own fog at the far end. The east rail leg moves out one cell only when the second bridge exists, giving it a ramp cell as on the west, so other cities' edges are unchanged.
- **Once placed** (manager, 2026-10-25, from "placed once and anchored" above): it stays, saved in `layout.json`, even if the count falls back below 16, until the plan has no coastal street on that side. The count is of project districts, not the depot.
- **Where the east rail goes** (manager, 2026-10-25): the belt's outer column failed `TestRiverKeepsClear`, since the river's banks wander up to 0.45 of a cell into it, so with the second bridge the east belt widens by a cell instead: the rail still moves out one cell, the bridge keeps its ramp cell, a belt column stays between rail and river, and cities without the second bridge are unchanged. Whether the tallest ship clears the deck is for Aria, from the frame.
