# 238. A baked look can still differ from the direct draw by a pixel for some shapes

**Open. Filed 2026-10-24 (r992), found by item 237's session. Nobody's call — parked until it shows on the art.**

[Item 233](233-cached-building-looks-differ-when-drawn-up.md) bakes each building's look at the frame's own coordinates, which made the cache match the direct draw at every zoom step on today's art.
While landing [item 237](237-a-panning-camera-can-flip-a-facades-planks.md), one industrial building's square pane briefly drew as a ribbon at zoom 0.35, heading 0, and its cached look then differed from the direct draw by one pixel, four levels, even though both placed the planks identically.
So the frame-coordinate bake is not exact for every geometry; the session's guess is float32 vertex noise between where Ebitengine keeps the scratch image and the frame.
Item 237's strict tie-break means today's art no longer draws that pane as a ribbon, and `--check-looks` passes at every step, so nothing shows it now.

**When to take it up.** If `--check-looks` fails again on new art, start from this case: draw a ribbon pane through the bake and directly, compare the vertices Ebitengine receives, and find where they differ.
