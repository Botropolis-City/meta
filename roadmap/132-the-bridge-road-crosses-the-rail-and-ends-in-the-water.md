# 132. The bridge road crosses the rail at grade and runs into the water

**Open, in progress since 2026-10-19 in the session "item 132". Filed 2026-10-19 (r678) at Aria's request, from item 78's frame. Nobody's call — Aria decided the design on 2026-10-19.**

Depends on: 134 (slice 1)
Landed: slice 1 (`4f0e7f9`, r707).
Landed: slice 2 (`7387a14`, r710).

Aria, 2026-10-19, passing item 78's train frame (`botropolis/docs/screenshots/r674-item-78-train-hovered.png`):
*"Now that we have a bridge/road leaving the island, we need a solution for when it crosses the train. The easiest is probably to make the train run through a tunnel with a bridge over it and the road on top. Also, The road looks like it just runs into the water. We should make it clearly running on a bridge or find another solution."*

## What is wrong

- **The crossing.** The road to the pull-request bridge (`City.Bridge`, `toBridge` in `botropolis/pkg/city/pullrequests.go`; drawn by `bridgeTile` in `botropolis/pkg/render/iso.go`) crosses item 85's freight loop (`botropolis/pkg/city/trains.go`) on the same level, so a train and a car or the merge truck can occupy the same tile with nothing to say which passes over which.
- **The shore.** Where the road leaves the island it reads as a road running into the sea: nothing shows it is carried on a bridge.

## The fix, as decided (2026-10-19)

The rail stays at ground level and the road goes over it, as in the real world: trains hold 1–2% grades and roads 6% or more, so the road is the one that climbs.
There is no room to ramp between the avenue and the rail, so the bridge starts one cell earlier:

1. **The landing cell becomes the bridge's abutment**, on the island side of the rail, where the road rises onto the deck.
2. **The rail runs under the bridge's first span**, at ground level, the way a coastal line passes under a bridge approach; trains draw beneath the deck, cars and the merge truck on it, and nothing shares a tile at one level.
3. **The deck runs out over the water from there** — piers, railings — so it plainly reads as a bridge, which also answers the road running into the sea.

The deck's clearance over the rail is set by the train's height after item 134 rescales it, which is why this item waits on that one.
A station ending the off-map traffic was considered and set aside: trains are each model's spend, so a pull-request truck ending at a station on the loop would read as riding on one, and driving off the island is how the city shows work leaving the machine.

Art follows `botropolis/design/art-sources.md` (item 123): a licensed pack piece or geometry built in code, never a generated image.

## Tests and frames

- A test that the rail and the bridge road never share a tile at one level: the bridge's first span is over the rail, and the draw order puts the train beneath it.
- A test that the bridge begins at the abutment on the island side of the rail, and that every tile from there out over the water is deck, not road.
- Frames for Aria: the crossing with a train passing under and a car over it, and the shore where the road leaves the island, at the isometric camera's four headings.

## Paused (Aria, 2026-10-19)

Item 132's session measured the crossing — the bridge landing is the westmost avenue cell and the rail's west leg the very next cell, so the road has no room to ramp — and proposed sinking the rail into a cutting under a road overpass.
Aria, on that proposal: *"I was gonna ask if the train could maybe go over the road then, but actually In looking at it, I first think that the proportion between the train and road is off. The train is way too small compared to that road. Is the train just too small, or is that road really big compared to other roads/cars. We should solve this first and then figure out which one runs over or under the other I could also see a world where there is a train station here and then cars and whatever that are supposed to go off the map actually just run to this station. Then we don't need a bridge/road off the map anymore. Pass this over to the design agent to talk and help me decide and pause this in the meantime."*
So the scale of the train against the road comes first, then which crosses which, or a station that ends the off-map traffic and removes the bridge road; the design session takes it with her, and this item is reworked or replaced by what she decides.

## Decided (Aria, 2026-10-19)

The design session measured the scale and recommended: rescale the train (item 134), keep the bridge, road over rail on the bridge's first span from an abutment on the landing cell, no station.
Aria: *"yes do it."*
