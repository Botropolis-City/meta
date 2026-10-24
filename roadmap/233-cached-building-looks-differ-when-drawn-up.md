# 233. A building's cached look differs from its direct draw when a kit level is drawn up

**Open, in progress since 2026-10-24 in the session "item 233". Filed 2026-10-24 (r971), found by item 162's session during its slice 14. Nobody's call — a defect.**

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
