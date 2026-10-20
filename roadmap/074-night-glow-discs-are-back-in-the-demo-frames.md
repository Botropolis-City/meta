# 74. Night glow draws as a grid of discs again, in the demo frames

**Fixed 2026-10-19 (`a945b61`, r779). Filed 2026-10-10 (r376), from looking at the first `make demo-media` output while building the website.**

Depends on: nothing
Landed: slice 1 (`a945b61`, r779).

Item 37 capped each storey's glow at half a storey so a lit building stops wearing a column of merged discs, and it was checked at fit and at zoom.
The demo frames show the same shape at fit: working buildings at night carry a grid of translucent beige discs, about three across and a storey apart, sitting over the facade and rising above the roof line.
The discs are beige rather than the white of item 37's saturated column, so this may be a second mechanism rather than item 37 coming back.

Where to look, all in `dist/demo/` after `make demo-media`:

| shot | where |
| --- | --- |
| `hamlet/hero.png` | the two working buildings at the top of the city, around (860–1110, 140–330) |
| `layers/night.png` | tidepool's and orchard's blocks, around (460–820, 260–520), and the tower at (1310, 330) |
| `hamlet/drift.mp4` | every frame after the zoom; worst at the closest point, 5–9 s |

The daytime frames of the same scenarios have no discs, so whatever draws them is night-only.

**Why it matters now:** the hamlet is the best-looking night scenario and the obvious second hero for botropolis.city, and these frames are the ones a visitor sees first.
The website uses the metropolis by day until this is fixed.

## Fixed

**It was a second mechanism, not item 37 coming back.** Item 37's storey cap still holds.
`nightLights` lit every storey of a lit building at its finished height and never asked whether the building was standing.
In the demo stills, the lit lots were sessions still arriving by tug — `Rising` 0, drawn as a vacant plot — so their windows floated over empty ground, three discs a storey.
During the build that follows, the same glow sat above the rising roof, which is what the drift clip showed at 5–9 s.
The build already had a `Site.Lights` ramp for "the lights come on", and nothing read it.

`Scene.Lights` now reads it: off while the tug sails and while a building rides a truck, coming on at the end of the build, and fading in with it under reduced motion.
`nightLights` skips a building whose lights are off and scales each disc by them (`a945b61`, r779, tests in `pkg/city/construction_test.go`, `haul_test.go` and `pkg/render/glow_test.go`).

Frames, before and after, at r780 (`1db46d9`): [the hamlet hero](../botropolis/docs/screenshots/r779-item-74-hamlet-hero.png), [layers at night](../botropolis/docs/screenshots/r779-item-74-layers-night.png), and [the drift through one arrival](../botropolis/docs/screenshots/r779-item-74-drift-arrival.png) at 5.5, 6.5, 7.5 and 8.5 s.

**For Aria:** the windows now light at the end of a build (0.88–1 of it), after the scaffolding comes down. If they should come on as the floors rise, that is one line in `SiteAt`.
Why the stills catch sessions mid-arrival at all is item 154's finding, filed separately: the city sails every live session in at start-up.
Once that is fixed, the hero shows those sessions standing and lit.

**Aria on the frames** (2026-10-19): every finished part of a building should light, floor by floor, and the frames should show lit buildings — [item 155](155-windows-light-as-each-floor-is-finished.md).
