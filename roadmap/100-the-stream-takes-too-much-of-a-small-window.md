# 100. The stream takes too much of a small window

**Open, in progress since 2026-10-16 in the session "item 100". Filed 2026-10-16 (r512) at Aria's request, from a frame of item 86's. Nobody's call — the cap is chosen.**

Item 88 added the stream, a column down the right with the event log's live tail, shown by default.
Its width is a fixed number of grid units (`StreamGrids` in `botropolis/pkg/ui/stream.go`, used by `StreamArea`), so it takes the same pixels at every window size, and in a window about 960 pixels wide it covers about 40% of the screen (`docs/screenshots/r511-item-86-depot.png`).

Aria chose, on 2026-10-16: cap it as a share of the window — at most about a quarter, wrapping its entries to fit — and below a minimum width it hides itself, while its key still shows it.
The map's reserved inset follows the column's actual width, so a fit still keeps the city beside it.

Tests, data-driven over window widths: the column is never wider than its share; below the minimum it is hidden by default and its key shows it; an entry longer than the column wraps rather than clips.

## Answered while building

- **The numbers** (manager, 2026-10-16): at most a quarter of the window and never wider than today's 40 grids, so wide windows are unchanged; below 24 grids it hides itself. Aria judges them in the frames.
- **Shown by its key in a narrow window** (manager, 2026-10-16): at the minimum width, clamped to the window, since narrower cannot be read.
- **That show is for the run only** (manager, 2026-10-16): it never sets the remembered hide, which only the key in a window wide enough changes; the column hiding itself is not the person hiding it.
- **The test tree** (manager, 2026-10-16): approved as proposed, data-driven over window widths, with frames at about 700 (key pressed), 960 and 1600.
