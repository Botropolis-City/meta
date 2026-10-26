# 264. The city behind a notice or any covering panel can still be hovered through it

**Open, in progress since 2026-10-26 in the session "item 264". Filed 2026-10-26 (r1093), from item 190's frames, at Aria's request. Nobody's call — a defect.**

Aria passed item 190's two notices on 2026-10-26 and asked for this to be filed on its own.

**The filing misread the frame** (item 264's session, 2026-10-26, measured at r1093): the plate in item 190's frame is a first-sighting caption, not a hover label (`pkg/render/explain.go`, `queueSightings`), and it is under the scrim like the chrome, its text at 94/255 behind the notice against 230 without it; being the panel colour, it reads as one more panel. The defect underneath is real, though: hover still resolves while a modal is open, because `notePointer` (`game.go`) runs before anything checks for one, so a pointer resting on the notice over the power plant brings up the plant's hover card behind the dim. The item now fixes that, as its second option said: while anything with a full scrim covers the city, the pointer is reported away. A first sighting spent behind a modal is item 268.

In item 190's frame of the damaged-store notice (`r1081-item-190-notice-damaged.png`), the city behind the notice is dimmed, but the hover label `train · one model's spend today`, at about (920, 390)–(1104, 408) in the 1600×1000 frame, is drawn above the dim at full brightness, beside the notice.
A notice is modal: everything behind it should read as behind it, and a label that stays bright suggests the city under it can still be hovered.

## Where

The hover label is drawn through `drawLabel` in `pkg/render/labelcache.go` from the kind's legend (`pkg/city/kinds.go`, `KindTrain`).
The modal overlays draw their own dim (`pkg/render/board.go` and `pkg/render/closeup.go` with the panel colour at alpha 0x60, `pkg/render/breakdown.go` with `colorScrim`), and the label is drawn after it.
The fix is either to draw hover labels before any modal's dim, or to stop resolving hover while a modal is open; the second also stops the label from following the mouse behind the notice.
Check the other modals (the board, the close-up, the breakdown and the quit prompt) for the same order, and pin it in one test, data-driven over them: with a modal open, no hover label is drawn.
