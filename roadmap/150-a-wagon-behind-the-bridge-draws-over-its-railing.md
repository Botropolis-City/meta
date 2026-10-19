# 150. A wagon just behind the bridge draws over the deck's far railing

**Open, in progress since 2026-10-19 in the session "item 150". Filed 2026-10-19 (r754) at Aria's request, from item 146's frames. Nobody's call — a defect.**

Depends on: nothing

[Item 146](146-the-bridge-ramp-is-a-solid-wedge.md)'s session found, and its frames show (`botropolis/docs/screenshots/r750-item-146-ramp-h0.png` and `-h270.png`, and item 132's `r707-item-132-bridge-h0.png`), that a train piece standing just beyond the deck's footprint, on the far side from the camera, draws over the deck's far railing. Under the deck the order is right; just past it, the depth sort puts the wagon in front.

## The fix

Sort a raised drawable against a ground one by the raised one's footprint and height, so anything behind the deck in depth draws before it whatever its screen position; the deck and its railings draw after a wagon behind them and before one in front.

Tests: at four headings, a wagon on the cell just behind the deck should draw before the deck and its railings, a wagon in front after them, and item 132's under-the-span order still holds. Frames for Aria at 0 and 270.
