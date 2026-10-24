# 239. The bridge fades into the sea with no fog to explain it

**Open, in progress since 2026-10-24 in the session "item 239". Filed 2026-10-24 (r1005) at Aria's request, on item 219's frames. Nobody's call — Aria judges the look from frames before it lands.**

Depends on: nothing

Aria, 2026-10-24, approving [item 219](219-the-bridge-ends-in-open-water.md)'s frames: *"maybe we should add some visible fog/clouds to make it make sense that it fades"*.
Item 219 runs the bridge deck three cells past its old end and fades it toward the sea's colour; there is no haze drawn, so the deck, and the trucks on it, melt into clear water for no reason the eye can see.

## The fix

Draw a fog or low cloud bank over the open sea where the deck fades (`Bridge.Haze` to `Bridge.Far`, `pkg/city`), so the deck and trucks vanish into something: by day and by night, at every zoom, in every heading.
- Art comes from three places only (`botropolis/design/art-sources.md`): this is geometry or noise built by hand in code, never a generated picture.
- It must not hide anything that carries meaning (boats keep to the river, which item 219 confirmed lies clear of the haze), nor read as an object you can hover.
- It costs draw commands and GPU memory: hold `TestTheWorkAFrameTakes`'s ceilings (no raise without the manager), and the city's memory budgets.
- Whether the fog stands still, drifts, or reaches along the whole coast is a look for Aria: propose one or two with frames before building tests.

Tests: the fog covers the deck's fading span at every heading; nothing hoverable is under it; the frame's draw count and memory stay within their budgets; frames by day and night, at fit and zoomed in, for Aria.

## Answered while building

- **The look** (Aria, 2026-10-24, choosing between two looks from frames): B, the fog bank over the deck's fading span plus a thin low mist along that whole coast, so it reads as weather; and still, not drifting, so it stays part of the standing city and costs no draw command on a settled frame. Built in code as soft puffs of one 64×64 Gaussian texture, white-grey by day and dim blue-grey by night, never hoverable.
- **What may be under it** (manager, 2026-10-24): nothing hoverable except a delivery truck on the bridge, which item 219 keeps hoverable until it is removed at the far end.
- **The test tree** (manager, 2026-10-24): approved as sent. `TestFogOverTheHaze` in `pkg/city/fog_test.go` (the fog is part of the model, `City.Fog()`, from the plan alone: it covers the fading span, thickens toward `Far`, ends within a cell and a half past it, lays the mist along the bridge's whole coast, keeps every puff over open sea, is the same for the same plan, and is absent without a bridge) and `TestFogInTheDrawing` in `pkg/render/fog_test.go` at every heading (drawn after the haze pieces and the trucks in the haze, covering each haze piece, noting no hover target, no hover target under it but a delivery truck on the bridge, clear of the river's mouth, the boats' run and the depot, its texture at most 16 KiB). `TestTheWorkAFrameTakes` holds at 24 and 41. Frames for Aria follow as their own slice.
