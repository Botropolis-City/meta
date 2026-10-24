# 217. A delivery truck can leave the island beside the bridge instead of on it

**Fixed 2026-10-24 (`a555de7`, r967). Filed 2026-10-24 (r966) at Aria's request, from the 0.3.0 website clip "A day on two projects". Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`a555de7`, r967).

Aria, 2026-10-24: *"in the video of a day on two projects, the green car leaves the screen not on the bridge"*.

**What the clip shows** (`botropolis/dist/demo/timelapse/day.mp4`, filmed 2026-10-23 from v0.3.0; the same clip is on botropolis.city):
- **The first merge (scenario `timelapse`, at 24 s): wrong.** The green delivery truck leaves the island running parallel to the bridge along its north side, over the shore and then the water, never on the deck. Reproduce with `ffmpeg -ss 28 -i day.mp4 -t 4 -vf "fps=2,crop=520:300:250:350,tile=4x2"`: the truck is at roughly (455,105) → (420,75) → (325,25) in successive frames of that crop, above the deck rather than on it, until the camera pans away at 32 s.
- **The second merge (at 46 s): right.** That truck drives onto the ramp and along the deck (`-ss 47 -t 7`, crop `900:520:200:280`).
So the route is not wrong every time, which rules out the bridge's geometry alone.

**Where it is.** `City.toBridge` (`botropolis/pkg/city/pullrequests.go`) builds the truck's path: the building's kerb, its driveway, the avenues from `walkStreets` to `bridgeCell`, then `bridge.Land` and `bridge.Far`. `render.deliveryAt` (`pkg/render/bridge.go`) raises it onto the deck only while `Bridge.Rise(at) > 0`. Candidates to check first:
- the keep-to-the-right lane offset from [item 153](153-cars-keep-to-the-right.md), applied on the bridge stretch where the deck is narrower than an avenue, or from a different heading when the last avenue cell meets `bridge.Land` at an angle (the two trucks start in different districts, kiln and tidepool, so they reach `bridgeCell` differently);
- a truck drawn at ground level while the deck is raised ([item 132](132-the-bridge-road-crosses-the-rail-and-ends-in-the-water.md)'s ramp), which on screen sits beside the deck rather than on it;
- the path's last avenue cell not being the bridge's landing cell, so the final leg cuts across.

## The fix

Find which of these it is from the first truck's actual path and drawn position, then keep every truck on the deck from the landing to the far end, at every heading.

Tests: for a truck leaving from each district of a city, every point of its path from `bridge.Land` on lies within the deck's width, and its drawn position is raised by the deck's rise wherever `Rise > 0`; a frame of both of the timelapse's trucks on the bridge for Aria.

## What it was

None of the three candidates.
The bridge moved under a truck already on its way.
Replaying `timelapse.yaml` through `city.Scene` from the staged corpus, logging `Bridge()` and each delivery's path every second, the landing moved from y=456 to y=504 when an arrival grew the island by a row.
A delivery's path is laid once, at the merge, while `bridgeCell` is the middlemost coastal street and is recomputed every frame,
so a truck that merged before the growth drove the old row: one row north of the drawn deck, over the shore and then the water.
In film time the growth landed during the first truck's trip, and the second truck merged after it.
The lane offset stays inside the one-cell deck, and `Rise` raises a truck correctly once it is on the current deck.

**Slice 1** (`a555de7`): every rebuild re-routes a truck whose path no longer ends on the bridge as it stands.
Short of the old landing, it drives on to the first avenue ahead and by the avenues to the new landing.
Already out on the old deck, it moves across to the same distance out on the new one, a jump of one row,
which the manager approved over a truck driving where no deck is drawn.
[Item 218](218-the-bridge-moves-when-the-island-grows.md) anchors the bridge, which makes that jump rare; the re-route stays as the safety net for when an anchored bridge still has to move.
Tests: `pkg/city/pullrequests_test.go` (each district's path within the deck's width; a bridge that moves before and after the truck reaches the landing), and `pkg/render/delivery_deck_test.go` (the drawn truck at the deck's full height past the ramp, including across a move), which fails with the re-route switched off.

**The same stale-path shape, elsewhere**, checked at the manager's request:
couriers and tugs already refresh their ends from the live river (bug 54a), drones keep only a seat, and inspectors are computed from the live building.
Two movers still store world points at birth and are not the same few lines, so they are left for filing:
- **message vans** (`pkg/city/messages.go`): `Message.Path` is the road's street path, or the group's line, when the message is sent, and `From`/`To` point at that city's districts; a re-layout during the drive leaves the van on the old road;
- **pack and unpack hauls** (`pkg/city/haul.go`): `Haul.To` is the building's centre at the haul's start, so a second move within `PackFor` (2 s) leaves the truck arriving where the building was.

The first `make land` failed only on `pkg/daemon`'s `TestThreadCPU` ("15.92ms is not greater than or equal to 25ms" for a 100 ms spin), at a load average of about 11; the second passed unchanged.

## Closed

Fixed by slice 1 (`a555de7`, r967), with its changelog entry under `[Unreleased]`.
Aria judged the frames on 2026-10-24: *"Approve and close"*.
They come from a fresh film of the timelapse at `a555de7`, kept git-ignored at `botropolis/dist/item-217/`: `first-truck-29s-to-33s.png` and `second-truck-47s-to-53s.png`, both trucks up the ramp and along the deck to the far end.
Whether the bridge moved during the first trip in that film cannot be told from the frames; the tests above cover that case directly.
**The website's timelapse clip was re-filmed from `a555de7` at Aria's request** and deployed the same day (botropolis.city `59b6a0f`); only that clip changed.
Left for others: items 218 (anchor the bridge), 224 (message vans and hauls keep a stale path) and 225 (`TestThreadCPU` under load).
