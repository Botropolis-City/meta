# 292. The quit prompt is a line in the footer, not a prompt in the middle of the screen

**Open. Filed 2026-10-26 (r1124), from Aria's use of 0.3.2. Nobody's call — Aria said what she wants.**

Aria, 2026-10-26: *"we should make the quit prompt in the middle of the screen not in the bottom screen text."*

Pressing `q` sets the footer's notice to the quit prompt (`quitPrompt`, `pkg/render/keys.go`), with *close up* drawn beside the last footer line (`quitButton`, `pkg/render/closeup.go`); `y` or Enter confirms, and item 270 made it wait for the answer however busy the city is.

## The fix

The quit prompt becomes a small centered panel on the overlay stack, over the dimmed map like the other modal panels (item 264's scrim): *Quit Botropolis?* with three buttons, **Quit** (`y`, Enter), **Close up…** (`c`) and **Cancel** (`n`, Esc), each clickable.
Item 270's rule holds: it stays until answered.
It is the same panel item 293 shows when the window is closed.
Tests: `q` opens it centered; each key and button does its one thing; the map behind takes no hover or click (item 264); and it does not expire while the loop is slow.
A frame for Aria.
