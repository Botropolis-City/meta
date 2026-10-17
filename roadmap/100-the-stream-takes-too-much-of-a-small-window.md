# 100. The stream takes too much of a small window

**Fixed 2026-10-17 (`cfd4d08`, r564). Filed 2026-10-16 (r512) at Aria's request, from a frame of item 86's.**

Depends on: nothing
Landed: slice 1 (`5d44000`, r541).
Landed: slice 2 (`2fc1881`, r552).
Landed: slice 3 (`4e42d89`, r561).

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
- **The r541 frames** (Aria, 2026-10-17): the width passed, and the column becomes a corner panel — *"Width is good, but I think we should actually make this more of a corner item than a side item… same height as this item. I'm also wondering what it would look like in the bottom right corner instead of the top right. But I'd like to maybe see both when other menus are open."* So the stream keeps its width rules, takes about the height of the card beside it rather than the window's, and is rendered top-right and bottom-right, with a card, the sidebar and an overlay open, for her to choose.
- **The corner panel's shape** (manager, 2026-10-17): a fixed height, `StreamPanelGrids` = 24, clamped to the room, rather than one that tracks the card and jumps; a new `SetCornerChrome` fits the city both ways around the panel and keeps the larger, never under it and never smaller than with the full-height column; cards keep out of the panel's column in both corners; `StreamCorner` chooses the corner, and in the bottom right the panel stacks above the minimap or the footer. Its tree was approved, with eight frames, two corners by two widths by two sets of open panels.
- **The r552 frames** (Aria, 2026-10-17): *"Of these I like the top right. But I want to see the bottom right actually at the bottom corner of the window right attached to the bottom bar like it is on the top bar. Also… I do like the sizing of it, and we should hava scroll bar to scroll the history and the mouse wheel should work for scrolling when it's hovered."* Top right stays for now; bottom right is redrawn flush on the footer, with the minimap moving above it when drawn, for her to compare again.
- **Scrolling** (manager, 2026-10-17, approved as the session proposed): newest at the top; scrolled to the top it follows new entries, scrolled back it holds still and says "↑ N newer", which jumps back when clicked; it moves a whole entry per wheel notch; a thin bar, drawn only when the entries do not fit, can be dragged; the wheel scrolls the panel only while the pointer is over it and zooms the map elsewhere; the position lasts the run.

## Closed

Aria passed it on 2026-10-17, from the r561 frames: top right, and the scrolling.
The stream is a panel in the top-right corner, 24 grids tall, at most a quarter of the window wide and never wider than its old 40 grids, wrapping its entries to fit (`5d44000`, r541; `2fc1881`, r552).
Below 24 grids wide it hides itself, and `l` still shows it for the run.
The map reserves the panel as a strip along the right or the top, whichever leaves the city larger.
It scrolls a whole entry per wheel notch while the pointer is over it, or by dragging its bar; scrolled back it holds still and says how many are newer above (`4e42d89`, r561).
`StreamCorner` still offers the bottom right, flush on the footer with the minimap above it (`cfd4d08`, r564, after the r561 frames showed it running over the footer's needs-you line).

The frames: `botropolis/docs/screenshots/r561-item-100-top-right-960-scrolled.png`, `r561-item-100-bottom-right-960-card.png` and `r561-item-100-bottom-right-1600-card.png`, and before them the r552 corner set and the r541 widths.
The tests are `TestStreamArea`, `TestLayoutStreamWraps`, `TestLayoutStreamScrolled`, `TestFollowStream`, `TestToggleStream` and `TestMinimapBesideStream` in `botropolis/pkg/ui`, `TestSetCornerChrome` in `botropolis/pkg/city`, and `TestStreamColumnNarrow` and `TestStreamScrolls` in the acceptance suite.

Flagged for Aria: no test covers the bottom-right panel's flush footer, since `StreamCorner` is a constant and the tests run top right; the frames are its check.
The minimap is drawn only once zoomed past the fit, so no frame shows it moving above a bottom-right panel; a unit test covers it.
