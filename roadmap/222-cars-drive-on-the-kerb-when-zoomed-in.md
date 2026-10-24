# 222. Cars drive on the kerb when zoomed in

**Open. Filed 2026-10-24 (r966) at Aria's request, from item 162's frames. Nobody's call — a defect.**

Aria, 2026-10-24, on item 162's 3x crop of a car at zoom 2.0: *"the cars are not on the road when zoomed"*.

**Where it shows.** [Item 162](162-the-city-holds-gigabytes-of-gpu-memory.md)'s frames of the staged metropolis at zoom 2.0 by the tidepool lot (`dist/item-162-options/kits/pair-zoom2-car-3x.png` in its worktree): the green car sits on the pale kerb at the road's outer edge, beside the lot, rather than in a lane. It is the same in both halves, so it is not item 162's change.

**Where to look.** Cars keep right by `laneOffset = 0.2 * city.CellSize` (`botropolis/pkg/render/lanes.go`, [item 153](153-cars-keep-to-the-right.md)), from paths along the avenue centres. Aria saw it "when zoomed", so a suspect that only shows up close is the sprite's anchor not scaling with the kit level drawn (an offset right at fit and wrong at z2). The others: the lane offset measured against a road narrower than a cell once the kerbs are counted, or this car's path running along the lot's edge instead of the avenue's centre.

## The fix

Every road vehicle's wheels stay on the carriageway in its own lane, at every zoom and every heading.

Tests: for each heading, the car's drawn footprint at fit, zoom 1.5 and zoom 2.0 lies inside the carriageway, kerbs excluded; a zoom 2.0 frame for Aria.
