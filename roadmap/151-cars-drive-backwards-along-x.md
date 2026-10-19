# 151. Cars drive backwards on roads that run along x

**Open, in progress since 2026-10-19 in the session "item 151". Filed 2026-10-19 (r757) at Aria's request, from item 147. Nobody's call — a defect, for 0.2.3.**

Depends on: nothing

[Item 147](147-the-engine-says-the-models-window.md) added a nose-first test for trains (`TestEngineRunsNoseFirst`, against a nose position the atlas now records) and found the map drew every train backwards on stretches running along x: the shared `carTurn` (`botropolis/pkg/render`) turns a piece the wrong way along x, which nobody saw because the old diesels looked alike from both ends. Trains now use `trainTurn`.
Cars still use `carTurn` and are modelled the same way, so a car on a road running along x very likely drives backwards — as do the vans, trucks and anything else that turns with it.

## The fix

Record each road vehicle's nose in the atlas as item 147 did for engines, drive every one round the roads at four headings in a nose-first test, and turn them with the corrected rule (sharing `trainTurn`'s, or one rule for both).

Tests: every road vehicle (sedan, van, the job trucks, the inspector's car) runs nose-first along x and along y at every heading; mutate red by restoring `carTurn`'s old x case. A frame for Aria with cars going both ways on an x road.
