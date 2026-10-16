# 98. District signs grow without limit when zoomed in

**Open, in progress since 2026-10-16 in the session "item 98". Filed 2026-10-16 (r510) at Aria's request, from a frame of item 86's. Nobody's call — a defect.**

Item 88 put a sign on each district: a board on a post with the district's name and whose move it is.
Its size is `cam.Zoom * districtSignScale` (`botropolis/pkg/render/districtsign.go`, `districtSign`), with a floor below which the board is left off and nothing above, so zoomed in it grows past any readable size: in `docs/screenshots/r505-item-86-overgrown.png` a board reading "the agents' move" covers half a building.

The fix: clamp the board's scale at a maximum as well as a minimum, so close up it stays the size of a readable sign and the post carries it.
Tests: data-driven over zooms, the board's drawn height never exceeds the cap, and below the floor it is still left off.
