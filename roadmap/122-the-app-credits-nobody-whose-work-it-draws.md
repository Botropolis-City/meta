# 122. The app credits nobody whose work it draws

**Done 2026-10-18 (`f78040b`, r649). Filed 2026-10-18 (r628), from the art audit Aria asked for. Nobody's call — Aria asked for it.**

Depends on: nothing
Landed: slice 1 (`f78040b`, r649).
Landed: slice 2 (`e72f66c`, r650).

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

## Where it went instead (2026-10-18)

`?` opens on the reference's index, not the key list: the key list is one of the index's terms, and only it is laid out by `LayoutHelp`.
That list is now about forty rows and already runs off a 1600×1000 window at the top and bottom with no scroll, so a line at its foot could not be seen.
The manager ruled for the foot of the index instead, under "click a term to open it": it is the help overlay's front page, short enough to fit any window, and where people land when they press `?`.
The key list overflowing is filed as its own defect.

The wording is the one the website and the README share, with Aria's ruling that the font credit names the licence holder:
*"Roads, trees, vehicles, trains, boats and landmarks by Kenney (kenney.nl), CC0 — thank you. Session buildings, the drone, the fountain and the building sites are modelled for Botropolis. Set in Inter by The Inter Project Authors (SIL OFL 1.1)."*
The stop-word list in `pkg/group/stopwords` is not drawn, so it is not credited here.

Slice 1 is the layout and its tests: `NewReference` takes the credit for the index entry, and `LayoutReference` wraps it at the panel's measure in `Small`, one grid under the hint, growing the panel by a grid plus a line per wrapped line, at theme scales 1 and 2; another entry, or an empty credit, lays out none.
Slice 2 is the frame, `botropolis/docs/screenshots/r649-item-122-reference-credit.png`, from the synthetic home.
The overlay does not depend on the camera's heading or zoom, so one frame shows it for all of them.

## Closed

Done in `f78040b` (r649): the reference's index ends with the credit, wrapped and dimmed under its hint, with the layout tests in `pkg/ui/reference_test.go`.
The frame landed in `e72f66c` (r650), and Aria passed it on 2026-10-18: *"Pass, close it."*
The changelog entry is `9cd2407`.
The deviation, flagged above and ruled by the manager: the credit is on the index, the overlay's front page, rather than under the key list, which overflows the window and is its own defect.

## Done when

The help overlay shows the credit line on every heading and zoom, the layout tests cover its placement and the panel's size with it, and a frame of the overlay is in `botropolis/docs/screenshots/` for Aria to judge.
