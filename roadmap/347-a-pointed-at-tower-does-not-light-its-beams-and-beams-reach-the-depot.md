# 347. Pointing at a water tower does not light its lines, and those lines run to the depot too

**Open, in progress since 2026-11-06 in the session "item 347". Filed 2026-11-05 (r1260), from Aria dogfooding 0.4.0 on her own sessions, at her request. Nobody's call — Aria chose the default on 2026-11-06.**

Depends on: nothing
Landed: slice 1 (`0c9768a`, r1266).

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
