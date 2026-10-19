# 134. The train is a third the size it should be beside the cars

**Fixed 2026-10-19 (`a637ff2`, r699). Filed 2026-10-19 (r685) at Aria's request, from item 132's pause. Nobody's call — the scale is measured and the change is small.**

Depends on: nothing
Landed: slice 1 (`67fb3d5`, r696).
Landed: slice 2 (`a637ff2`, r699).

Aria, 2026-10-19, on item 78's frame (`botropolis/docs/screenshots/r674-item-78-train-hovered.png`): *"The train is way too small compared to that road. Is the train just too small, or is that road really big compared to other roads/cars."*
The train is too small; the road is right.

## Measured

Each kit is scaled once, when its sprites are rendered: `SCALE` in `botropolis/tools/render-sprites/render.py:140`, the Car Kit at 0.12 and the Train Kit at 0.25 of their native units per cell.
With the car as the ruler (a 2.5 m sedan drawn a third of a cell), one cell is about 8.3 m:

| piece | on the map | by the car's scale | real |
| --- | --- | --- | --- |
| road tile | 1 cell, two lanes | ≈ 8.3 m | 8–10 m for two lanes and verges |
| wagon (`train-carriage-container-*`) | ≈ 0.68 × 0.21 cell | ≈ 5.6 × 1.8 m | 14–18 × 2.9 m |
| locomotive (`train-diesel-*`) | ≈ 0.6 × 0.21 cell | ≈ 5 × 1.75 m | 18–22 × 3.1 m |

Widths are read from the z2 atlas's sprite boxes (`botropolis/pkg/assets/kits/kits-z2.json`): at one heading a cell's diamond is 267 px wide, the sedan 61, a wagon 119 and a locomotive 108.
So roads, cars and lots agree with each other, and the train is about a third of its length and three fifths of its width beside them.

## The fix

- Raise the Train Kit's `SCALE` from 0.25 to about 0.40, so a wagon is about 1.1 × 0.36 cell; re-render the atlas.
- Scale `wagonGap` (`botropolis/pkg/render/rails.go`) with it, from 0.72 cell to about 1.15, and `trainGap` in proportion.
- Leave `railGauge` at 0.22 cell: a body about twice its gauge is how a real train sits on its rails.
- `MaxWagons` is 6, so the longest train becomes about 8 cells; check the loop still holds every model's train with gaps between them on the smallest island the tests build.
- `drawMessage` (`botropolis/pkg/render/pullrequests.go`) also draws `kitWagons[0]`, at 0.9, for a message on a group's line: decide with a frame whether that carriage grows with the train or keeps today's size by its shrink.
- The Watercraft Kit shares 0.25 in `SCALE` and is out of scope.

## Remeasured, and decided (2026-10-19)

The table above reads the code's constants in the wrong unit.
`wagonGap` and `railGauge` are multiples of `city.Tile`, and a cell is three tiles (`BuildingSize`), so the shipped train already stood each wagon two thirds over the one behind it, 0.72 tile apart for a wagon two tiles long.
Raising `wagonGap` to 1.15 would have left them overlapping, and the gauge was a body 3.4 times its width, not twice.

Measured on the models in Blender: the sedan is 1.50 × 2.55 kit units, a wagon 1.00 × 2.70 and the locomotives 1.0–1.2 × 2.40.
The kit's wagon is stubby and its sedan wide, so no one scale matches a real wagon's width beside a car (about 1.7 times) and its length (about 3.3 times).
At 0.40 a wagon is 2.2 times the sedan's width and 3.5 its length, wider than a real wagon; at 0.31 the width is right and it stays short, which is what Aria complained of.
**The scale is 0.35** (the manager, for Aria, 2026-10-19): 1.9 times the width and 3.1 times the length, about a tenth off real on each.

So the fix changed shape, approved by the manager the same day:

- the pipeline records each car and train piece's footprint in the atlas (`foot`), and `assets.Footprints()` reads it from the manifest alone;
- carriages are spaced by half of each one's length plus a coupling, so the spacing cannot drift from the scale again; trains run a wagon and a half clear of each other;
- the gauge is 0.55 of the wagon's width, from the same footprint.

The tests are `TestVehicleScale` (`botropolis/pkg/assets/kits_test.go`): the wagon is 1.6–2.1 times the sedan's width and 2.8–3.6 its length, and a locomotive is at least four fifths a wagon's width; and `TestTrainOnTheLoop` (`botropolis/pkg/render/rails_test.go`): no two neighbouring carriages overlap, the gauge is between half the wagon's width and its width, and three six-wagon trains on the smallest test city's loop are each a wagon's length clear of the next.
Putting the old 0.72-tile spacing back turns the second red, and putting the old scale back into the manifest turns the first.
The loop on the smallest test city is 204 tiles; a six-wagon train and its gap take about 25.

## Frames, and the manager's verdicts (2026-10-19)

The frames are in `botropolis/docs/screenshots/` (`7ed2100`, r697): `r685-item-134-train-before.png` and `r696-item-134-train-after.png`, the workday demo zoomed toward the loop with the bridge road and a car in view, and `r696-item-134-message-carriage-options.png`, a sheet of the message carriage at today's size and grown with the train beside the van, a loop wagon and a sedan — a sheet rather than a map frame, because no demo scenario sends messages.
Aria delegated judging them to the manager that night, and these are the manager's verdicts, which she can reopen:

- **0.35 passes.** The wagons are separate and read clearly against the cars, which answers "way too small", and 0.40 would make them wider than real beside a car.
- **A message's carriage keeps today's size**, 0.61 cells long (slice 2). It rides the group lines over lots, badges and station dots, and at a loop wagon's size it would cover the badges. `TestMessageCarriage` holds the length against the atlas's footprint, so it does not grow with the next change of scale either.

The kit stays the Kenney Train Kit (`botropolis/design/art-sources.md`); its pieces are chunky, so the train stays shorter than a real one in proportion, as the cars are.

## Tests and frames

- A test that a wagon's footprint is at least the car's width ratio says it should be: wagon width over sedan width, read from the atlas, within a band around 3.3 m / 1.8 m, so the scale cannot drift back.
- A test that the longest trains fit the loop with a gap, on the smallest test island.
- Frames for Aria: item 78's frame again, at r685 and after, with a car and the bridge road in view.

## Closed

Fixed in two slices: the Train Kit at 0.35 with every carriage spaced by its own footprint and the gauge set under its body (`67fb3d5`, r696), and a message's carriage held at its old size (`a637ff2`, r699); the changelog entry is `84938b8`.
`TestVehicleScale`, `TestTrainOnTheLoop` and `TestMessageCarriage` hold them, and the frames are `7ed2100` (r697).

**For Aria, deviations from what was filed:** the scale is 0.35, not about 0.40; the spacing is read from the atlas rather than set as a larger `wagonGap`, because the shipped wagons already overlapped; and both of the frame's calls — 0.35, and the message carriage at its old size — were the manager's that night, so either can be reopened.

**Aria's verdict** (2026-10-19, reviewing the frames the roadmap manager passed overnight): the 0.35 scale and the smaller message carriage (A) are approved; she asked for an engine class by context window, and for other locomotive options, in [item 147](147-the-engine-says-the-models-window.md).
