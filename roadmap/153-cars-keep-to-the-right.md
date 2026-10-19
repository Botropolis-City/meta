# 153. Cars drive down the middle of the road; they should keep to the right

**Open, in progress since 2026-10-19 in the session "item 153". Filed 2026-10-19 (r765) at Aria's request. Nobody's call.**

Depends on: nothing
Landed: slice 1 (`b473c0a`, r769).

Aria, 2026-10-19: *"Cars should travel on the correct side of the road rather than the middle. Assume all our roads are two way and make all cars travel on the right side (meaning right as opposed to left). That way if cars are going in different directions they don't overlap in the middle."*
Today every road vehicle follows its road's centre line, so two cars going opposite ways on one road pass through each other (`botropolis/docs/screenshots/r762-item-151-cars-both-ways.png`).

## The fix

Every road is two-way, and every road vehicle — cars, the message vans, the delivery and depot trucks, the skip truck and mixer, the inspector's car — drives in the lane to the right of its direction of travel: offset from the centre line by half a lane, perpendicular to the road, on the right-hand side as it travels. Turns and junctions (the T joins, driveways into lots, the bridge ramp and deck) keep each vehicle in its lane through the corner, so nothing jumps sideways. The offset is a fraction of the road's drawn width, so it holds at every zoom and heading, and the lane line item 146 draws on the bridge is the line between the two lanes.

Builds on item 151's `vehicleTurn` (vehicles run nose-first); the train is not a road vehicle and is unchanged.

Tests: a vehicle travelling either way along x and along y sits right of the centre line by half a lane at every heading; two vehicles going opposite ways on one road never overlap; through a turn the lateral offset changes continuously (no jump); on the bridge each direction keeps its lane; a frame for Aria of two-way traffic on a road and through a junction.
