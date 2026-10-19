# 153. Cars drive down the middle of the road; they should keep to the right

**Done 2026-10-19 (`b473c0a`, r769). Filed 2026-10-19 (r765) at Aria's request.**

Depends on: nothing
Landed: slice 1 (`b473c0a`, r769).

Aria, 2026-10-19: *"Cars should travel on the correct side of the road rather than the middle. Assume all our roads are two way and make all cars travel on the right side (meaning right as opposed to left). That way if cars are going in different directions they don't overlap in the middle."*
Today every road vehicle follows its road's centre line, so two cars going opposite ways on one road pass through each other (`botropolis/docs/screenshots/r762-item-151-cars-both-ways.png`).

## The fix

Every road is two-way, and every road vehicle — cars, the message vans, the delivery and depot trucks, the skip truck and mixer, the inspector's car — drives in the lane to the right of its direction of travel: offset from the centre line by half a lane, perpendicular to the road, on the right-hand side as it travels. Turns and junctions (the T joins, driveways into lots, the bridge ramp and deck) keep each vehicle in its lane through the corner, so nothing jumps sideways. The offset is a fraction of the road's drawn width, so it holds at every zoom and heading, and the lane line item 146 draws on the bridge is the line between the two lanes.

Builds on item 151's `vehicleTurn` (vehicles run nose-first); the train is not a road vehicle and is unchanged.

Tests: a vehicle travelling either way along x and along y sits right of the centre line by half a lane at every heading; two vehicles going opposite ways on one road never overlap; through a turn the lateral offset changes continuously (no jump); on the bridge each direction keeps its lane; a frame for Aria of two-way traffic on a road and through a junction.

## Done

Every road vehicle places itself through one rule, `keepRight` (`botropolis/pkg/render/lanes.go`): its path moved half a lane to the right of travel, mitred at corners so it keeps its lane round a bend, and holding both lane ends where the path turns back, so turning back is a short drive across the road.
Half a lane is 0.2 of a cell, a quarter of `road-straight`'s asphalt as the atlas draws it, and the lane line down the middle of the road is the line between the two lanes.
The traffic, the message vans, the delivery truck (over the bridge too), the depot's truck, the skip truck and mixer, and the inspector's car all use it; a message carriage on the rails, the trains and the tugs are unchanged.

The inspector's car and the site trucks leave forward, with a U-turn across the road at their stop, nose first, rather than reversing (the manager's ruling, 2026-10-19).

`TestKeepRight` holds the lane half a lane right at every heading, on asphalt between the kerb and the lane line as the atlas draws it, two opposite lanes further apart than the widest road vehicle, and no jump through a corner or a turn back; `TestEveryRoadVehicleKeepsRight` holds each vehicle along x and y both ways, on the bridge, and the inspector's way out.
Zeroing the offset, keeping left, or dropping the mitre each turns them red.
One older test changed: `TestTrafficCars` (items 85, 108) held every car exactly on the centre line, and now holds it within a lane of it.

**For Aria:** the frame [r769-item-153-cars-keep-right.png](../botropolis/docs/screenshots/r769-item-153-cars-keep-right.png) is a straight road with a T junction from heading 0 and heading 180, traffic both ways and turning, each car where the code puts it, drawn from the atlas rather than in the app, because the staged demo cities have one short road with one car on it.
