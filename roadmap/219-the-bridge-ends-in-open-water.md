# 219. The bridge ends in open water

**Open, in progress since 2026-10-24 in the session "item 219". Filed 2026-10-24 (r966) at Aria's request. Nobody's call — Aria chose: the bridge runs off into the haze.**

Aria, 2026-10-24: *"the bridge really does just seem to end in the middle of the water. I initially expected it to statically run off the whole map so it makes sense that things disappear, but that is a very long way to draw the cars driving."*

Today the deck ([item 132](132-the-bridge-road-crosses-the-rail-and-ends-in-the-water.md), [item 146](146-the-bridge-ramp-is-a-solid-wedge.md)) stops a short way out from the coast, and delivery trucks vanish at its far end, so the bridge reads as going nowhere.

## The fix

Run the deck on past where it ends now and fade it into the haze that already softens the island's coast, so it never visibly stops: within a few tiles it is gone into the distance, at every zoom. Trucks fade with the deck as they drive into the haze and are removed once fully faded, so a trip stays short.
Considered and not chosen: the deck drawn all the way to the map's edge (a long drive to animate), a strip of mainland with a depot (a permanent feature at the map's edge). Aria also floated some trucks turning into boats and cruising off the map. Turned down (manager, 2026-10-24, with Aria): boats already carry usage at a glance, so a cargo boat for a merge would blur that signal; it would also need a dock and a hand-off, and still sail a long way off the map. A merge already shows on land (flag, celebration, truck). If a sea departure is ever wanted, it suits a different event, such as a whole project shipping.

Tests: the deck is drawn past its current end and its alpha falls to zero within the haze's band; a truck's alpha follows the deck's at its position and the truck is removed at zero; the minimap and the fitted view frame the island, not the faded deck; frames for Aria at fit and zoomed in, by day and night.

## Answered while building

- **What the "haze" is** (the session "item 219", 2026-10-24): no haze is drawn today; the shore texture blends the shallows into a flat sea colour, and the deck's far end already stands over that flat sea, one cell past the island's reach.
- **How far** (manager, 2026-10-24): `HazeCells` = 3, from Aria's "within a few tiles": the deck runs on 3 cells past its old end (`Bridge.Haze`) to a new `Far`, `Bridge.Alpha` falls linearly from 1 at `Haze` to 0 at `Far`, and trucks fade with it and are removed at `Far`, replacing the last-10% fade.
- **How it fades** (manager, 2026-10-24): by opaque colour, each quarter-cell piece of girder, road, lane line, railing and pier mixed toward the shore palette's sea colour by 1 − Alpha, because a deck at partial alpha shows its overlapping parts through each other. That equals true alpha only over flat sea, so it holds on the condition that nothing else is drawn under the haze span (no boat route, wake or shallows there); the session checks, and a test pins it.
- **The test tree** (manager, 2026-10-24): approved as sent, `TestBridgeIntoTheHaze` in `pkg/city` and `TestDeckIntoTheHaze` in `pkg/render`, with one more case: nothing but flat sea is drawn under the haze span. Frames for Aria at fit and zoomed in, by day and night, with a truck in the haze.
