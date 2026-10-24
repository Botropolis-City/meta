# 237. A panning camera can flip a facade's planks or a pane's wall row from frame to frame

**Fixed 2026-10-24 (`0773851`, r994, and `d47d27d`, r995). Filed 2026-10-24 (r978), found by item 233's session. Nobody's call — a defect.**

[Item 233](233-cached-building-looks-differ-when-drawn-up.md) traced cached building looks that differ from the direct draw to discrete decisions sitting exactly on a tie, which float noise in the camera's offset tips one way or the other.
Item 233 removes that noise from the cache, by baking at the frame's own coordinates, but two of the ties are real in the direct draw as well, because the camera's offset changes as it pans:

1. `nail()` (`botropolis/pkg/render/facade.go`, about line 148) truncates `(c.Y-origin.Y)/scale` to pick a wall row, and at scale 1.5 pane corners land exactly on row edges;
2. `planksFor`'s `ribbon = length >= height` compares a pane that is exactly square, so its plank layout flips.

So while the camera pans, a pane's planks or the row it nails to can change between frames: a one-pixel flicker.

**The fix.** Make each decision from world or sprite units that the camera cannot move, not from screen values: the wall row from the pane's position in the sprite, and the ribbon test from the pane's own size with a fixed tie-break.
Tests: across a pan of whole and fractional pixels at every zoom step, each building's planks and wall rows stay the same.

## Answered while building

- **The plan and the test tree** (manager, 2026-10-24): approved as sent, one slice. `planksFor` and `nail` work in the sprite's own pixels (integer pane corners, the wall row from a sprite-pixel corner, the ribbon test on the integer pane), and only the finished planks are mapped to the screen, through a pure `boardsOf` that `shutter` and `shutterEach` share, so both ties sit on integers the camera cannot move. `TestBoardsHoldStillWhileTheCameraPans` in `pkg/render/facade_test.go` pans 0–3 pixels in eighths on both axes at every zoom step, kind and heading, red on main first; item 233's `--check-looks` in `make land` holds the cached looks to the direct draw as before. Away from the ties the planks are drawn exactly as today, so no frame for Aria.
- **One case dropped** (the session "item 237", 2026-10-24, agreed by the manager): the test is red on main only for the square-pane tie (industrial-1 and -2 at zoom 0.35, headings 0 and 270). The wall-row tie cannot be shown on today's art: plank corners land on row edges (1,199 over 2,000 seeds), but both rows' spans always cover them, so either row nails the same plank, and a constructed wall did not tip it across 90,000 pans; a test that cannot fail is not shipped. The fix still decides the wall row in sprite pixels, so that tie is gone by construction.

## Closed

Fixed in `0773851` (r994) and `d47d27d` (r995), with its changelog entry in the first.
A boarded building's planks are laid and nailed in the sprite's own pixels by `boardsOf` and only then put on screen, so the camera's offset decides neither the ribbon test nor the wall row a corner nails to.
`TestBoardsHoldStillWhileTheCameraPans` pans every kind, heading and zoom step by whole and fractional pixels on both axes.
It failed on main's screen-space logic for industrial-1 and industrial-2 at zoom 0.35, and passes now.

**Deviations, flagged for Aria:**
- The pan steps are a fixed list from 0 to 3 pixels, including tenths, rather than eighths: dyadic steps add no float noise, so eighths alone never tipped a tie.
- The wall-row case was dropped, as recorded above.
- **The ribbon tie-break is strict** (`d47d27d`): a pane exactly as long as it is tall is a window, not a ribbon, as `ribbonRatio` says.
  A new `TestPlanks` case fails on `>=`.
  With `>=`, the first landing failed `--check-looks` at 0.35, by one pixel off by 4 levels on boarded industrial tier 1 from heading 0.
  On main, that camera's float noise had happened to make the pane a window.
- **For item 233:** as a ribbon, that look's bake differed from the direct draw by one pixel, though both placed the planks identically.
  So baking at the frame's coordinates is not exact for every geometry.
  Today's art no longer shows it, and the manager has the finding.
