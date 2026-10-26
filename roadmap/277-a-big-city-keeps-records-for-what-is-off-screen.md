# 277. A big city keeps drawing records for what is off screen

**Open. Filed 2026-10-26 (r1118), from item 212's design, at Aria's ruling. Nobody's call — parked until item 270's city shows it is needed.**

Item 212 keeps each still thing's drawing record between frames, so a settled frame does not record it again.
It keeps them for everything drawn, on screen or not, so a big city zoomed in holds records for most of the map it cannot see.

Aria, 2026-10-26, asked whether to keep records only for what is on or near the screen: *"File it separately"*, as item 212 recommended, because it saves nothing at the fitted view, where everything is on screen, and the item's other work comes first.

## When to start it

Only if item 270's stress city (900 districts, 2,400 sessions) is still over the settled memory budget once item 212 gives its buffers' spare room back; until then it is parked.

## The fix, when it starts

Keep records only for what stands on screen or within a margin of it; let the rest go, and record a thing afresh when it comes back into view.
Tests: a pan away and back holds the frame to the one recorded afresh; the records kept are counted against what is on screen; and panning at the margin causes no frame over the frame budget.
