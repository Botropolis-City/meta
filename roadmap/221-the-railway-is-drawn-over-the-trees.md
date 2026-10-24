# 221. The railway is drawn over the trees

**Open, in progress since 2026-10-24 in the session "item 221". Filed 2026-10-24 (r966) at Aria's request, from item 162's frames. Nobody's call — a defect.**

Aria, 2026-10-24, on item 162's zoom 2.0 coast frame: *"The train tracks are rendering over the trees"*.

**Where it shows.** [Item 162](162-the-city-holds-gigabytes-of-gpu-memory.md)'s frames of the staged metropolis at zoom 2.0 on the east sea coast (`dist/item-162-options/shore/pair-zoom2-coast.png` in its worktree): where the loop passes behind a tree, its sleepers and rails cross the tree's trunk and canopy instead of being hidden by it. It is the same in the "now" and the option halves, so it is not item 162's change.

**Where to look.** `isoRails` (`botropolis/pkg/render/rails.go`) strokes the sleepers and rails through `g.paint` and flushes, and `isoGround` calls it right after the shore, before the depth-sorted pass in which every tree is a `standingAt` item. So by order the trees should cover the rail. Suspects: the ground pass and the standing pass being composed in a different order since the dry pass and replay ([item 193](193-a-still-city-is-redrawn-whole-every-frame.md), [item 212](212-every-frame-re-records-every-drawable.md) touches the same recording); `g.paint`'s batch reaching the screen after the sprites it was queued before; or the rail being drawn a second time somewhere later in the frame.

## The fix

Draw the rail as ground: under every tree, building and vehicle that stands on or behind it, at every zoom and with the ground layer cached or not.

Tests: a frame's draw record puts the rail's strokes before every standing item whose footprint overlaps it; a zoom 2.0 frame of the metropolis coast for Aria.

## Answered while building

- **The cause and the fix** (manager, 2026-10-24): the order was right; park trees are drawn at alpha 0.66 (`treeTint`, item 85), so the rail shows through them. Item 85 asked for trees lower in contrast and saturation than anything hoverable, which the translucency served, not for seeing through them; so park trees are drawn opaque with the same mix baked into their colour (rgb' = 0.66·0.86·rgb + 0.34·grass at the tree's foot, for the palette the ground uses), the same pixel over grass as before.
- **The test tree** (manager, 2026-10-24): `TestParkTreesHideWhatIsUnderThem` in `pkg/render/view_test.go` replaces the draw-order test, which passes today and so cannot be red: full alpha for a park tree; a tinted texel matching the old translucent tree over its grass to 1/255; a street tree's tint unchanged; every park tree meeting a rail stroke on the zoom 2 metropolis coast at full alpha. Plus a before-and-after frame of that coast for Aria.
- **Item 85's own test** (manager, 2026-10-24): `pkg/render/groundtint_test.go`'s "it should let the ground show through, lowering its contrast" pins the cause; it was an implementation test, not in the tree Aria agreed for item 85, so it is rewritten as "it should look as it did over the grass it stands on" (to 1/255, edges included) and "it should hide what lies under it", and the approved tree goes in that file.
- **The fix's draw cost** (manager, 2026-10-24): opaque park trees drawn through a colour matrix break batching with the kit sprites beside them, 2–3 draw commands a frame on the settled metropolis (day 25, night 42). `TestTheWorkAFrameTakes`'s day and night ceilings, ratchets item 193 lowered to what it reached, rise to 25 and 42 citing item 221, in the open: the target they guard is 70, which still holds with room, and item 193's "same movers, no more than 1.25× the hamlet" case must still pass unchanged. Rejected: pre-mixed tree sprites per palette (more GPU memory, against item 162) and one shader for every kit sprite (far beyond this item).
