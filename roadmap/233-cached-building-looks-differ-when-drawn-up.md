# 233. A building's cached look differs from its direct draw when a kit level is drawn up

**Open. Filed 2026-10-24 (r971), found by item 162's session during its slice 14. Nobody's call — a defect.**

[Item 192](192-a-building-is-drawn-from-many-pieces-every-frame.md) caches each building's look, and `--check-looks` compares every cached look with the building drawn directly from its pieces.
At zoom 1.5, which draws the z1 kit level up by 1.5 on `main`, `--check-looks` finds 12 cached looks that differ from the direct draw by up to 35 levels, in small patches of about 10×7 pixels; residential tier 5 differs at every heading.
`TestBuildingLooksCached` and `TestBuildingSheetLights` run only at zoom 1 and zoom 2, where no level is drawn up, so neither has ever looked at a drawn-up zoom, and a wheel step lands on one.

The same guards' "lit pixels show through the building in front" check also misfired at drawn-up zooms, because its solid margin of 2 pixels did not grow with the sprite's rim; item 162's slice 14 scales that margin with the draw-up (recorded in [item 162](162-the-city-holds-gigabytes-of-gpu-memory.md)).

**The fix.** Find why the cached look and the direct draw diverge when drawn up — most likely the cache is rendered at the level's own size and scaled, while the direct draw scales each piece, so filtering differs at piece seams — and make the two the same, or cache per drawn-up scale.
Then run both acceptance checks at every zoom a wheel step reaches, drawn up or not, not only at 1 and 2.
