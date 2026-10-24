# 237. A panning camera can flip a facade's planks or a pane's wall row from frame to frame

**Open, in progress since 2026-10-24 in the session "item 237". Filed 2026-10-24 (r978), found by item 233's session. Nobody's call — a defect.**

[Item 233](233-cached-building-looks-differ-when-drawn-up.md) traced cached building looks that differ from the direct draw to discrete decisions sitting exactly on a tie, which float noise in the camera's offset tips one way or the other.
Item 233 removes that noise from the cache, by baking at the frame's own coordinates, but two of the ties are real in the direct draw as well, because the camera's offset changes as it pans:

1. `nail()` (`botropolis/pkg/render/facade.go`, about line 148) truncates `(c.Y-origin.Y)/scale` to pick a wall row, and at scale 1.5 pane corners land exactly on row edges;
2. `planksFor`'s `ribbon = length >= height` compares a pane that is exactly square, so its plank layout flips.

So while the camera pans, a pane's planks or the row it nails to can change between frames: a one-pixel flicker.

**The fix.** Make each decision from world or sprite units that the camera cannot move, not from screen values: the wall row from the pane's position in the sprite, and the ribbon test from the pane's own size with a fixed tie-break.
Tests: across a pan of whole and fractional pixels at every zoom step, each building's planks and wall rows stay the same.
