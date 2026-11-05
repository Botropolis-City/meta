# 344. A group with one session on the map is hidden

**Open. Filed 2026-11-05 (r1260), from Aria dogfooding 0.4.0 on her own sessions, at her request. Nobody's call — she has said what it should do.**

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
