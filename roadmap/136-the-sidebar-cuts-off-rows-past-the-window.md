# 136. The sidebar cuts off every row past the bottom of the window

**Fixed 2026-10-19 (`27fe1de`, r721). Filed 2026-10-19 (r707), from the validation checklist's step 9 run against main before 0.2.0. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`5352172`, r720).
Landed: slice 2 (`27fe1de`, r721).

Step 9 of the [validation checklist](validation-checklist.md) asks that `b` with more projects than fit scrolls the sidebar and keeps the cursor row visible.
Run on Aria's machine on 2026-10-19 (84 resting sessions across a few dozen projects), the sidebar showed its first ~35 rows and nothing after them: `ui.LayoutSidebar` (`botropolis/pkg/ui/sidebar.go`) stops adding rows at the panel's bottom and returns, with no scroll offset, no wheel or keyboard movement and no "N more" mark.
So every project and session below the fold, and the whole **hidden** section with its *show* buttons, cannot be reached from the sidebar at all; nothing says anything is missing.
The sidebar has no keyboard cursor either, so the checklist's "cursor row" no longer describes it.

## The fix

Item 127's answer for the key list, applied here: the sidebar scrolls with the wheel over it and with PageUp, PageDown, Home and End while it is open (the arrows keep panning the map; manager, 2026-10-19), marks "N more above" / "N more below" when rows are out of view, and keeps the selected session's row in view when the selection changes (from the map, `tab` or the finder).
Update step 9's wording in the checklist to what the sidebar is.

Tests: a layout with more rows than fit → it should mark how many are below; scrolled → it should show the rows after the fold and mark those above; with a selection below the fold → it should scroll to keep it in view; the hidden section is reachable by scrolling.

## Answered while building

- **The keys** (manager, 2026-10-19): neither the arrows nor arrows-while-pointing; PageUp, PageDown, Home and End scroll the sidebar while it is open, the arrows keep panning, and the wheel over the panel scrolls it instead of zooming.
- **The card squeezing the list** (manager, 2026-10-19): filed as its own item rather than fixed here.

## Closed

Slice 1 (`5352172`, r720) made the sidebar scroll.
`ui.LayoutSidebar` lays out every row, then shows a window of whole rows with "N more above" and "N more below"; it takes the scroll and a flag to reveal the selection, and keeps both in range.
The wheel over the panel scrolls it and no longer zooms the map, PageUp and PageDown move a page (the rows that fit between both marks), Home and End go to either end, and the arrows still pan.
When the selection changes, from the map, `tab` or the finder, the list scrolls just far enough to show its row, once, so it can be scrolled away from after.
Slice 2 (`27fe1de`, r721) fixed what the first frame showed: the panel ran down under the footer's needs-you line, hiding the "more below" mark, and now ends where the footer begins.
And the page keys no longer clamp against the last drawn layout, so a key pressed before the panel's first draw still counts.
Step 9 of the checklist now describes the sidebar as it is.

Frames, passed by the manager for Aria (2026-10-19): `botropolis/docs/screenshots/r721-item-136-sidebar-top.png`, `…-paged.png` and `…-end.png`, the metropolis demo at 1280×800.

Tests: `botropolis/pkg/ui/sidebar_test.go` covers the marks, the rows clear of them, scrolling, clamping, the hidden section reached at the end, the page size, and revealing a selection below, above and already in view.
`botropolis/testing/acceptance/sidebar_test.go` drives PageDown, PageUp, Home, End and the wheel on the metropolis demo at 1024×900.
It checks the camera neither moves nor zooms, the up arrow still pans, the panel stays clear of the footer, and each selection `tab` walks to has its row in view.
The reveal and the wheel hook were each removed to watch their tests fail.

**Left open, for the item the manager files:** in short windows the selection's card, docked at the sidebar's foot, leaves the list no room.
At 1024×600 on the metropolis demo, with a session selected, the list is 25 to 40 px tall and shows zero rows,
so the selected row cannot be kept in view there; the acceptance test runs at 1024×900, where it holds.

**A follow-up, the manager's note:** when scrolled, a district's session rows can sit at the top with its header out of view (in the paged frame, "Sea conditions…" under "1 more above"),
so the top district's header could stick.

**Aria's verdict** (2026-10-19, reviewing the frames the roadmap manager passed overnight): approved.
