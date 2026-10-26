# 247. No road leads to a bridge, so its ramp comes down onto grass

**Fixed 2026-10-26 (`5f68e6f`, r1065). Filed 2026-10-25 (r1031), found by item 220's session from its frame. Nobody's call — a defect.**

Depends on: 220
Landed: slice 1 (`5f68e6f`, r1065).

Both bridges' island ends stand on a street in the plan's sense (`IsStreet`, a cell of the ring road's corridor), but nothing draws road there.
`layRoads` (`botropolis/pkg/city`) lays road only on corridor cells that a route between two districts crosses — "a corridor nothing travels is belt" — and no route goes to a bridge, so the ramp comes down onto grass and the nearest road is a block away.
The T where a road meets the bridge, from 2026-10-18 ([item 132](132-the-bridge-road-crosses-the-rail-and-ends-in-the-water.md)), is drawn only `if road[land]`, so it never shows either.
Delivery trucks already drive that unpaved corridor to the bridge ([item 217](217-a-delivery-truck-drives-beside-the-bridge-not-on-it.md)), so the corridor is travelled, and the rule that leaves it as belt is wrong about it.
It was true of the first bridge before [item 220](220-a-large-island-gets-a-second-bridge.md) added a second, and item 220's frame shows it at both: crops at 2x from its `hero.png` were made in that item's worktree as `dist/item-220/frames/landing1.png` and `landing2.png`.

## The fix

Treat each bridge's landing as a route's end: lay road from the nearest laid road to every landing, through the corridor the trucks already drive, so the T is drawn and the trucks are on road.
It stays keyed on the landing, as item 218 keyed the roads remembered for a plan, so a bridge that is anchored keeps its road.

Tests: for each bridge (data-driven over `Bridges()`), its landing cell is road and a run of road connects it to a district's road; the T is drawn at the landing; a truck's path to the bridge runs only on road cells; a city whose districts have no road between them still gets road to its bridge. A frame of the two-bridge city at fit for Aria.

## Answered while building

- **A spur, not every truck's way** (manager, 2026-10-25, from the fix above): each landing not on road gets road along the cheapest avenue walk from the nearest laid road, or from the nearest driveway when the city has none; trucks prefer road and join it at their first chance. Paving every district's truck walk would add 96–118 cells at 17 districts, half the ring, which changes the city's look and was not asked for; trucks from districts with no road still cross unpaved corridor until they reach road, and the closing section says so for Aria.
- **The road misses the ramp by half a road** (Aria, 2026-10-25, on the frames: *"The roads don't attach to the ramps. They're half a road width off"*): the spur reached each landing along the ring road and turned onto the bridge, and the kit's only bend is a quarter arc around the cell's inner corner, half a cell off the ramp's centreline. Aria chose, 2026-10-26, the T with a short stub: the road runs one cell past the landing and ends in the kit's end piece, so the landing is a T; held by `TestRoadMeetsTheRamp` at every landing, heading and atlas zoom.
- **A road that moves** (manager, 2026-10-26, from the item's own "a bridge that is anchored keeps its road"): the spur started at whichever road was nearest, so it moved as roads came and went; it now starts from the nearest district's driveway by the plan and is kept while the plan and the landing stand.
- **The night draw ceiling** (manager): stays at 37; the new road's lamps must join the existing lamps' batch, and only a shown impossibility goes to Aria.
- **The fixed road and the trucks** (manager, 2026-10-26): a bridge road from a fixed driveway can end short of the roads between districts (a 3-cell gap each side in the 17-district city), so where such a road ends within reach of it a short joining road links the two, laid and faded like any route; the bridge's own road never moves, and every truck on road reaches the bridge on road.
- **A turn, and a driveway that moved** (manager, 2026-10-26): a camera turn re-lays the bridge road as it re-lays every road from the camera-facing driveways (item 108). The bridge road starts from the district's current driveway, not its camera-facing side, so a district never shows a second pad that means nothing; it follows that driveway once, the first time the driveway moves for a road, and then stays.
- **The bridge road's lamps** (Aria, 2026-10-26, asked by the manager with item 247's measurements: 36 with no lamps, 37 with the district roads', 40 with the bridge road's, against a ceiling of 37): land the bridge road and its joints unlit, so 37 holds, and get the lamps back through [item 257](257-every-lamp-glow-splits-a-batch.md), a light layer for every glow.

## Closed

Fixed by slice 1, three commits in botropolis: `5f5132d` (r1063), `6c42f2d` (r1064) and `5f68e6f` (r1065), with its changelog entry under `[Unreleased]`.
Every bridge's landing that no route reaches gets road from the nearest lot, out of that lot's own driveway,
and the road runs on a cell past the landing, so the landing is a T whose stem runs along the ramp.
Where a run of road between districts does not meet a bridge's road, a short joint links the two by the cheapest walk and fades with that road;
the bridge's road itself stays put.
A delivery truck crosses as few unpaved corridor cells as it can, then takes the shortest way among those.

Tests: `TestRoadToTheBridge` in `botropolis/pkg/city/bridgeroad_test.go` holds that the landing is road, joined to a driveway and to the bridge, and a T; that every truck from a district on road runs on road; that the anchored landing keeps its road and a second bridge gets its own; that the bridge road is the same cells as roads come and go, follows a driveway that moves once and then stays, and keeps while a joint fades; and that no lamp stands on it.
`TestRoadMeetsTheRamp` in `botropolis/pkg/render/rampmeet_test.go` reads the landing's road piece off the atlas at every heading and both zooms.
`TestRoadJoinsTheBridge` gained a case that no road is laid beyond a route that already reaches the landing.
Each was red before the code it holds, and the truck routing and the driveway start were mutated red.

**Deviations, flagged for Aria:**

- `TestRoadMeetsTheRamp` holds the road's middle within 3 pixels of the ramp's, not the 1 the manager asked for.
  The kit's own straight piece, measured the same way, sits up to 2.5 pixels off its cell's middle at some headings, where the atlas rounds its anchor, so a pixel is finer than the art.
  The T measures 0.55 at worst; the bend that was there measured 5 to 23.
- The bridge road and its joints are unlit until item 257 lays every lamp's glow in one layer; lit, they took the metropolis's night frame from 37 draws to 40.
- A truck from a district with no road of its own still crosses unpaved corridor until it reaches road.
  Paving every truck's whole way instead would have laid 96 to 118 of the 17-district city's 246 corridor cells.
- Preferring road can make a long way round: in the 17-district test city a truck from d04 takes a 32-cell road detour over 9 unpaved cells.
- A camera turn lays the bridge road again from the driveways the camera now faces, as it does every road (item 108).

**Frames**, git-ignored in the item 247 worktree at `botropolis/dist/item-247/`: `out/bridges/hero.png`, the 17-district city at fit with both bridges, and `landing1.png` and `landing2.png`, 2x crops of each landing as a T.
Aria on the first frames (2026-10-25): *"The roads don't attach to the ramps. They're half a road width off."*
On these (2026-10-26): *"Approve and close"*.
[Item 252](252-the-second-bridge-is-too-low-for-the-liner.md) raises the second bridge's deck in the same code, and item 257 puts the bridge road's lamps back.
