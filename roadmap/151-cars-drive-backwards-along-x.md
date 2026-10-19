# 151. Cars drive backwards on roads that run along x

**Fixed 2026-10-19 (`d53af2a`, r762; `9ecdb39`, r767). Filed 2026-10-19 (r757) at Aria's request, from item 147. Nobody's call — a defect, for 0.2.3.**

Depends on: nothing
Landed: slice 1 (`d53af2a`, r762).

[Item 147](147-the-engine-says-the-models-window.md) added a nose-first test for trains (`TestEngineRunsNoseFirst`, against a nose position the atlas now records) and found the map drew every train backwards on stretches running along x: the shared `carTurn` (`botropolis/pkg/render`) turns a piece the wrong way along x, which nobody saw because the old diesels looked alike from both ends. Trains now use `trainTurn`.
Cars still use `carTurn` and are modelled the same way, so a car on a road running along x very likely drives backwards — as do the vans, trucks and anything else that turns with it.

## The fix

Record each road vehicle's nose in the atlas as item 147 did for engines, drive every one round the roads at four headings in a nose-first test, and turn them with the corrected rule (sharing `trainTurn`'s, or one rule for both).

Tests: every road vehicle (sedan, van, the job trucks, the inspector's car) runs nose-first along x and along y at every heading; mutate red by restoring `carTurn`'s old x case. A frame for Aria with cars going both ways on an x road.

## Closed

Every vehicle now turns by one rule, `vehicleTurn` (item 147's `trainTurn`, renamed), and `carTurn` is gone (`d53af2a`, r762).
The Car Kit models its vehicles nose toward −y like the Train Kit, so `carTurn` ran the traffic, the message van, the delivery truck and the depot's truck backwards along x.
Our own site trucks were modelled nose toward +y, so it ran the skip trucks and the cement mixer backwards along y instead; they are now built facing −y like every kit.
The atlas records a nose for every road vehicle and tug, and `TestVehicleRunsNoseFirst`, `TestTrafficRunsNoseFirst` and `TestInspectorRunsNoseFirst` hold them to it along ±x and ±y at all four headings; restoring `carTurn`'s x case turns every one red along x.

**Beyond what was asked:** item 147's `TestEngineRunsNoseFirst` projected top-down, the camera's zero value, rather than isometrically as the map draws.
That catches a piece turned 180° but can pass one turned onto the wrong axis.
All four nose tests now project isometrically, skip samples that sit exactly on a corner, and the engine test must check more than four samples so it cannot pass on nothing.
The trains were nose first throughout.

**The tugs' bow.**
Aria ruled on 2026-10-19 that a tug's bow is its pointed hull, after this session had described the tugs to her backwards from the sprite.
Measured in the model, the tug's pointed, raked end is at −y and its flat stern, carrying the funnels, at +y; the cargo ship is built the same way, with its pointed bow and deckhouse at −y, the end she ruled its bow (`botropolis/pkg/render/gauges.go`, `bowHome`).
So `vehicleTurn` already sails the tugs bow first and nothing was turned.
The atlas now records each vehicle's width across its nose end and its tail end, and `TestTugBowIsPointed` requires a tug's nose end to be the narrower (`9ecdb39`, r767); swapping the recorded ends fails it.

Frames, all in `botropolis/docs/screenshots/`, approved by Aria on 2026-10-19 except the last two, sent for her after:
`r762-item-151-vehicles-nose-first.png` (every vehicle under an arrow for each direction), `r762-item-151-cars-both-ways.png` (two cars passing on the kiln–tidepool road), `r766-item-151-tugs-bow-first.png` (arriving tugs sailing top right to bottom left, bow leading) and `r766-item-151-tug-hull-from-above.png` (the tug and the cargo ship in plan, −y at the top).
The leaving tug is on the first frame only; it sails after its building is cleared, later than the clip ran.
