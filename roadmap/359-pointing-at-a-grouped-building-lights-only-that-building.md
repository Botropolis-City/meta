# 359. Pointing at a grouped building lights only that building, not its group

**Open. Filed 2026-11-06 (r1276) at Aria's request. Nobody's call — she has said what it should do.**

Aria, on item 348's frames of a group focused: *"I do think that a whole group should stay visible not just a single sesssion if the session is part of a group"*, and, asked where, *"Everywhere, on hover only"*.

## Where it stands

`Scene.Highlight` in [`pkg/city/highlight.go`](../botropolis/pkg/city/highlight.go) lights a building under the pointer through `tieBuilding`, which lights it and the towers it calls, and nothing at all when it calls none.
A building's group plays no part.
The group's own lit set exists already: a group focus (`s.focus`) keeps every building of the group lit and recedes the rest, as focusing from a card, City Hall's board or the finder does.

## What it wants

- **The pointer on a grouped building lights its whole group**, in every lens, and the rest of the city recedes as it does under a group focus.
  In Servers it also lights the towers the pointed-at session calls, and their lines to it, so the lens's own answer is kept.
- **Hover only.** A selected building with the pointer elsewhere keeps today's answer, `tieBuilding` on the selection, so an open card does not hold the whole city faded.
- **A building in no group** keeps today's answer.
- A group of one (item 344) lights its one building, which is the same as today.

Only the lit set changes, so the kept ground's key ([item 347](347-a-pointed-at-tower-does-not-light-its-beams-and-beams-reach-the-depot.md)) already reads it through `HasBuilding`; check that in `TestTheGroundKey`'s random walk, which pointed at buildings when it found 347's bug.

## Tests

In `pkg/city`: when the pointer is on a grouped building → every building of its group is lit, and one outside it is not; in Servers, its towers are lit too, and another group member's towers are not unless it calls them; when the pointer is on a building in no group → only it and its towers, as today; when the pointer is on nothing and a grouped building is selected → only it and its towers, as today.
A frame for Aria: the pointer on a grouped building, on the large city item 348 stages.
