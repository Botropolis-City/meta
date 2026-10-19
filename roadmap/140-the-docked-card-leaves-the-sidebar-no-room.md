# 140. In a short window the docked card leaves the sidebar no room for a single row

**Fixed 2026-10-19 (`e77370e`, r730). Filed 2026-10-19 (r711), from item 136. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`e77370e`, r730).

[Item 136](136-the-sidebar-cuts-off-rows-past-the-window.md) made the sidebar scroll and keep the selected session's row in view.
Building it, its session found that the selection's card, docked at the sidebar's foot, takes the panel's height first: at 1024×600 with a session selected in the metropolis demo the list is 25–40 px tall and shows no rows at all, so there is nothing to scroll and the selected row cannot be shown.
This predates item 136; at 1024×900 the list has room and item 136's acceptance test holds.

## The fix

Give the list a floor of about four rows. When the docked card would push it under that, the card gives way — shrinking to its title and verbs, or standing beside the panel rather than under it, whichever item 100's small-window rules already use for the stream.

Tests: at 1024×600 with a selection, the list should show at least four rows and the selected one; the card should stay whole on screen and clear of the list.

## Answered while building

- **Shrink or stand beside** (manager, 2026-10-19): the card ~490 px tall at 1024×600, so shrinking it to its title and verbs would drop nearly all of it; it stands beside the panel, not pinned to its building, which jumps as the selection changes.
- **The covers** (manager, 2026-10-19): a card beside the panel keeps clear of the lens panel, the stream and the minimap, as item 127's key list does, and prefers covering the lens panel to leaving the screen.
- **No clear place at 600** (manager, 2026-10-19): measured, nothing beside the sidebar holds the card clear of both the lens panel and the stream, so the ladder: the whole card docked at the foot; else the whole card beside, clear of every cover; else, with its details closed, the compact card (kind, title, verbs) at the foot; else the card beside, over the lens panel. `i` must still open the full card from the compact form.

## Closed

Slice 1 (`e77370e`, r730) gave the list a floor of four rows between both scroll marks (`ui.SidebarFloor`), and `ui.DockCard` places the card down the ladder above.
At 1024×600 the card is compact at the foot with four rows above it and the selected one among them; `i` brings the full card back, beside the panel over the lens panel.
At 1024×900 it is docked whole, as before.

Two deviations from the approved tree, both passed by the manager:
the last rung stands the card beside the panel over the lens panel rather than "covering the least", since by area the least is the stream (about 32,000 against 32,700 px²);
and a card beside the panel keeps its top under the strip, drawn on an opaque backing so the lens panel's text does not show through, after the first frames showed both.

Frames, passed by the manager for Aria (2026-10-19): `botropolis/docs/screenshots/r730-item-140-sidebar-600-compact.png`, `…-600-details.png` and `…-900.png`, the metropolis demo.
At 600 the folded-out detail lines do not fit and are dropped, as they already were for any card short of room; the rest of the full card returns.
The footer in the 600 frames shows two lines starting "needs-you:".
The white one is not a second needs-you line: it is the status notice `tab` leaves (`botropolis/pkg/render/strip.go`, the state's name and the session's title), which names where it jumped in the same words as the footer's needs-you line.

Tests: `TestSidebarFloor` and `TestDockCard` in `botropolis/pkg/ui/dock_test.go`, a case per rung; `TestSidebarCard` in `botropolis/testing/acceptance/sidebar_test.go`, at 1024×600 and 1024×900, checks four rows, the selected row, the card whole on screen, clear of the list, the lens panel and the stream, and `i` at 600.
Disabling the compact rung fails it at 600.

**Aria's verdict** (2026-10-19, reviewing the frames the roadmap manager passed overnight): approved.
