# 344. A group with one session on the map is hidden

**Fixed 2026-11-06 (`e85936f`, r1263). Filed 2026-11-05 (r1260), from Aria dogfooding 0.4.0 on her own sessions, at her request. Nobody's call — she has said what it should do.**

Depends on: nothing
Landed: slice 1 (`e85936f`, r1263).
Landed: slice 2 (`5d2325d`, r1264).
Landed: slice 3 (`abf1567`, r1267).

Aria: *"Also add a roadmap item not to hide groups of 1."*

## What happened

Aria made two new groups from *move to group*, typed their names, and neither appeared: *"The groups did not get created."*
They had been created.
`groups.json` held both, and `botropolis status --json` named each session's group.
The city dropped them without a word.

It gets worse from there.
Two sessions in two hidden groups cannot be put together, because the picker lists only `g.scene.Groups()` ([`move.go`](../botropolis/pkg/render/move.go)), which leaves the hidden ones out.
And a hidden group's name is free to the picker's check while still being taken in the file.

## Why

`groupsOnMap` in `pkg/city/onmap.go` drops every group with fewer than two sessions on the map and clears `Group`, `GroupJoined`, `GroupLikely` and `GroupWords` on its member.
`pkg/city/tidy_test.go:85`, "when fewer than two of a group's members are on the map", pins it.

## What it wants

A group with one session on the map is shown: on the board, in the picker, and on its member's card.
A group with **none** on the map stays off, since the board counts what the map draws.

## What to check while changing it

- **The quiet sweep changes meaning.**
  `state.Quiet` packs only sessions with `Group == ""`, and it reads the buildings' sessions after `groupsOnMap`.
  Today a resting session left alone in its group counts as in no group, so it gets swept.
  Once it keeps its group, it never will, unless closing the group or a rule for it takes over.
- **Guessed groups with one member left.**
  Packing all but one of a detected group now leaves a row with the detector's guess for a name.
  Aria's words cover these too; if the board turns noisy, bring that to her with the count rather than bringing the rule back.
- **The walk.** `walkGroups` will offer one-session groups as cards.
- **Lines.** A group in one district already draws a badge and no line, which should cover one session; check it in a frame.
- **A solo team is a different thing.** Item 14 removed a one-member team named after its own session, and that stays.

## Answered while building

- **The test tree** (roadmap manager, 2026-11-06): approved as sent, two slices — the city keeps every group with one or more sessions on the map and drops only those with none, the clear-`Group` path going with it; the picker and its name check follow through `scene.Groups()`; a resting session alone in its group is never swept, as every grouped session already is not.
- **The walk** (roadmap manager, 2026-11-06): keeps its two-member bar for a group's card, which item 333 set and 0.4.0 shipped.
  A group of one is shown on the board, in the picker and on its card, and the walk does not ask about it; Aria's words are about hiding, and the walk skipping it hides nothing.
- **The frames pass** (Aria, 2026-11-06, to the roadmap manager): the badge on the one building, no line, and the board's "driftwood · 1 session" row — *"Pass"*.
  Noticed on the board frame, not from this item: the row's move column names an off-map member, since the move is computed over every member; left as is.

## Closed

`groupsOnMap` keeps every group with a session on the map and drops only those with none (`e85936f`, r1263); the path that cleared a dropped group's member went with it as dead code.
The picker and its name check followed through `scene.Groups()`, and `walkGroups` skips a group with one session on the map, so it is shown everywhere and asked about nowhere (`5d2325d`, r1264).
`pkg/city/tidy_test.go` pins the group shown with one member, the badge, the card, no line, the quiet sweep leaving a session alone in its group, and a group with none on the map staying off; `pkg/render/move_test.go` and `walk_test.go` pin the picker and the walk.
The frames are [`r1264-item-344-badge.png`](../botropolis/docs/screenshots/r1264-item-344-badge.png) and [`r1264-item-344-board.png`](../botropolis/docs/screenshots/r1264-item-344-board.png) (`abf1567`, r1267), passed by Aria.
Nothing deviates from what the item asked; the walk's two-member bar is item 333's, kept as answered above.
