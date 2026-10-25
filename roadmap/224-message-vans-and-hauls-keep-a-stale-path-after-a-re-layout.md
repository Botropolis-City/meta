# 224. Message vans and hauls keep a stale path after a re-layout

**Fixed 2026-10-25 (`9898e24`, r1023). Filed 2026-10-24 (r967), found by item 217's audit. Nobody's call — a defect.**

[Item 217](217-a-delivery-truck-drives-beside-the-bridge-not-on-it.md) found that a delivery truck kept driving the path it was given at the merge after the island grew and the bridge moved, and re-routed trucks whenever the city is rebuilt (slice 1, `a555de7`, r967). Its audit of the other movers that store a path at birth found two more with the same shape:
- **Message vans** (`botropolis/pkg/city/messages.go`): `Message.Path` is the road's street path, or the group's line, as it stood when the message was sent, and `From`/`To` point at that city's districts. A re-layout during the drive leaves the van on a road that is no longer there.
- **Pack and unpack hauls** (`botropolis/pkg/city/haul.go`): `Haul.To` is the building's centre when the haul starts, so a second move within `PackFor` (2 s) leaves the truck arriving where the building was.

## The fix

Re-route both the way item 217 re-routes trucks when the scene's city is rebuilt: a van carries on from where it is, along the streets as they now stand, to its districts' current kerbs; a haul retargets its building's current centre. Neither speeds up or jumps.

Tests: for each, when the city is re-laid out mid-trip so the route moves, it should carry on from where it was, and it should end where its target now stands.

## Answered while building

- **The test tree and plan** (manager, 2026-10-25): approved as sent, vans and hauls in one slice. A van is re-routed from where it is along the streets as they now stand to its districts' current kerbs; a haul keeps `Since` and `For`, retargets `To` and solves `From`, so it keeps its speed and arrives on time.
- **A camera turn** (manager, 2026-10-25): included. A turn re-places the streets through `Face` just as a re-layout does, so `face()` re-routes vans and hauls too; and if item 217's trucks go stale on a turn, they join the same call, with a case per mover.

## Closed

Fixed in one slice (`9898e24`, r1023), with its changelog entry under `[Unreleased]`.
Every rebuild, in `apply` after `holdDepot` and in `releaseDepot`, now calls `carryOn`:
- **A van** whose remaining path is no longer the tail of its road as it now stands drives from where it is to the nearest avenue if its own has gone (of those about as near, the one nearer where it is going, so it does not back up), by the avenues to its road, and along it to the recipient's kerb, at `TruckSpeed`.
  Its `From` and `To` become the rebuilt city's districts.
  A carriage carries on to the stations as they now stand, and a van fading in under Still takes the current end.
- **A haul** keeps `Since` and `For`, so its progress, its arrival and the reduced-motion fade are untouched; `To` becomes the building's centre now and `From` is solved so `At(now)` does not move.
  The ease-out is self-similar, so the truck keeps its speed.
  A haul whose building has since gone the other way, packed and unpacked again within `PackFor`, is left alone, so the pack truck still ends at the depot.

Tests: `botropolis/pkg/city/messages_test.go` (a van, a carriage and a Still van, each with the city re-laid out mid-trip by three more sessions in cinders, which moves the road a row) and `botropolis/pkg/city/haul_test.go` (a pack haul whose crate's place in the depot moves mid-haul, and the pack-then-unpack guard).
Each re-layout case was red before the fix; the guard was green before it and stays green, since it is there to stop the fix from sending a pack truck back to the lot.

**Deviations, flagged for Aria:**
- **No unpack case.** A building's lot never moved when the city grew, at one to nine more sessions in each of three districts, because lots are kept; the code retargets an unpack haul the same way, but no fixture can turn that test red.
- **A camera turn re-routes vans, with no test, and hauls and trucks get nothing.** Probed: across all 15 road pairs of the six-district fixture, at every heading, no street path moved, since driveways are kept across turns (item 108) and only the walk's tie-break depends on the heading; building centres and the bridge did not move on any turn either.
  So `face()` re-routes vans, which costs nothing when the road is unchanged and covers a tie-break that does flip, and the manager approved leaving the rest unchanged.
