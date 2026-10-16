# 98. District signs grow without limit when zoomed in

**Fixed 2026-10-16 (`a8dc964`, r536). Filed 2026-10-16 (r510) at Aria's request, from a frame of item 86's. Nobody's call — a defect.**

Item 88 put a sign on each district: a board on a post with the district's name and whose move it is.
Its size is `cam.Zoom * districtSignScale` (`botropolis/pkg/render/districtsign.go`, `districtSign`), with a floor below which the board is left off and nothing above, so zoomed in it grows past any readable size: in `docs/screenshots/r505-item-86-overgrown.png` a board reading "the agents' move" covers half a building.

The fix: clamp the board's scale at a maximum as well as a minimum, so close up it stays the size of a readable sign and the post carries it.
Tests: data-driven over zooms, the board's drawn height never exceeds the cap, and below the floor it is still left off.

## Answered while building

- **Where the cap sits** (manager, 2026-10-16, from the item's "the size of a readable sign"): the board stops growing at its zoom-1 size, `min(zoom, 1) * 1.3`, so the cap is the size it was already readable at rather than a new number; the post keeps scaling with the uncapped zoom, so close up it lifts the board clear of the session's plaque. The floor is unchanged. Aria judges the frame.
- **The test tree** (manager, 2026-10-16): approved as proposed, in `pkg/ui/districtsign_test.go` — never taller than at zoom 1 across the zoom steps and beyond the maximum, higher above its foot past zoom 1, left off below the floor, and unchanged at zoom 1.

## Closed

The board's geometry moved from render's `districtSign` to `ui.DistrictSignBoard` (`botropolis/pkg/ui/signage.go`), which caps the board at its zoom-1 size while the post goes on scaling with zoom.
The tests in `pkg/ui/districtsign_test.go` were red at zooms 1.5, 2 and 4 before the cap and are green after.
`botropolis/docs/screenshots/r536-item-98-capped.png` (`6165e64`) is the r505 overgrown scene again, zoomed in the same way, from a staged demo home: kiln's "the agents' move" board stays sign-sized on a taller post.
Aria passed it on 2026-10-16.
District signs have not been released yet, so the changelog says it in item 88's `[Unreleased]` entry rather than as a fix (`924223a`).
No deviation from what the item asked.
