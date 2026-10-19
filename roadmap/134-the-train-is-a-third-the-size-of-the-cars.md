# 134. The train is a third the size it should be beside the cars

**Open, in progress since 2026-10-19 in the session "item 134". Filed 2026-10-19 (r685) at Aria's request, from item 132's pause. Nobody's call — the scale is measured and the change is small.**

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

The kit stays the Kenney Train Kit (`botropolis/design/art-sources.md`); its pieces are chunky, so the train stays shorter than a real one in proportion, as the cars are.

## Tests and frames

- A test that a wagon's footprint is at least the car's width ratio says it should be: wagon width over sedan width, read from the atlas, within a band around 3.3 m / 1.8 m, so the scale cannot drift back.
- A test that the longest trains fit the loop with a gap, on the smallest test island.
- Frames for Aria: item 78's frame again, at r685 and after, with a car and the bridge road in view.
