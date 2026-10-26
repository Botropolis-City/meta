# 264. The city behind a notice or any covering panel can still be hovered through it

**Fixed 2026-10-26 (`2acfd65`, r1097). Filed 2026-10-26 (r1093), from item 190's frames, at Aria's request. Nobody's call — a defect.**

Aria passed item 190's two notices on 2026-10-26 and asked for this to be filed on its own.

**The filing misread the frame** (item 264's session, 2026-10-26, measured at r1093): the plate in item 190's frame is a first-sighting caption, not a hover label (`pkg/render/explain.go`, `queueSightings`), and it is under the scrim like the chrome, its text at 94/255 behind the notice against 230 without it; being the panel colour, it reads as one more panel. The defect underneath is real, though: hover still resolves while a modal is open, because `notePointer` (`game.go`) runs before anything checks for one, so a pointer resting on the notice over the power plant brings up the plant's hover card behind the dim. The item now fixes that, as its second option said: while anything with a full scrim covers the city, the pointer is reported away. A first sighting spent behind a modal is item 268.

In item 190's frame of the damaged-store notice (`r1081-item-190-notice-damaged.png`), the city behind the notice is dimmed, but the hover label `train · one model's spend today`, at about (920, 390)–(1104, 408) in the 1600×1000 frame, is drawn above the dim at full brightness, beside the notice.
A notice is modal: everything behind it should read as behind it, and a label that stays bright suggests the city under it can still be hovered.

## Where

The hover label is drawn through `drawLabel` in `pkg/render/labelcache.go` from the kind's legend (`pkg/city/kinds.go`, `KindTrain`).
The modal overlays draw their own dim (`pkg/render/board.go` and `pkg/render/closeup.go` with the panel colour at alpha 0x60, `pkg/render/breakdown.go` with `colorScrim`), and the label is drawn after it.
The fix is either to draw hover labels before any modal's dim, or to stop resolving hover while a modal is open; the second also stops the label from following the mouse behind the notice.
Check the other modals (the board, the close-up, the breakdown and the quit prompt) for the same order, and pin it in one test, data-driven over them: with a modal open, no hover label is drawn.

## Closed

Fixed in one slice (`2acfd65`, r1097), landed through `make land`.
While anything with a full scrim covers the city, `notePointer` (`pkg/render/game.go`) reports the pointer away and skips sprite hover.
That covers any modal overlay, and the settings, the breakdown with its ranges, the timeline and the view key, which each draw a scrim outside the overlay stack.
The quit prompt is a footer line with no dim, so it is left out, as agreed.

`TestCoveredCityTakesNoHover` (`pkg/render/modalhover_test.go`) is data-driven over those ten covers, with an uncovered control and a closed-again case.
It was red on all ten before the fix.
The changelog has the entry under Fixed.

Frames for Aria to judge, the damaged-store notice with the pointer resting on it over the power plant: `botropolis/docs/screenshots/r1093-item-264-notice-hover-before.png` shows the plant's card behind the dim, and `botropolis/docs/screenshots/r1094-item-264-notice-hover-after.png` shows none.
The after frame was filmed from the fix before it landed, so its filename says r1094 where the fix landed at r1097, after other items landed first.
