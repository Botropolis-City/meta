# 261. Past four seconds, the metropolis draws over its draw-count ceilings

**Open. Filed 2026-10-26 (r1085), found by item 260's session. Nobody's call — the ceilings are set (20 by day, 37 by night; wobble 1 and 2).**

Depends on: 260

`TestTheWorkAFrameTakes` judges the metropolis's settled frames over a fixed span, ticks 18–121 (104 frames, about the first 4 s after it settles); [item 260](260-the-draw-count-wobble-test-fails-under-load.md) pinned that span so load cannot move it.
Measured past it, with no first-sighting caption up, the same scene draws over its limits as its vehicles move on:

| record | by day | by night |
| --- | --- | --- |
| ticks 18–121 (the span judged) | 20–20 | 35–37 |
| 5 s (134 settled frames) | 20–21 (a car makes 21 at 4.8 s) | 35–38 |
| 8 s | 19–21 | 34–38 |

So the ceilings and wobble limits that [item 236](236-where-a-vehicle-stands-changes-a-frames-draw-count.md) set hold for the first four seconds of this demo and no longer: where a vehicle stands still changes a frame's draw count, past the span the test counts.

## The fix

Find what the frames over the ceiling draw that the others batch (item 260's off-count logging names them), and bring the metropolis within 20 by day and 37 by night, with a spread of at most 1 and 2, over a long settled record (16 s, both lights); then widen `TestTheWorkAFrameTakes`'s judged span to that record. The limits stay as they are: they are the goal.

Tests: the widened span passing at both lights many times in a row, and a vehicle drawn on its own batch still failing it.
