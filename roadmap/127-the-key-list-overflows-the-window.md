# 127. The key list runs off the window and cannot be scrolled

**Open. Filed 2026-10-18 (r648), from what item 122 found. Nobody's call — a defect.**

The help's key list — opened from the Reference index (`?` or F1) by its "keys" term, and laid out by `LayoutHelp` in `botropolis/pkg/ui` — has grown to about 40 rows, and in a 1600 by 1000 window it is clipped at both the top and the bottom with no way to scroll, so some keys cannot be read at all.
Item 122 found it while placing a credit line under the list's last row, which would have been off-screen for most people; the credit went to the Reference index instead.

## The fix

The list fits or scrolls: group the rows into columns where the window is wide enough, and where it is not, scroll the panel with the wheel and the arrow keys, as the stream panel does (item 100), with a mark saying more is above or below.

Tests: data-driven over window sizes from 700 by 600 up, every row is either on screen or reachable by scrolling, and none is ever clipped half-drawn; a frame at 1600 by 1000 for Aria.
