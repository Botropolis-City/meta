# 335. The frame's batcher is greedy, so the draw-command count depends on which source happens to lead

**Open. Filed 2026-11-03 (r1234), from item 212's slice 29. Nobody's call — a defect in the batcher's order, after 0.4.0.**

`batchBy` (item 193) batches a frame's draws greedily: when the current source has no free draw, it starts the source of the earliest free draw.
So the command count depends on which source leads: with the aged lots' fills in a frame's record they led, and the standing city's other fills merged into their batch; with the lots painted into the ground layer (item 212, slice 29) nothing starts the fill source early, the other fills go down after a page of sprites, one sprite quad overlaps a fill and must follow it, and that sprite batch splits in two — one command more a frame, identical pixels (34 → 35 on a staged metropolis, 38 → 39 in `TestTheWorkAFrameTakes` against its ceiling of 38).
Two greedier rules tried (start the source with the most free draws, always or only when switching) read 40–43, worse everywhere.

## The fix

A batcher that looks ahead: the fewest batches under the overlap order, or a bounded look-ahead that avoids a split when a source can be started earlier without breaking an overlap; measured on the metropolis by day and night, the record city and the 600-district city, and held by the draw ceilings with the per-source breakdown slice 29 adds to the frame log.
