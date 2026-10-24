# 239. The bridge fades into the sea with no fog to explain it

**Done 2026-10-24 (`02d0bd4`, r1007). Filed 2026-10-24 (r1005) at Aria's request, on item 219's frames. Nobody's call — Aria chose the look: a still bank with a thin mist along the coast.**

Depends on: nothing
Landed: slice 1 (`02d0bd4`, r1007).
Landed: slice 2 (`bafd62d`, r1009).

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

## Closed (2026-10-24)

Slice 1 (`02d0bd4`, r1007) built it.
`City.Fog()` places the fog from the plan alone: a bank of soft puffs from just short of `Haze` to a cell and a half past `Far`, rising to the deck's height and thickening toward `Far`, and a thin low mist strung along the bridge's whole coast, every puff over open sea.
`pkg/render` draws it as one item in the depth sort, a level above the trucks on the deck, from one 64×64 puff texture built in code (16 KiB), white-grey by day and dim blue-grey by night, and notes no hover target.
It stands still, so it is composed into the standing city: `TestTheWorkAFrameTakes` settles at 24 draw commands by day and 41 by night, its ceilings unchanged.
`TestFogOverTheHaze` (`pkg/city`) and `TestFogInTheDrawing` (`pkg/render`, at all four headings) hold it.
These were mutated red: the mist moved over the river's mouth and over the depot, the fog put on the ground level, a hover target noted by the fog, the bank lifted off the deck, and flat alpha, which first passed "thickens toward the far end" and made that test compare mean alpha instead of a sum.
The changelog says it under `[Unreleased]`.

Slice 2 (`bafd62d`, r1009) is the frames, filmed through `make demo-media-locked` from the demo corpus with a pull request merging so a truck drives off into the fog: `botropolis/docs/screenshots/r1007-item-239-fit-day.png`, `-fit-night`, `-zoomed-day` and `-zoomed-night` at heading 270, and `-zoomed-180-day`.

**Aria's verdict** (2026-10-24, through the manager): *"Approve as is"*, the faint night mist included.
