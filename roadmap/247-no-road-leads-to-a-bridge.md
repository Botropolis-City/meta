# 247. No road leads to a bridge, so its ramp comes down onto grass

**Open. Filed 2026-10-25 (r1031), found by item 220's session from its frame. Nobody's call — a defect.**

Depends on: 220

Both bridges' island ends stand on a street in the plan's sense (`IsStreet`, a cell of the ring road's corridor), but nothing draws road there.
`layRoads` (`botropolis/pkg/city`) lays road only on corridor cells that a route between two districts crosses — "a corridor nothing travels is belt" — and no route goes to a bridge, so the ramp comes down onto grass and the nearest road is a block away.
The T where a road meets the bridge, from 2026-10-18 ([item 132](132-the-bridge-road-crosses-the-rail-and-ends-in-the-water.md)), is drawn only `if road[land]`, so it never shows either.
Delivery trucks already drive that unpaved corridor to the bridge ([item 217](217-a-delivery-truck-drives-beside-the-bridge-not-on-it.md)), so the corridor is travelled, and the rule that leaves it as belt is wrong about it.
It was true of the first bridge before [item 220](220-a-large-island-gets-a-second-bridge.md) added a second, and item 220's frame shows it at both: crops at 2x from its `hero.png` were made in that item's worktree as `dist/item-220/frames/landing1.png` and `landing2.png`.

## The fix

Treat each bridge's landing as a route's end: lay road from the nearest laid road to every landing, through the corridor the trucks already drive, so the T is drawn and the trucks are on road.
It stays keyed on the landing, as item 218 keyed the roads remembered for a plan, so a bridge that is anchored keeps its road.

Tests: for each bridge (data-driven over `Bridges()`), its landing cell is road and a run of road connects it to a district's road; the T is drawn at the landing; a truck's path to the bridge runs only on road cells; a city whose districts have no road between them still gets road to its bridge. A frame of the two-bridge city at fit for Aria.
