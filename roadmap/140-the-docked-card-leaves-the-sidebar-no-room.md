# 140. In a short window the docked card leaves the sidebar no room for a single row

**Open, in progress since 2026-10-19 in the session "item 140". Filed 2026-10-19 (r711), from item 136. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`e77370e`, r730).

[Item 136](136-the-sidebar-cuts-off-rows-past-the-window.md) made the sidebar scroll and keep the selected session's row in view.
Building it, its session found that the selection's card, docked at the sidebar's foot, takes the panel's height first: at 1024×600 with a session selected in the metropolis demo the list is 25–40 px tall and shows no rows at all, so there is nothing to scroll and the selected row cannot be shown.
This predates item 136; at 1024×900 the list has room and item 136's acceptance test holds.

## The fix

Give the list a floor of about four rows. When the docked card would push it under that, the card gives way — shrinking to its title and verbs, or standing beside the panel rather than under it, whichever item 100's small-window rules already use for the stream.

Tests: at 1024×600 with a selection, the list should show at least four rows and the selected one; the card should stay whole on screen and clear of the list.
