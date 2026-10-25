# 224. Message vans and hauls keep a stale path after a re-layout

**Open, in progress since 2026-10-25 in the session "item 224". Filed 2026-10-24 (r967), found by item 217's audit. Nobody's call — a defect.**

[Item 217](217-a-delivery-truck-drives-beside-the-bridge-not-on-it.md) found that a delivery truck kept driving the path it was given at the merge after the island grew and the bridge moved, and re-routed trucks whenever the city is rebuilt (slice 1, `a555de7`, r967). Its audit of the other movers that store a path at birth found two more with the same shape:
- **Message vans** (`botropolis/pkg/city/messages.go`): `Message.Path` is the road's street path, or the group's line, as it stood when the message was sent, and `From`/`To` point at that city's districts. A re-layout during the drive leaves the van on a road that is no longer there.
- **Pack and unpack hauls** (`botropolis/pkg/city/haul.go`): `Haul.To` is the building's centre when the haul starts, so a second move within `PackFor` (2 s) leaves the truck arriving where the building was.

## The fix

Re-route both the way item 217 re-routes trucks when the scene's city is rebuilt: a van carries on from where it is, along the streets as they now stand, to its districts' current kerbs; a haul retargets its building's current centre. Neither speeds up or jumps.

Tests: for each, when the city is re-laid out mid-trip so the route moves, it should carry on from where it was, and it should end where its target now stands.

## Answered while building

- **The test tree and plan** (manager, 2026-10-25): approved as sent, vans and hauls in one slice. A van is re-routed from where it is along the streets as they now stand to its districts' current kerbs; a haul keeps `Since` and `For`, retargets `To` and solves `From`, so it keeps its speed and arrives on time.
- **A camera turn** (manager, 2026-10-25): included. A turn re-places the streets through `Face` just as a re-layout does, so `face()` re-routes vans and hauls too; and if item 217's trucks go stale on a turn, they join the same call, with a case per mover.
