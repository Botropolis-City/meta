# 233. A building's cached look differs from its direct draw when a kit level is drawn up

**Fixed 2026-10-24 (`72d8615`, r982). Filed 2026-10-24 (r971), found by item 162's session during its slice 14. Nobody's call — a defect.**

[Item 192](192-a-building-is-drawn-from-many-pieces-every-frame.md) caches each building's look, and `--check-looks` compares every cached look with the building drawn directly from its pieces.
At zoom 1.5, which draws the z1 kit level up by 1.5 on `main`, `--check-looks` finds 12 cached looks that differ from the direct draw by up to 35 levels, in small patches of about 10×7 pixels; residential tier 5 differs at every heading.
`TestBuildingLooksCached` and `TestBuildingSheetLights` run only at zoom 1 and zoom 2, where no level is drawn up, so neither has ever looked at a drawn-up zoom, and a wheel step lands on one.

The same guards' "lit pixels show through the building in front" check also misfired at drawn-up zooms, because its solid margin of 2 pixels did not grow with the sprite's rim; item 162's slice 14 scales that margin with the draw-up (recorded in [item 162](162-the-city-holds-gigabytes-of-gpu-memory.md)).

**The fix.** Find why the cached look and the direct draw diverge when drawn up — most likely the cache is rendered at the level's own size and scaled, while the direct draw scales each piece, so filtering differs at piece seams — and make the two the same, or cache per drawn-up scale.
Then run both acceptance checks at every zoom a wheel step reaches, drawn up or not, not only at 1 and 2.

## Answered while building

- **What is wrong** (the session "item 233", 2026-10-24): `--check-looks` fails at four of the seven wheel steps (0.25, 0.35, 0.75 and 1.5), not only drawn-up ones, because `bake()` moves the camera in world units, so the bake's screen values carry different float noise from the direct draw, and four discrete decisions sitting on exact ties go the other way (a wall row's truncation, a square pane's planks, float32 sign text, nail discs). Patching ties only moves them.
- **The fix** (manager, 2026-10-24, option A): bake at the frame's own coordinates, drawing the run with the camera unmoved into a scratch clipped to the look's box and copying the box with a whole-pixel blit, which is exact by construction. The scratch is the still layer's existing pan scratch, shared, not a new frame-sized texture, since [item 162](162-the-city-holds-gigabytes-of-gpu-memory.md) is cutting GPU memory against a budget still missed. A look whose box runs off the target is drawn directly that frame and baked once on screen.
- **The lights check at small zooms** (manager, 2026-10-24): it runs at every step too; a fixture that cannot exist at a zoom (signs are not painted under 7 pixels, and so on) says so from the same constant the drawing code uses, not a hand-made skip list, and the 1-pixel station-label case at 0.35 and 0.75 is investigated in this item.
- **The test tree** (manager, 2026-10-24): approved as sent, both acceptance checks over `city.ZoomSteps`, and `TestBakeDrawsAtTheFramesCoordinates` in `pkg/render`, with one more case: baking allocates no texture beyond the shared scratch.
- **The flicker the ties cause while panning**, which the direct draw has too, is filed as [item 237](237-a-panning-camera-can-flip-a-facades-planks.md).
- **Looks that run off the frame** (manager, 2026-10-24, option A2): a look box is generous (room for a sign three buildings wide, and flags), so drawing every look cut by the frame's edge directly took full zoom from 11 straight draws a frame to 34, against `TestFullZoomDrawsWhatIsOnScreen`'s ceiling. Such a look is baked the old way, with the camera moved, and marked inexact; drawn from the cache with its box wholly on the frame, it is baked again exactly, once. A building cut by the edge may show a tie flip until it is wholly on screen, and no ceiling rises; the held-arrow pan's counts must not rise either, or it comes back. `--check-looks` draws each look on a frame big enough to hold its box (a 1024 cell), since the check is about looks on the frame. Rejected: raising the ceiling to 34 (A3), which gives back what items 161 and 162 cut.

## Closed

Fixed in `72d8615` (r982), with its changelog entry in `27f7d8f`.
A look whose box lies on the frame is now baked at the frame's own coordinates, with the frame's camera, into the pan's shared scratch, and copied onto its page by whole pixels, so it matches the direct draw by construction.
A look cut by the frame's edge is baked the old way, marked inexact, and baked again exactly the first time it is drawn wholly on the frame (`TestBakeDrawsAtTheFramesCoordinates`).
`TestBuildingLooksCached` and `TestBuildingSheetLights` now run at every zoom in `city.ZoomSteps`, 0.25 to 2, and pass at all seven.
Reverting every bake to the moved camera fails `--check-looks` again.

The cause was wider than drawing up: the moved camera's float noise flipped exact ties, at 0.25, 0.35 and 0.75 as well as 1.5.

What the lights check found at small zooms:
- **Fixtures that can't be drawn there.** A district sign, a painted sign or a landmark's name that its own layout leaves off below `ui.MinSignPx` is now printed as "not checked". It fails only if left off even at `city.MaxZoom`, where it would never be drawn.
- **The 1-pixel station label at 0.35 and 0.75 was the check misfiring, not light leaking.** The label covers 98% of the pixel and lets through one level of a lit window. But the check measured that against the lit window minus the label over a dark tower, which is a few levels for a pale label. So one level of rounding read as half the light.
  A thing laid over the frame is now measured against the light itself. Things in the depth sort keep the measure their half-transparent case is calibrated to. Leaving the label out of the scene still fails the check.

The held-arrow pan's counts, from one headless run each of the `ebitenginedebug` city on main's code (`73cc0c7`) and on this:

| | main | item 233 |
| --- | --- | --- |
| worst commands, indices, switches (frames 15–60 and 20–55) | 30, 4782, 6 | 30, 4782, 6 |
| still: composes, redos, rects, direct, shifts | 0, 1, 11, 0, 3 | 0, 1, 11, 0, 3 |
| looks over frames 15–60: hits, misses, bakes | 1230, 0, 0 | 1230, 0, 0 |

**Deviations from the tree:**
- "It should draw with the frame's own camera, unmoved" is not a unit test: unit tests here cannot read pixels. The acceptance check proves it pixel for pixel at every step, and the mutation above confirms that.
- `TestLightFixturesFollowTheirLayouts` was added for the fixtures' layouts.
- `lookdraw.go:bake` joins `TestRawDrawSites`'s allowed list, because it copies a baked look onto its page.
