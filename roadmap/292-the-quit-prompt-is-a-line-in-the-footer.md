# 292. The quit prompt is a line in the footer, not a prompt in the middle of the screen

**Done 2026-10-26 (`f431298`, r1150). Filed 2026-10-26 (r1124), from Aria's use of 0.3.2. Nobody's call — Aria said what she wants.**

Aria, 2026-10-26: *"we should make the quit prompt in the middle of the screen not in the bottom screen text."*

Pressing `q` sets the footer's notice to the quit prompt (`quitPrompt`, `pkg/render/keys.go`), with *close up* drawn beside the last footer line (`quitButton`, `pkg/render/closeup.go`); `y` or Enter confirms, and item 270 made it wait for the answer however busy the city is.

## The fix

The quit prompt becomes a small centered panel on the overlay stack, over the dimmed map like the other modal panels (item 264's scrim): *Quit Botropolis?* with three buttons, **Quit** (`y`, Enter), **Close up…** (`c`) and **Cancel** (`n`, Esc), each clickable.
Item 270's rule holds: it stays until answered.
It is the same panel item 293 shows when the window is closed.
Tests: `q` opens it centered; each key and button does its one thing; the map behind takes no hover or click (item 264); and it does not expire while the loop is slow.
A frame for Aria.

## Answered while building

- **The clock** (manager, 2026-10-26): none. Item 270's ten seconds and hundred updates existed only to keep a slow loop from expiring the footer line, so they went with it; the panel stays until it is answered.
- **Other keys** (manager, 2026-10-26): it is modal, so they do nothing, except `q`, which cancels: two presses of `q` never quit.
- **The finder** (manager, 2026-10-26): Ctrl+K stands the panel down rather than stacking over it, as it did the line.

## Closed

Landed in `f431298` (r1150), with `051754b` (r1151) removing the footer button's leftover label.
`q` opens `quitPanel` (`pkg/render/quit.go`), centred over the scrim: *Quit Botropolis?* with **Quit** (`y`, Enter), **Close up…** (`c`) and **Cancel** (`n`, Esc, `q`), each button pressing its key so a click and the keyboard run one path.
The footer line, its close-up button and `confirm` are gone.
`g.openQuit()` is the one call item 293 needs: it always leaves exactly one quit panel on top, whatever else is open.
`TestQuitPanel` covers each key and button, the centring, the modal keys, a minute and a thousand updates without expiring, and the single panel; `TestCoveredCityTakesNoHover` gains the quit panel.
Item 291's test that closing up from the quit prompt quits was rewritten against the panel's Close up… button, which with nothing live records and quits at once.
The plate is opaque, not the theme's translucent panel colour, because district labels showed through it.

Frame for Aria: `botropolis/docs/screenshots/r1125-item-292-quit-panel.png`, the metropolis demo at 1280×800 with `q` pressed.
