# 185. The landmarks stay dark at night

**Done 2026-10-20 (`565aa78`, r842). Filed 2026-10-20 (r787) at Aria's request, from item 166's frames.**

Depends on: 166
Landed: slice 1 (`5a920bd`, r835).
Landed: slice 2 (`f599a23`, r838).
Landed: slice 3 (`6aa638b`, r841).
Landed: slice 4 (`565aa78`, r842).

[Item 166](166-lit-windows-are-round-halos-not-windows.md) lights a session's building at night by redrawing its own window panes at day brightness (option A). The landmarks — the library, City Hall and the power plant — are not sessions, so they stay dark (`botropolis/docs/screenshots/r788-item-166-district-at-night.png`).
Aria, 2026-10-20, approving item 166: *"Approve, and light the landmarks too."*

## The fix

Light each landmark's windows at night the same way, from its own measured panes (item 166's pipeline already measures them, and item 99 lettered their walls), with the same occlusion layer. Decide per landmark what "lit" means: the library and City Hall lit through the evening, the power plant lit while any session is working (it already glows with spend).

Tests: each landmark lights exactly its panes at night and none by day; nothing in front of a landmark is painted over (item 166's occlusion test, with a landmark behind); its lettering (item 99) stays readable. A night frame for Aria with the plaza in view.

## Decided along the way

Answered by the roadmap manager for Aria, 2026-10-20:

- The library and City Hall are lit all night, dusk to dawn on the scene's clock, and whenever night is forced; "through the evening" above was a gloss on her ask.
- The plant is lit while any session is working, fading on and off over about a second like a building's lights.

Aria, 2026-10-20, on the first plaza frames (`botropolis/docs/screenshots/r838-item-185-plaza-at-night.png` and `r838-item-185-plaza-nobody-working.png`):
*"Tint them a little yellow at night only. And I do still see one glow circle that we didn't remove."*
So at night a landmark's lit panes are drained of colour and warmed a little, softer than the session buildings' yellow,
and by day nothing is laid over them.
Slice 3 first mixed the blue 30% toward the city's warm glass, which passes through grey and read pale grey-white.
Slice 4 replaced it after a mock-up of four tints,
and the check now also requires the lit glass to be redder than blue.
And the power plant's round glow is gone.
Its spend stays visible on the strip's "$… 24h" chip and in the Cost lens, so nothing it said at a glance is lost.

## Done

**At night the landmarks light their own windows** (`f599a23`, r838; tint and glow `6aa638b`, r841, and `565aa78`, r842).
Each landmark's panes are its own sprite's pixels, drawn again from the atlas page through item 166's lights layer in one draw, so anything in front cuts them out, and tinted a soft yellow at night only (`botropolis/pkg/render/landmarklights.go`).
The library and City Hall are lit all night.
The plant is lit while any session is working, faded over a second by the scene (`botropolis/pkg/city/plantlights.go`).
The plant's round glow is gone.

**The plant's windows are now measured** (`5a920bd`, r835): the atlas measured panes for the commercial pieces only, so it had none.
`tools/render-sprites/render.py` now measures all three landmarks, and a pane must hold glass bluer than green, which drops six false panes on City Hall's green cross and the library's awning.
The manifests were remeasured from the committed atlas pages with render.py's own functions, because a full `make sprites` took 91 minutes under the day's load and moved a few pixels elsewhere, within `make sprites-check`'s tolerance.

**Tests**, each mutated red: the atlas carries the plant's panes and no green ones (`botropolis/pkg/assets/landmarkpanes_test.go`); the lights' timing, every pane lit from the right heading and page, one draw per landmark, and the map lighting them at night and not by day (`botropolis/pkg/render/landmarklights_test.go`, `botropolis/pkg/city/plantlights_test.go`); no glow on the plant; and `botropolis-demo sheet --check-lights`, which now draws each landmark at every heading and fails on a lit pixel off its panes, windows that light nothing, light on its painted name (item 99), a lit City Hall showing through a dark building in front, or lit glass that is not warmer than by day and redder than blue.

**Frames**: `botropolis/docs/screenshots/r842-item-185-plaza-at-night.png`, with twelve sessions working, and `r842-item-185-plaza-nobody-working.png`, the plant dark.
**For Aria:** these follow her verdict on the r838 frames and have not been judged yet.
The tint is softer than the session buildings' yellow, as "a little yellow" asked; reopen this if it should be stronger or weaker.

**Aria approved the r842 frames** (2026-10-20): the soft warm tint at night and the plant without its glow.
