# 359. Pointing at a grouped building lights only that building, not its group

**Done 2026-11-06 (`bd3a11d5`, r1280). Filed 2026-11-06 (r1276) at Aria's request.**

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

## Answered while building

- **The test tree** (roadmap manager, 2026-11-06): approved — the `hit.Building` branch lights a grouped building's whole group and the towers it calls, and a new field narrows `HasBeam` to the pointed-at building's own lines, so a tower it calls does not also light its lines to other members; the selection-only path is untouched; `TestTheGroundKey` gains a fixed move from a grouped building to an ungrouped one, and its random walk's city gets a group.
- **A group of one is treated as no group** (roadmap manager, 2026-11-06, from "the same as today" above): it lights its building and its towers, and nothing when it calls none, so a lone building never fades the whole city.
- **The selected building's roads still win** (roadmap manager, 2026-11-06): pointing at the selected building while its roads are shown keeps showing them, as today.
- **The recede reads at the fitted view** (Aria, 2026-11-06, on item 348's focused frames: *"Yes, dim more"*): under a group focus, and under this item's hover, the buildings outside the lit set dimmed too little to see at the fitted zoom.
  This item takes it as its second slice, since it owns the highlight now: a stronger recede, with a frame of each highlight — a tower, a building, a group under the pointer, a focus — for Aria.
- **Slice 2's test tree** (roadmap manager, 2026-11-06): approved — the one dim every dimmed thing shares, in `pkg/render/search.go`, scaled RGB and alpha alike, so it only turned sprites 35% opaque with a blue cast and read as pale, not dimmed; it becomes darker, with no hue of its own, the numbers Aria's on frames.
  It stays one tint, so the finder's filter and a hovered car's faded streets deepen with it, and the frames show a filter before and after too.
- **The stronger dim passes** (Aria, 2026-11-06, on the before-and-after frames: *"Pass"*): one grey for the three channels at 0.2 and alpha at 0.55, in place of 0.35 alike with a blue cast; it covers a tower, a building, a group hover, a focus and the finder's filter.

## Closed

Done in two slices, landed together after 0.4.1 was tagged.
Slice 1 (`feb1137c`, r1278): pointing at a building in a group of two or more lights the group, through `tieGroup` in `pkg/city/highlight.go`, and `HasBeam` keeps only the pointed-at building's own lines; `TestHighlightGroup` in `pkg/city` holds it, and `TestTheGroundKey`'s random walk now moves sessions in and out of a group.
Its frames are `botropolis/docs/screenshots/r1277-item-359-attention-group-hover.png` and `-servers-group-hover.png`.
Slice 2 (`bd3a11d5`, r1280): the shared dim is the constant pair `dimLight`, `dimAlpha` in `pkg/render/search.go`, held by `TestDim` and `TestUnlitUnderEveryHighlight`; the before-and-after frames are `botropolis/docs/screenshots/r1279-item-359-dim-*.png`.
The changelog's `[Unreleased]` says both (`6d96fdc2`, r1281).

Deviation, flagged: the frames' filenames cite r1277 and r1279, the revisions they were shot at before the rebase, and their commits landed as r1279 and r1280.
A hovered car's faded streets were not filmed, as the staged city has no roads; they take the same tint.
Item 348's "hovered" frames used a group focus, because no hover lit a group until this item, so they may want reshooting with the real hover.
