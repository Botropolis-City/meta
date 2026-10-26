# 264. A hover label draws over a notice's dimmed city, at full brightness

**Open. Filed 2026-10-26 (r1093), from item 190's frames, at Aria's request. Nobody's call — a defect.**

Aria passed item 190's two notices on 2026-10-26 and asked for this to be filed on its own.

In item 190's frame of the damaged-store notice (`r1081-item-190-notice-damaged.png`), the city behind the notice is dimmed, but the hover label `train · one model's spend today`, at about (920, 390)–(1104, 408) in the 1600×1000 frame, is drawn above the dim at full brightness, beside the notice.
A notice is modal: everything behind it should read as behind it, and a label that stays bright suggests the city under it can still be hovered.

## Where

The hover label is drawn through `drawLabel` in `pkg/render/labelcache.go` from the kind's legend (`pkg/city/kinds.go`, `KindTrain`).
The modal overlays draw their own dim (`pkg/render/board.go` and `pkg/render/closeup.go` with the panel colour at alpha 0x60, `pkg/render/breakdown.go` with `colorScrim`), and the label is drawn after it.
The fix is either to draw hover labels before any modal's dim, or to stop resolving hover while a modal is open; the second also stops the label from following the mouse behind the notice.
Check the other modals (the board, the close-up, the breakdown and the quit prompt) for the same order, and pin it in one test, data-driven over them: with a modal open, no hover label is drawn.
