# 108. Roads run alongside two lots instead of from one to the other

**Open, in progress since 2026-10-18 in the session "item 108". Filed 2026-10-17 (r571) at Aria's request. Nobody's call — the design is chosen.**

Depends on: nothing
Landed: slice 1 (`7bc9bc4`, r615).
Landed: slice 2 (`4098d79`, r619).
Landed: slice 3 (`90f4380`, r622).
Landed: slice 4 (`1a2848e`, r629).
Landed: slice 5 (`4f60920`, r637).

A road between two districts is the street traffic between them runs on, and today it can run beside both lots and into neither.
`routeStreets` in `botropolis/pkg/city/streets.go` takes every street cell touching each district's block (`kerbCells`); when two blocks face each other across one avenue they share kerb cells, and the road becomes that shared stretch, so the cars drive up and down an avenue parallel to both lots.
Only blocks that share no kerb are joined by a walk along the streets (`walkStreets`), and even then the walk starts and ends at any kerb cell, not at a point that reads as the lot's own.

Aria, 2026-10-17: *"We need it to run from lot to lot not just on a road parallel with them. Like the road should run between them."*
A straight link between lots was set aside because the districts read as blocks of one city, not separate towns.

## What it becomes

Agreed with Aria on 2026-10-17:

- **A driveway per lot**, one, on the side of the block facing the camera, so a car is seen leaving and every lot reads the same way.
- **A road is driveway, streets, driveway**: the shortest path along the street grid from one lot's driveway to the other's, preferring streets on the camera's side where two paths tie, so traffic stays in view. Two roads that share a stretch of street share it, with more cars on it.
- **Paved only while it is used**, as roads already are: a driveway and the street cells on a road are drawn while that exchange is active and fade when it is quiet; one car still means one active exchange.
- **Roads join districts**, not each session's building.
- Everything that drives a road follows the same path: cars, item 89's message vans (`messagePath` in `botropolis/pkg/city/messages.go`), and its merge truck, which leaves by the bridge.

**Hovering a car** (Aria, 2026-10-17): *"hovering the cars should show a line along their path either by highlighting the roads of their path or by drawing a new line across it. Also, it should mute out everything but the lots it's traveling between."*
So pointing at a car highlights its whole path, driveway to driveway, and recedes everything but the two lots it runs between, the way selecting a group already focuses its districts (`Highlight` in `botropolis/pkg/city/highlight.go`); its card keeps saying which group it belongs to, as it does now.

## Tests

- data-driven over pairs of districts — neighbours across one avenue, across a corner, far apart — a road should start at one lot's driveway and end at the other's, and never be only cells beside both;
- every lot's driveway should be on its block's camera-facing side, and every car, van and truck path between two lots should pass through both driveways;
- pointing at a car should highlight exactly its path and recede every district but its two;
- a frame for Aria of the r541 workday scene, before and after, with one car hovered.

## Answered while building

- **The driveway follows the camera** (manager, 2026-10-18, from the item's reason that a car is seen leaving): each block's driveway is under the middle of the side facing the camera at the current heading, and turning the map re-places the streets; doors and `Route`'s kerb end stay on the south side for now.
- **The routing and its tree** (manager, 2026-10-18): lot end, driveway, the shortest street walk with a tie-break toward the camera, the other driveway, lot end; the shared-kerb shortcut goes; cars, vans, the merge truck and item 109's skip and mixer trucks all follow the path; hovering a car lights its road and its two districts and recedes every other lot, road and building. Approved with cases that a driveway is paved only while its road is active.
- **A driveway goes where its roads are shortest** (Aria, 2026-10-18), replacing "always camera-facing": with every driveway facing the camera, a lot directly behind another reached it only by going round its whole depth (ten cells for a one-cell avenue). So each lot's one driveway is on the side that keeps the total length of its roads shortest, the camera-facing side when it ties or is within a cell or two; an even side's middle rounds toward the camera.
- **Roads join** (Aria, 2026-10-18, from item 115's frame): *"The road should always attach to any other existing road. So we'd need a T piece here."* Wherever a road meets another — the bridge road, another district's road, any paved street — it joins with a T or a crossing, never running beside it unjoined.
- **Driveways do not move** (Aria, 2026-10-18, in the item's own session: *"We don't want driveways moving"*), replacing "the driveway follows the heading" and refining "where its roads are shortest": a lot's driveway is chosen once, when it first has a road, by the rule above, and kept in the layout beside its district type, as a side of its block and a cell along it.
  New roads route to it, turning the camera does not move it, and neither does a restart.
  A lot with no road yet has no kept driveway and defaults to the side facing the camera.
- **The hover fades everything not tied to the car** (Aria, 2026-10-18, from item 102's r624 frame): the car, its road and its two districts stay at full strength, and everything else fades, labels and plates included. Item 102's labels ask `Highlight.FadesDistrict` and `FadesRoad`.
- **The frames passed** (Aria, 2026-10-18, r636), with two changes: a road's tag steps off its car, cars joining the label layout as things labels avoid; and a hovered car's two districts keep their group-line station dots lit while the lines themselves fade. The bridge's T is trusted to its test, since no demo road now reaches the bridge.
