# 122. The app credits nobody whose work it draws

**Open, in progress since 2026-10-18 in the session "item 122". Filed 2026-10-18 (r628), from the art audit Aria asked for. Nobody's call — Aria asked for it.**

Aria, 2026-10-18: *"Make sure that for anything we pulled from an asset pack we have followed their licensing and attributed and thanked them."*

Someone who installs the package and never reads the README sees no credit anywhere.
The licence texts are installed under `/usr/share/licenses/botropolis/` (item 121), but inside the app the only mentions of Kenney are code comments.
Neither licence requires an in-app credit.
This is a thank-you, put where the people looking at the art will see it.

The natural place is the help overlay, `?`.
`pkg/render/reference.go:67` lays it out with `ui.LayoutHelp(th, width, height, "Keys", g.helpKeys(), g.faces.Measure)`, and `pkg/ui/help.go` sizes the panel to its title and key rows.
`pkg/ui/help_test.go` pins that layout: centred, one row per key, the label column, the panel sized to the longest row plus padding.

## The fix

One quiet line at the foot of the help panel, in the `Small` size and dimmed, along the lines of *"City art by Kenney (CC0) · type by Inter (OFL) · rendered in Blender"*.
`LayoutHelp` takes it as a field and places it under the last row, and the panel's width and height include it.
It is not a key, so it does not join `Rows` and `Hit` never returns it.

## Done when

The help overlay shows the credit line on every heading and zoom, the layout tests cover its placement and the panel's size with it, and a frame of the overlay is in `botropolis/docs/screenshots/` for Aria to judge.
