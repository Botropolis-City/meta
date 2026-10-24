# 219. The bridge ends in open water

**Open. Filed 2026-10-24 (r966) at Aria's request. Nobody's call — Aria chose: the bridge runs off into the haze.**

Aria, 2026-10-24: *"the bridge really does just seem to end in the middle of the water. I initially expected it to statically run off the whole map so it makes sense that things disappear, but that is a very long way to draw the cars driving."*

Today the deck ([item 132](132-the-bridge-road-crosses-the-rail-and-ends-in-the-water.md), [item 146](146-the-bridge-ramp-is-a-solid-wedge.md)) stops a short way out from the coast, and delivery trucks vanish at its far end, so the bridge reads as going nowhere.

## The fix

Run the deck on past where it ends now and fade it into the haze that already softens the island's coast, so it never visibly stops: within a few tiles it is gone into the distance, at every zoom. Trucks fade with the deck as they drive into the haze and are removed once fully faded, so a trip stays short.
Considered and not chosen: the deck drawn all the way to the map's edge (a long drive to animate), a strip of mainland with a depot (a permanent feature at the map's edge). Aria also floated some trucks turning into boats and cruising off the map, noting the same distance problem; if boats want the same ending, the haze is it.

Tests: the deck is drawn past its current end and its alpha falls to zero within the haze's band; a truck's alpha follows the deck's at its position and the truck is removed at zero; the minimap and the fitted view frame the island, not the faded deck; frames for Aria at fit and zoomed in, by day and night.
