# 283. Districts can be moved only one at a time

**Done 2026-10-26 (`8c4a440`, r1143). Filed 2026-10-26 (r1120), from Aria's use of 0.3.2. Nobody's call — Aria asked for it.**

Depends on: nothing
Landed: slice 1 (`dd93c5e`, r1124).
Landed: slice 2 (`8c4a440`, r1143).

Aria, 2026-10-26, reporting what she met in 0.3.2 for 0.3.3: *"I should be able to select multiple distrcits together and move them together."*

Today a left press on a district's floor or sign picks that one district up (`pkg/city/drag.go`), and its new place is saved in the layout.

## The fix

1. **Ctrl+click** a district adds it to a selection or takes it out, and **Ctrl+drag** on open ground draws a box that selects every district it touches; the selected districts are outlined.
2. Dragging any selected district moves them all together, keeping their places relative to each other, and the move is refused, as a single move is, where it would overlap; `Esc` clears the selection.
3. The layout saves every moved district at once, so a restart keeps them.
4. Tests: a selection of three moves together and keeps its shape; a move that would overlap is refused for all; the layout holds all three after a reload; a plain click without Ctrl still picks up one district.
5. A frame for Aria with three districts selected, and the help and man page updated.

## Answered while building

- **The design** (session's, approved by the manager, 2026-10-26): Ctrl or Cmd click toggles a district, Ctrl or Cmd drag on open ground boxes; a plain click on open ground or Esc clears; dragging a selected district moves all of them by the same offset and is refused whole, shown in red, when an unselected district holds a target, while a single drag keeps swapping as item 85 made it.

## Done

- **Slice 1** (`dd93c5e`, r1124), in `pkg/city`: `Layout.MoveDistricts` carries a group by one slot offset, and the scene keeps a selection, toggled a district at a time or boxed on the screen.
  Dragging a selected district carries the whole selection; dragging one outside it moves only that one and leaves the selection alone.
  `TestMoveDistricts` and `TestDistrictSelection` cover the three moving together and keeping their shape, the move refused for all, the reload holding all three, and a plain drag picking up one.
- **Slice 2** (`8c4a440`, r1143), in `pkg/render`: Ctrl or Cmd with a click toggles a district, and with a drag on open ground draws the box; a plain click on open ground or `Esc` clears the selection.
  Selected districts are tinted and outlined in the theme accent, and a group being dragged shows a ghost per district over its own target, all in the error colour when refused.
  The left button's press, hold and release moved into `leftButton`, which `TestLeftButton` drives a frame at a time.
  The help, README, `design/city-and-rendering.md` and the changelog say so; the man page has no input section, so it was not touched.
- The frame: `botropolis/docs/screenshots/r1124-item-283-three-selected.png`, the metropolis demo with tidepool, kiln and orchard selected; the manager passed it to Aria.

Decided on the way, by the manager for Aria: a group move swaps with nothing, so a target held by a district outside the selection refuses the whole move, while a single drag still swaps as item 85 made it; Ctrl and Cmd both select.

Also landed in slice 2, from item 282: a left release is measured from the press, not from where the pan last moved it, so a drag that began on a building no longer ends as a click on it.
And a clip's `hold: Control` or `Meta` counts as Ctrl, which is how the frame was filmed.

Flagged for Aria: the test group is b, c and d rather than a, b and c, because in the four-district test city no offset carries a, b and c onto another district without one landing on the plaza.
