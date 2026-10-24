# 222. Cars drive on the kerb when zoomed in

**Open, in progress since 2026-10-24 in the session "item 222". Filed 2026-10-24 (r966) at Aria's request, from item 162's frames. Nobody's call — a defect.**

Aria, 2026-10-24, on item 162's 3x crop of a car at zoom 2.0: *"the cars are not on the road when zoomed"*.

**Where it shows.** [Item 162](162-the-city-holds-gigabytes-of-gpu-memory.md)'s frames of the staged metropolis at zoom 2.0 by the tidepool lot (`dist/item-162-options/kits/pair-zoom2-car-3x.png` in its worktree): the green car sits on the pale kerb at the road's outer edge, beside the lot, rather than in a lane. It is the same in both halves, so it is not item 162's change.

**Where to look.** Cars keep right by `laneOffset = 0.2 * city.CellSize` (`botropolis/pkg/render/lanes.go`, [item 153](153-cars-keep-to-the-right.md)), from paths along the avenue centres. Aria saw it "when zoomed", so a suspect that only shows up close is the sprite's anchor not scaling with the kit level drawn (an offset right at fit and wrong at z2). The others: the lane offset measured against a road narrower than a cell once the kerbs are counted, or this car's path running along the lot's edge instead of the avenue's centre.

## The fix

Every road vehicle's wheels stay on the carriageway in its own lane, at every zoom and every heading.

Tests: for each heading, the car's drawn footprint at fit, zoom 1.5 and zoom 2.0 lies inside the carriageway, kerbs excluded; a zoom 2.0 frame for Aria.

## Answered while building

- **The cause** (the session "item 222", 2026-10-24): not zoom. Item 153's keep-right offset of 9.6 units is applied on lot lanes too, which have 8 units of room either side (the inspector's route along a lot's front, `DoorInset` 8; the lanes between buildings, `BuildingGap` 16), so the inspector parks 1.6 units past the lot edge on the road tile's kerb, and the delivery, skip and mixer trucks' lot legs do the same; zoom only makes it visible.
- **The fix** (manager, 2026-10-24, option A): a leg whose midpoint lies inside a district's block keeps right by a lot lane's offset (about 3.5, so offset plus a car's half-width stays within the 8 units), and every leg on an avenue, a pad or the bridge keeps item 153's 9.6, mitred where they join. Aria's item 153 ruling is about roads (*"all our roads are two way"*); a lot lane is one vehicle wide and not a road, so two vehicles meeting head-on inside a lot may overlap, which the frame lets her overrule. Option B (moving lot-front legs deeper) was rejected: it leaves the building-gap lanes inside the buildings.
- **The test tree** (manager, 2026-10-24): approved as sent, `TestRoadVehiclesStayOnTheirGround` and `TestVehicleSpritesStandOnTheirFoot` in `pkg/render/lanes_test.go`, with `TestEveryRoadVehicleKeepsRight`'s in-lot assertions changed to the lot offset; plus a zoom 2.0 frame of a lot with the inspector parked, for Aria.
- **Two changes beyond the ruling** (the session "item 222", 2026-10-24, inside the item's "every heading"; the manager checked the frames): right-angle road turns follow the kit's quarter-ring bend instead of a mitred square corner, since cars clipped the outer kerb at every bend; and a lot's front lane moves from 8 to 16 units in from the edge (`city.FrontLane`), since a 20-long truck turning there put its nose over the kerb, so site trucks reach the driveway along the joined road. Frames for Aria: `dist/item-222/zoom2-lots-and-bends.png` and `zoom2-crops-3x.png` in its worktree.
- **The night ceiling** (manager, 2026-10-24): the change moves where vehicles stand, and one now splits a batch in the depth-sorted pass, so the metropolis by night takes 40 commands against a ceiling of 39. The ceiling rises by that one, citing item 222, under the target of 70; the cause is filed as [item 236](236-where-a-vehicle-stands-changes-a-frames-draw-count.md). Item 221 raises the same ceiling for its own cost, so whichever of the two lands second measures the combined count on its rebase and raises only to that.
- **Landing after item 236's batching fix** (manager, 2026-10-24): item 222 lands once item 236's slice 1 is on `main`, setting the metropolis ceilings to its own measured count (item 236 measured 24/41 on `51c05d1`), one over what slice 1 measures without it, and under the 26/43 the freeze held; anything above 24/41 comes back to the manager.
