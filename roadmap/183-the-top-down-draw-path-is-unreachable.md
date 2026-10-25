# 183. `pkg/render` still carries the top-down drawing path, which the app no longer reaches

**Open, in progress since 2026-10-25 in the session "item 183". Filed 2026-10-20 (r786), found while working item 178. Nobody's call — dead code.**

Item 106 retired the top-down map: `city.UserProjection` (`botropolis/pkg/city/projection.go`) turns `top` into `Isometric` with a warning, and both ways a projection reaches the map go through it — `--projection` via `projectionFor` (`botropolis/pkg/app/projection.go`) and the setting via `config.KeyProjection` (`botropolis/pkg/render/settings.go`).
`render.Run` and the drive harness then call `SetProjection` with that value or with `Isometric` (`botropolis/pkg/render/run.go`, `botropolis/pkg/render/drive.go`).

`Game.Draw` (`botropolis/pkg/render/game.go`) still branches on `cam.Projection == city.Isometric`, and everything after that branch is the top-down map:
`ground`, `flatCells`, `drivewayPads(…, true)`, `overgrowth(…, true)`, `district`, `building` and the `block` it draws, `flatBody` (`botropolis/pkg/render/view.go`), and the flat half of `shoreImage` (`botropolis/pkg/render/shore.go`).
None of it is reachable from the app.

`TopDown` is `Projection`'s zero value, so a `Scene` whose projection is never set still draws through that path.
The fix decides between deleting the path and making `Isometric` the zero value, so that no camera can ask for a map that no longer exists.
`pkg/city`'s own use of `TopDown` as the identity, which most of its tests run in, is separate and stays (`botropolis/design/city-and-rendering.md`).

`ui.Receded` stays either way: the isometric map's driveway pads (`padColour`, `botropolis/pkg/render/driveways.go`) and its streets when no kit is loaded (`botropolis/pkg/render/iso.go`) still drain through `g.flat`.
`botropolis/design/info-views.md` says so since item 178, and `botropolis/design/city-and-rendering.md` names this path; both need a line changed when it goes.

Item 149 removes the `projection` config key before 1.0, which is the user-facing half of the same retirement; this item is the code-facing half and does not depend on it.

## Answered while building

- **Delete the path or flip the zero value** (manager, 2026-10-25): delete it. `NewGame` sets `Isometric`, `render.Options.Projection` goes, and `pkg/city` keeps `TopDown` as its identity. Item 149 had already removed `--projection` and the config key, so this item's first paragraph was out of date when it started. `city.ParseProjection`, dead since item 149, goes in the same slice.
- **The 16px Kenney packs** (Aria, 2026-10-25, asked by the manager): delete them as slice 2, since nothing draws them once the path is gone: `pkg/assets/kenney/`, `assets.Tilemap`, `License` and `Pack`, and every place that names them in the Makefile, packaging, README and design notes, with a changelog line. `kits/` and its Kenney credit stay.
