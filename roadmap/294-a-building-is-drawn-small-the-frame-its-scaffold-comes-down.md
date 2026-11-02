# 294. A building is drawn small for one frame as its scaffold finishes coming down

**Fixed 2026-11-02 (`71f7fab`, r1211). Filed 2026-10-26 (r1130), from item 212's session. Nobody's call — a defect.**

Found by item 212's whole-frame walk, and there before its work: on the frame a scaffold finishes coming down, one building is drawn smaller (26×48 px) than on the next frame, or than a frame drawn afresh at the same tick (50×66 px).
Nothing is held from an earlier frame on that frame, so it is not item 212's reuse.

## Likely cause

`city.Scene.Scaffold` deletes a finished strike lazily, partway through the frame, after the frame has already worked out which sessions are stirring; so that frame mixes a building with a scaffold and one without.

## The fix

Settle every timed state at one point, before a frame reads any of them, so a frame sees the scene at one instant: prune finished strikes, and any other state pruned on read, at the tick, not inside a draw.
Tests: on the frame a scaffold finishes, the building is drawn at its full size, the same as a frame drawn afresh at that tick; item 212's Drive case can then compare the finishing frame itself, not the one two ticks later.

## Closed

The stale strike was real and is fixed (`71f7fab`, r1211; a test case adjusted in `f40873b`, r1212).
`Scene.Expire` lets go of every timed state that has run out — strikes, loads, settling, celebrations, pours, voyages, hauls — on the scene's tick and as a frame begins,
and the accessors only read, so no read of a frame changes what the rest of it, or the next frame, reads.
`TestStirring` holds each state to that: let go of once the scene ticks, and as stirring after two reads as before them.
Item 212's Drive case now holds that the frame a scaffold finishes does not count its building as stirring.

**The building was never drawn small, which differs from what this item says — flagged for Aria.**
The 26×48 was the record box of a look drawn straight on the first frame its key is new,
and the 50×66 was the same look baked with its padding on the next sighting, which a fresh redraw at the same tick is.
On pixels, rendered under Xvfb, the building's crop on the finishing frame differs from the next frame's in 23 pixels, by up to 7 levels, and all of them are the pulsing disc at its door.
The frames after that differ from each other the same way (25 and 26 pixels, by up to 9).
On main without the fix, the crops are byte-identical to these.
So the Drive case compares the frame after the finish with one drawn afresh, one tick later instead of two, since the finishing frame is the new look's first sighting.
