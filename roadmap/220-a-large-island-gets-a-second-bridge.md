# 220. A large island gets a second bridge

**Done 2026-10-25 (`2be10d6`, r1030). Filed 2026-10-24 (r966) at Aria's request. Nobody's call — Aria set the threshold on 2026-10-25, below.**

Depends on: 218
Landed: slice 1 (`2be10d6`, r1030).

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

## Closed

Done by slice 1 (`2be10d6`, r1030), with its changelog entry under `[Unreleased]`.
Once the island holds `SecondBridgeAt` (16) project districts, `City.placeBridge` lands a second bridge on the east road, opposite the first, and the layout keeps its row as an omitempty `"bridge2"` mark, so it stays as the island grows, across a restart, and after the count falls back.
`City.Bridges` lists both; each truck takes the bridge nearer its building by road, and a truck re-routed while the island grows keeps to the bridge on its own coast.
Each bridge has its own fog bank (`City.FogOf`), and the renderer draws every bridge and its fog through `bridgesInSort`.
Tests: `TestSecondBridge` in `botropolis/pkg/city/pullrequests_test.go` (one bridge at 15, two at 16, the opposite coast, the nearer bridge for trucks, anchoring, restart, the count falling back, the east rail leg moving only with the second bridge, and its one ramp cell), and `TestEveryBridgeIsDrawn` in `botropolis/pkg/render/bridges_test.go` (every bridge's parts and its own fog in the depth sort, the boats' run passing under the second deck, and a boat under it drawn beneath the deck at every heading).
The boat case passed before any code changed, so it was mutated: dropping the deck's level failed all eight of its cases.

**Deviation, flagged for Aria:** the east rail leg does not stand in the belt's outer column next to the river, because that failed `TestRiverKeepsClear`: the river's banks wander up to 0.45 of a cell into that column. With the second bridge the east belt widens by a cell instead, so the rail still moves out one cell and the bridge keeps its ramp cell. Accepted by the manager on 2026-10-25.

**Frames**, git-ignored in the item 220 worktree at `botropolis/dist/item-220/`: `out/bridges/hero.png` and `overview.png`, a 17-district city at the fit view with both bridges, and `frames/liner-58.png`, `liner-58-zoom.png` and `liner-61-zoom.png`, the weekly usage liner at the second deck.
Aria judged them on 2026-10-25: the deck is too low for the liner, whose upper decks and funnels stand above it, which is [item 252](252-the-second-bridge-is-too-low-for-the-liner.md).
Neither bridge has a road laid to its landing, so each ramp comes down onto grass (`frames/landing1.png`, `landing2.png`); that was true of the first bridge before this item, and is [item 247](247-no-road-leads-to-a-bridge.md).
