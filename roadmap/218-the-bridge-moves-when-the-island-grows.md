# 218. The bridge moves a row every time the island grows a row

**Fixed 2026-10-24 (`1b5cc23`, r974). Filed 2026-10-24 (r966) at Aria's request, from item 217. Nobody's call — Aria decided: anchor it.**

Depends on: nothing
Landed: slice 1 (`1b5cc23`, r974).

Aria, 2026-10-24, on whether the bridge should move as the island grows: *"It should stay where it is."*

[Item 217](217-a-delivery-truck-drives-beside-the-bridge-not-on-it.md) found that `City.bridgeCell` (`botropolis/pkg/city/pullrequests.go`) places the bridge on the middlemost coastal street row every time the plan is made, so each row the island gains moves the whole bridge over by one. Item 217 re-routes trucks already in flight; this item stops the bridge moving at all.

## The fix

Place the bridge once and keep it: the scene remembers the bridge's row, and a new plan keeps it while that row is still a coastal street. Only when it is not does the bridge move, to the nearest coastal street row to where it was, not the middle. The memory lives with the scene (as the plan's other remembered parts do), so a restart may place it afresh; say in the item whether it should survive a restart (the layout file) and why.

Tests: the island growing by rows on the bridge's side and the opposite side keeps the bridge on its row; the bridge's row stopping being a street moves it to the nearest street row; a frame of the timelapse with the bridge staying put while the island grows.

## Answered while building

- **What "stay where it is" means** (manager, 2026-10-24): relative to the island, not to a world row, since the plan is laid from its north-west corner and growth north of the bridge shifts every row below it. A row mark in `pkg/plan` ({band, offset}: the slot row or road the row falls in, and how far into it) keeps the same stretch of road beside the same districts.
- **Whether it survives a restart** (manager, 2026-10-24): yes, in `layout.json` as an omitempty `"bridge"` mark, with no version bump. Aria asked for it to stay where it is; the layout's contract is that the map you have learned does not move under you; and the plan's other remembered parts, district slots and driveways, already live in the layout (item 108), not only in the scene as this item's text assumed. `docs/compatibility.md` keeps `layout.json` readable forward, so a layout without the mark places the bridge by the middle rule.
- **The test tree** (manager, 2026-10-24): approved as sent, `TestRowMark` in `pkg/plan/plan_test.go` and `TestBridge` in `pkg/city/pullrequests_test.go`, with one addition: a layout from before the mark loads and places the bridge by the middle rule.

## Closed

Fixed by slice 1 (`1b5cc23`, r974), with its changelog entry under `[Unreleased]`.
The layout keeps the bridge's row as a `plan.RowMark`, and `City.placeBridge` lands it on that row while the row is a coastal street, and otherwise on the coastal street row nearest it.
The bridge always lands on the ring road on its coast, which is a street on every row, so in practice it moves only when the island shrinks past it.
The roads remembered for a plan are now also keyed on the landing, because the T where a road meets the bridge no longer follows from the plan alone.
Tests: `TestRowMark` in `pkg/plan/plan_test.go`, and `TestBridgeStays` in `pkg/city/pullrequests_test.go`, a function of its own beside `TestBridge` rather than inside it. Each `TestBridgeStays` case first checks that the middle rule would have put the bridge elsewhere, so it cannot pass on a fixture where both rules agree.
Item 217's tests still pass unchanged: its fixture grows the island north of the bridge, so the bridge still moves in world rows with the road under it, and the re-route still runs.
The first `make land` failed only on `TestTheStillCityMatchesTheCityDrawnDirectly` with "gamepad: Open failed: interrupted system call", which is item 230; the second passed unchanged.

**Frames for Aria**, filmed fresh from r974 and kept git-ignored at `botropolis/dist/item-218/`: `bridge-before-and-after-growth.png` (the bridge corner at 24, 26, 32 and 38 s, holding its place while the island grows a row between 26 and 32 s), and `bridge-in-0.3.0-for-comparison.png` (the same crops from the 0.3.0 clip, where it jumps a row at 32 s).
Closed pending her judgement of them, as item 217 was.

**Aria's verdict** (2026-10-24): the frames are approved.
