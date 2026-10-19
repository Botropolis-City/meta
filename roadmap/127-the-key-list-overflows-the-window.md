# 127. The key list runs off the window and cannot be scrolled

**Fixed 2026-10-18 (`e82f32a`, r670). Filed 2026-10-18 (r648), from what item 122 found. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`a94e823`, r665).
Landed: slice 2 (`e82f32a`, r670).

The help's key list — opened from the Reference index (`?` or F1) by its "keys" term, and laid out by `LayoutHelp` in `botropolis/pkg/ui` — has grown to about 40 rows, and in a 1600 by 1000 window it is clipped at both the top and the bottom with no way to scroll, so some keys cannot be read at all.
Item 122 found it while placing a credit line under the list's last row, which would have been off-screen for most people; the credit went to the Reference index instead.

## The fix

The list fits or scrolls: group the rows into columns where the window is wide enough, and where it is not, scroll the panel with the wheel and the arrow keys, as the stream panel does (item 100), with a mark saying more is above or below.

Tests: data-driven over window sizes from 700 by 600 up, every row is either on screen or reachable by scrolling, and none is ever clipped half-drawn; a frame at 1600 by 1000 for Aria.

## Answered while building

- **The layout** (manager, 2026-10-18): the key list takes the fewest columns that fit the window, read down each column and then across in the bindings' order, wrapping long labels rather than clipping them; when no column count fits, it falls back to one column that scrolls by whole rows, with "N more above" and "N more below", by wheel and arrow keys, and the wheel no longer zooms the map behind it. Frames at 1600×1000 and at 700×600 scrolled.

## Closed

Slice 1 (`a94e823`, r665) made the list fit or scroll.
`LayoutHelp` takes the fewest columns that fit, each column's labels just past its own chips, and wraps long actions.
Where nothing fits, it is one scrolling column of whole rows with "N more above" and "N more below", moved by the wheel and the up and down arrows.
It is laid out between the strip and the footer, and the reference takes the wheel, so the map behind it no longer zooms.
Aria passed the r665 frames (`botropolis/docs/screenshots/r665-item-127-key-list-columns.png`, `…-scrolled.png`) with two fixes, which are slice 2 (`e82f32a`, r670).
`LayoutHelpIn` works round the stream and the minimap as the City Plan does, and a chip much wider than the rest wraps at word boundaries.
Frame, passed by Aria (2026-10-18, "Pass, close it."): `botropolis/docs/screenshots/r670-item-127-key-list-clear-of-stream.png`.

Tests: `pkg/ui/help_test.go` sweeps seven window sizes at two scales.
It checks every row and line inside the panel, no overlaps, no mark over a row, and every key reachable at some scroll, plus the covers and the chip wrapping.
`testing/acceptance/keylist_test.go` drives the wheel and arrows and checks the list clear of the strip, the footer and the stream.

**Deviation, passed by Aria with the r670 frame (2026-10-18):** the chip cap is half again the 95th percentile of key widths, not the 90th that was agreed, because at the 90th "/ or ctrl+k" wrapped too.
With the real font, "wheel out past Skyline" wraps onto three lines.
The reference panel is slightly translucent, so a selected card can still show faintly through it; that is existing styling and was left alone.
