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
