# 136. The sidebar cuts off every row past the bottom of the window

**Open, in progress since 2026-10-19 in the session "item 136". Filed 2026-10-19 (r707), from the validation checklist's step 9 run against main before 0.2.0. Nobody's call — a defect.**

Depends on: nothing

Step 9 of the [validation checklist](validation-checklist.md) asks that `b` with more projects than fit scrolls the sidebar and keeps the cursor row visible.
Run on Aria's machine on 2026-10-19 (84 resting sessions across a few dozen projects), the sidebar showed its first ~35 rows and nothing after them: `ui.LayoutSidebar` (`botropolis/pkg/ui/sidebar.go`) stops adding rows at the panel's bottom and returns, with no scroll offset, no wheel or keyboard movement and no "N more" mark.
So every project and session below the fold, and the whole **hidden** section with its *show* buttons, cannot be reached from the sidebar at all; nothing says anything is missing.
The sidebar has no keyboard cursor either, so the checklist's "cursor row" no longer describes it.

## The fix

Item 127's answer for the key list, applied here: the sidebar scrolls with the wheel over it and with the arrow keys while it is open, marks "N more above" / "N more below" when rows are out of view, and keeps the selected session's row in view when the selection changes (from the map, `tab` or the finder).
Update step 9's wording in the checklist to what the sidebar is.

Tests: a layout with more rows than fit → it should mark how many are below; scrolled → it should show the rows after the fold and mark those above; with a selection below the fold → it should scroll to keep it in view; the hidden section is reachable by scrolling.
