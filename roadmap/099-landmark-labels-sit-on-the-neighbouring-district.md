# 99. Landmark labels sit on the neighbouring district

**Open, in progress since 2026-10-19 in the session "item 99". Filed 2026-10-16 (r510) at Aria's request, from frames of items 86 and 88. Nobody's call — a defect.**

Landed: slice 1 (`5e70cb3`, r676).
Landed: slice 2 (`5fd2ef2`, r684).
Landed: slice 3 (`e5f0e5a`, r692).

The "power plant" label is drawn beside the kiln district's plaque rather than on the power plant, in `docs/screenshots/r470-item-86-ladder.png`, `r490-item-86-ladder.png`, `r505-item-86-overgrown.png` and `r488-item-88-district-signs.png`, and the library's label is just as far from the library.

Both labels anchor at the projected `Rect.Min` of the landmark's plot (`botropolis/pkg/render/game.go`, the `if labels` blocks for `c.Plant` and `c.Library`).
In the isometric projection that corner is the plot's back corner, which lands on or beside whatever stands behind it, here a district's plaque.

The fix: anchor each landmark's label on the landmark itself, over the top of its drawn sprite, the way district and building signs are placed, and test that the label's point lies within the landmark's projected bounds at every heading.
