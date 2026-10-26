# 283. Districts can be moved only one at a time

**Open, in progress since 2026-10-26 in the session "item 283". Filed 2026-10-26 (r1120), from Aria's use of 0.3.2. Nobody's call — Aria asked for it.**

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
