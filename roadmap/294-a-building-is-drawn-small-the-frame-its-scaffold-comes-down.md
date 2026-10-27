# 294. A building is drawn small for one frame as its scaffold finishes coming down

**Open. Filed 2026-10-26 (r1130), from item 212's session. Nobody's call — a defect.**

Found by item 212's whole-frame walk, and there before its work: on the frame a scaffold finishes coming down, one building is drawn smaller (26×48 px) than on the next frame, or than a frame drawn afresh at the same tick (50×66 px).
Nothing is held from an earlier frame on that frame, so it is not item 212's reuse.

## Likely cause

`city.Scene.Scaffold` deletes a finished strike lazily, partway through the frame, after the frame has already worked out which sessions are stirring; so that frame mixes a building with a scaffold and one without.

## The fix

Settle every timed state at one point, before a frame reads any of them, so a frame sees the scene at one instant: prune finished strikes, and any other state pruned on read, at the tick, not inside a draw.
Tests: on the frame a scaffold finishes, the building is drawn at its full size, the same as a frame drawn afresh at that tick; item 212's Drive case can then compare the finishing frame itself, not the one two ticks later.
