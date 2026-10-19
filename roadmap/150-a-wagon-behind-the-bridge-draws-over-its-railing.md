# 150. A wagon just behind the bridge draws over the deck's far railing

**Closed 2026-10-19 by adjudication (`819f9ef`, r755): not a defect, and now guarded. Filed 2026-10-19 (r754) at Aria's request, from item 146's frames. Nobody's call — a defect.**

Depends on: nothing

[Item 146](146-the-bridge-ramp-is-a-solid-wedge.md)'s session found, and its frames show (`botropolis/docs/screenshots/r750-item-146-ramp-h0.png` and `-h270.png`, and item 132's `r707-item-132-bridge-h0.png`), that a train piece standing just beyond the deck's footprint, on the far side from the camera, draws over the deck's far railing. Under the deck the order is right; just past it, the depth sort puts the wagon in front.

## The fix

Sort a raised drawable against a ground one by the raised one's footprint and height, so anything behind the deck in depth draws before it whatever its screen position; the deck and its railings draw after a wagon behind them and before one in front.

Tests: at four headings, a wagon on the cell just behind the deck should draw before the deck and its railings, a wagon in front after them, and item 132's under-the-span order still holds. Frames for Aria at 0 and 270.

## Closed (2026-10-19)

The order was already right, so nothing in the sort changed.
Zoomed crops of all three frames show the deck's far railing and its edge strip painted over the wagon, not under it.
The wagon stands behind the deck and below its underside, so its body shows above the far edge, which reads as the wagon being on top.
A staging hook that was not committed put a three-piece train on the rail at the first span in the synthetic fixture and logged the frame's draw order: at headings 0 and 270, zoom 2 and 3, with the wagon 0.4 to 1.2 cells off the deck, every piece drew before the span, with no cycle in the sort.
The roadmap manager read the crops and agreed (2026-10-19): the misreading was the manager's and the filing session's.

`819f9ef` (r755) guards it in `TestBridgeDrawOrder`.
At each of the four headings, gathered either way, a wagon on the rail a cell behind the first span draws before every bridge part it is wholly behind, and one a cell in front draws after every part it is wholly in front of; item 132's under-the-span cases are unchanged.
It was green from its first run, so it was mutated red twice: dropping the overlap check from the level rule failed all 16 in-front cases, and dropping it while drawing the ground thing after the raised one — the defect as reported — failed all 16 behind cases.

No changelog entry: nothing a user sees changed.
For Aria, only if it bothers her: a train behind the bridge showing above its far edge is a matter of design, the deck's height or look, and is not filed.
