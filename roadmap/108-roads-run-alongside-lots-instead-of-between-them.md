# 108. Roads run alongside two lots instead of from one to the other

**Open. Filed 2026-10-17 (r571) at Aria's request. Nobody's call — the design is chosen.**

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
