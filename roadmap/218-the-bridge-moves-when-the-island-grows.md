# 218. The bridge moves a row every time the island grows a row

**Open, in progress since 2026-10-24 in the session "item 218". Filed 2026-10-24 (r966) at Aria's request, from item 217. Nobody's call — Aria decided: anchor it.**

Aria, 2026-10-24, on whether the bridge should move as the island grows: *"It should stay where it is."*

[Item 217](217-a-delivery-truck-drives-beside-the-bridge-not-on-it.md) found that `City.bridgeCell` (`botropolis/pkg/city/pullrequests.go`) places the bridge on the middlemost coastal street row every time the plan is made, so each row the island gains moves the whole bridge over by one. Item 217 re-routes trucks already in flight; this item stops the bridge moving at all.

## The fix

Place the bridge once and keep it: the scene remembers the bridge's row, and a new plan keeps it while that row is still a coastal street. Only when it is not does the bridge move, to the nearest coastal street row to where it was, not the middle. The memory lives with the scene (as the plan's other remembered parts do), so a restart may place it afresh; say in the item whether it should survive a restart (the layout file) and why.

Tests: the island growing by rows on the bridge's side and the opposite side keeps the bridge on its row; the bridge's row stopping being a street moves it to the nearest street row; a frame of the timelapse with the bridge staying put while the island grows.
