# 347. Pointing at a water tower does not light its lines, and those lines run to the depot too

**Open. Filed 2026-11-05 (r1260), from Aria dogfooding 0.4.0 on her own sessions, at her request. Nobody's call on the first part; Aria's call on the second part's default.**

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

**Aria's call: the default.**
The recommendation is buildings only, since packing a session is saying it is finished with, and a tower's lines are most useful for what is still on the map.

## Tests

- In `pkg/city`: when a tower is pointed at, its beams should be in the highlight and the others should not.
- When the setting is off, there should be no beam to a crate in the depot, and when it is on, there should be.
- A frame of Servers with a tower pointed at, for Aria to judge.
