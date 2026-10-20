# 178. `DESIGN.md` and `design/info-views.md` still describe nine views and two projections

**Fixed 2026-10-20 (`a92fab4`, r800). Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

Depends on: nothing

The city has six lenses (`city.Lenses`, `botropolis/pkg/city/lens.go`: Attention, Work, Cost, Capacity, Health, Connections) and one projection: `--projection` is deprecated and its help says *"the map is isometric"*.
The design documents have not caught up:

- `botropolis/DESIGN.md`'s index describes `info-views.md` as *"the nine views, their legends and what each says"*.
- `botropolis/design/info-views.md` opens *"There are two projections and the views have to mean the same thing in both"*, and its section on networks assigns them to views that no longer exist: *"Spend has the wires and the train, Servers the beams, Traffic the cars and the drones, Fan-out the drones"*.

`design/city-and-rendering.md` already says the top-down projection survives only inside `pkg/city`, so the two documents also disagree with each other.

The fix rewrites those passages for the six lenses and one map, keeping the history as history.
The comments in `pkg/ui/viewkey.go` and `pkg/render/viewkey.go` that say *"the nine views"* are about what the key replaced, so they can stay.

## Closed

`botropolis/DESIGN.md`'s index row now reads *"the six lenses, the views they fold, their legends and what each says"*.
`botropolis/design/info-views.md` opens on the six lenses and the ten views they fold, and keeps the two projections as history, retired by item 106.
It also says why `ui.Receded` outlived the top-down map: the isometric map's driveway pads, and its streets when no kit is loaded, are flat fills that still drain through it.
The networks sentence that named views which no longer exist is now a lens | view | networks table.
`botropolis/pkg/city/network_doc_test.go` holds that table against `View.Shows` for every view of every lens, and was mutated red three ways: a wrong network, a missing row, and a lens that does not exist.
The base-view paragraph had gone stale the same way, saying Attention draws one network where it draws three, and was rewritten too.

One deviation, agreed with the manager: the item said `botropolis/design/city-and-rendering.md` was already right, but top-down also survives in `pkg/render`, as a flat drawing path the app no longer reaches.
That sentence now says so, and the dead code is filed as item 183 rather than removed here.
The manager also dropped a proposed test on the index row's wording, since a string match on an index is not a guard.
