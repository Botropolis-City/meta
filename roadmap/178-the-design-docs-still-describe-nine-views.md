# 178. `DESIGN.md` and `design/info-views.md` still describe nine views and two projections

**Open, in progress since 2026-10-20 in the session "item 178". Filed 2026-10-20 (r786), by the fresh-eyes audit, item 154. Nobody's call — a defect.**

Depends on: nothing

The city has six lenses (`city.Lenses`, `botropolis/pkg/city/lens.go`: Attention, Work, Cost, Capacity, Health, Connections) and one projection: `--projection` is deprecated and its help says *"the map is isometric"*.
The design documents have not caught up:

- `botropolis/DESIGN.md`'s index describes `info-views.md` as *"the nine views, their legends and what each says"*.
- `botropolis/design/info-views.md` opens *"There are two projections and the views have to mean the same thing in both"*, and its section on networks assigns them to views that no longer exist: *"Spend has the wires and the train, Servers the beams, Traffic the cars and the drones, Fan-out the drones"*.

`design/city-and-rendering.md` already says the top-down projection survives only inside `pkg/city`, so the two documents also disagree with each other.

The fix rewrites those passages for the six lenses and one map, keeping the history as history.
The comments in `pkg/ui/viewkey.go` and `pkg/render/viewkey.go` that say *"the nine views"* are about what the key replaced, so they can stay.
