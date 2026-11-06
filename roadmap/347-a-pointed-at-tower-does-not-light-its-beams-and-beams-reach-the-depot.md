# 347. Pointing at a water tower does not light its lines, and those lines run to the depot too

**Fixed 2026-11-06 (`779d874`, r1273). Filed 2026-11-05 (r1260), from Aria dogfooding 0.4.0 on her own sessions, at her request. Nobody's call — Aria chose the default on 2026-11-06.**

Depends on: nothing
Landed: slice 1 (`0c9768a`, r1266).
Landed: slice 2 (`779d874`, r1273).

Aria: *"highlighting a water tower in the servers view should also highlight its lines to the agents. We also need a way to show only connections to buildings or also to packed sessions"*.

## Part 1: the lines light with the tower

Pointing at a tower already lights the sessions that call its server and fades the rest (`pkg/city/highlight.go`, and [the design](../botropolis/design/info-views.md)).
The lines do not follow.
`beams` in `pkg/render/game.go` brightens a beam only when `hover.Beam` is that beam, which means pointing at the line itself.
So the buildings light up while the lines that explain why stay as they were, among every other tower's.

The fix: a beam whose tower is the one pointed at draws in the highlight colour, and the other beams fade with the rest of the city.
Pointing at a line keeps lighting that one line.

## Part 2: lines to packed sessions

`City.Beams` in `pkg/city/landmarks.go` runs over `c.Buildings()`, and that includes the crates in the depot, which `placeLines` has to skip by hand.
So a session packed away keeps its line from every tower it ever called.
On a real city with about 90 crates, a frame shows thin lines crossing the map's whole empty south to reach them, and packing does nothing to thin the view out.

A way to choose: lines to buildings only, or to packed sessions as well.
It is one setting in the Servers lens, and it should be reachable from the lens panel, so it is not hidden in the settings.
The counts the panel shows should say which they cover.

**The default is buildings only** (Aria, 2026-11-06, to the roadmap manager), since packing a session is saying it is finished with,
and a tower's lines are most useful for what is still on the map.
The switch in the lens panel shows the lines to the depot's crates too.

## Tests

- In `pkg/city`: when a tower is pointed at, its beams should be in the highlight and the others should not.
- When the setting is off, there should be no beam to a crate in the depot, and when it is on, there should be.
- A frame of Servers with a tower pointed at, for Aria to judge.

## Answered while building

- **The test tree** (roadmap manager, 2026-11-06): approved as sent, two slices — part 1 in `pkg/city` and `pkg/render`, with the beam look a pure function tested without a GPU; part 2 the setting, the scene, the lens panel, the changelog and the docs.
- **The key** (roadmap manager, 2026-11-06): `tower_lines`, `buildings` (default) or `all`, after `group_lines`; set through `--set` with no flag of its own, as item 149 wants, with a row in the settings panel and in botropolis-config(5).
- **A pointed-at building lights its own beams too** (roadmap manager, 2026-11-06): pointing at a building already lights the towers it calls, so the lines between them light for the same reason a tower's do; a district hover or a group focus lights no beam.
- **The lens panel's words** (roadmap manager, 2026-11-06): "12 lines from 3 towers to 8 sessions on the map" or "… and 90 crates", with a switch line under it, "show lines to the depot too" / "lines to buildings only"; provisional until Aria sees the frame, which is why the frame comes after slice 2.
- **The frames** (Aria, 2026-11-06, to the roadmap manager): the panel's words pass — the aggregate's two forms and the switch's two forms — and the lit lines are to be brightened, *"Pass words, brighten lines"*: at the frame's zoom the pointed-at tower's lines were too thin and faint to pick out from the faded ones.
- **Slice 1 left the kept ground's key stale** (item 343's session, 2026-11-06): the key did not name what the highlight lights, so pointing from one session to another kept the first one's beams; fixed in `5bae78c0` with the key reading `HasTower` per tower and `HasBuilding` per building.

## Closed

- **Part 1** (`0c9768a`, r1266): `Highlight.HasBeam` is whether both ends of a beam are lit, so a pointed-at tower lights its beams, a pointed-at session lights its own, and a district or a group lights none.
  The renderer's `beamLook` draws a lit beam with an opaque white line over it, four world units wide and never under three pixels on screen (`779d874`, r1273, after Aria's *"brighten lines"*), and fades the others by the ground's receded alpha.
  Tests: `TestHighlightBeams` in `pkg/city`, `TestBeamLook` in `pkg/render`.
- **Part 2** (`f3e8961`, r1271): `tower_lines`, `buildings` by default or `all`; `City.Beams()` leaves out crates under `buildings`, so a crate's line is neither drawn nor pointed at.
  The Connections panel on the servers view counts its lines and says which they cover, and its switch flips the setting through the settings panel's row and save.
  A change bumps the ground generation, since the beams are painted into the kept ground.
  Tests: `TestTowerLines` and `TestLensPanelTowerLines` in `pkg/city`, `TestTowerLinesKey` in `pkg/config`, `TestLensPanelSwitch` and `TestTheGroundKeyFollowsTowerLines` in `pkg/render`, `TestLayoutLensPanelSwitch` in `pkg/ui`, and `TestSurface` holds the key's values.
- **Frames** (`3d1a7df`, refilmed in `779d874`): `botropolis/docs/screenshots/r1267-item-347-servers-tower-buildings.png` and `r1267-item-347-servers-tower-depot.png`, filmed from a tidy-style scenario that closes the harbor group into the depot first.
  Their names carry r1267, the revision they were filmed on before the last rebase; the code they show landed as r1273.
  The filmer's shots now take a `set:` map of config keys, so a frame can show a setting's other value.
- **For Aria to judge**: the brightened frame went to her through the roadmap manager, and the item closes without waiting on her verdict, as the manager asked; a further change would be a follow-up.
