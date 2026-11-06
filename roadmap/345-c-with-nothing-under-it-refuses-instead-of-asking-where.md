# 345. `c` with nothing under the pointer refuses instead of asking where

**Fixed 2026-11-06 (`8e5367b`, r1261). Filed 2026-11-05 (r1260), from Aria dogfooding 0.4.0 on her own sessions, at her request. Nobody's call — she has said what it should do.**

Aria: *"a c on the map with no hover should ask me in which directory to create a new session"*.

## Where it stands

`NewHere` in [`scene.go`](../botropolis/pkg/city/scene.go) takes the selected session's folder, or the hovered district's root.
With neither, it returns no action and the footer note "select a building or hover a district first".
Hovering the depot counts as neither, so `c` there gets the same note.
`pkg/city/scene_test.go` pins the refusal in its third `NewHere` case.

The city already has the question.
New session ([`newsession.go`](../botropolis/pkg/render/newsession.go)), on `Shift+N` by default, opens on its directory field with completion when nothing is selected.

## The fix

`c` with nothing selected and no district under the pointer opens New session on its directory field.
A selection or a hovered district starts a session there at once, as it does now; item 302's attach is unchanged.

`NewHere` is in `pkg/city` and `openNewSession` in `pkg/render`, so `NewHere` needs to say "ask" rather than refuse, in the way `ActionMoveToGroup` asks `act` to open its picker.
The README's key line and the in-city key reference say what `c` does and should mention it.

## Tests

- In `scene_test.go`, the refusal case becomes: when nothing is selected or hovered, it should ask.
- The same for hovering the depot.
- In `pkg/render/newsession_test.go`, when `c` is pressed with nothing under the pointer, it should open New session with the directory field focused and empty.
- The selected and hovered cases stay as they are, so a session still starts with no question.

## Answered while building

- **The test tree** (roadmap manager, 2026-11-06): approved as sent — `scene_test.go`'s refusal case becomes "it should ask where", a depot case beside it, and `newsession_test.go` checks that `c` over nothing opens New session on an empty, focused directory field and starts nothing, while a selected building still starts at once.
- **The kind's name** (roadmap manager, 2026-11-06): `ActionAskWhere`, string `"ask where"`, with an `actionText` line like every other kind; it follows `ActionMoveToGroup`'s shape, an action that asks `act` to open a panel, and the item decides nothing else about it.

## Closed

`8e5367b` (r1261) gives `NewHere` a third outcome: with nothing selected and no district under the pointer, the depot included, it returns `ActionAskWhere`,
and `act` opens New session on its empty directory field, the way `ActionMoveToGroup` opens the picker.
A selection or a hovered district still returns `ActionNew` and starts there at once.
`pkg/city/scene_test.go` pins both ask cases in `TestSelectionActions`, with the depot case checking the depot is really under the pointer,
and `pkg/render/newsession_test.go` pins that `c` over nothing opens the panel focused on an empty directory field and starts nothing,
while `c` with a building selected starts a session with no panel.
The key reference row, `README.md`'s key line and the changelog's `[Unreleased]` say what `c` does now.
No frame to judge: the panel it opens is New session as it already was.
