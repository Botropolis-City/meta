# 132. The bridge road crosses the rail at grade and runs into the water

**Open, in progress since 2026-10-19 in the session "item 132". Filed 2026-10-19 (r678) at Aria's request, from item 78's frame. Nobody's call.**

Depends on: nothing

Aria, 2026-10-19, passing item 78's train frame (`botropolis/docs/screenshots/r674-item-78-train-hovered.png`):
*"Now that we have a bridge/road leaving the island, we need a solution for when it crosses the train. The easiest is probably to make the train run through a tunnel with a bridge over it and the road on top. Also, The road looks like it just runs into the water. We should make it clearly running on a bridge or find another solution."*

## What is wrong

- **The crossing.** The road to the pull-request bridge (`City.Bridge`, `toBridge` in `botropolis/pkg/city/pullrequests.go`; drawn by `bridgeTile` in `botropolis/pkg/render/iso.go`) crosses item 85's freight loop (`botropolis/pkg/city/trains.go`) on the same level, so a train and a car or the merge truck can occupy the same tile with nothing to say which passes over which.
- **The shore.** Where the road leaves the island it reads as a road running into the sea: nothing shows it is carried on a bridge.

## The fix, as Aria suggested

1. **Grade separation**: where the bridge road meets the rail, the rail goes through a short tunnel or cutting and the road crosses on an overpass above it; trains draw under it, cars and trucks over it, and neither ever shares the tile at one level.
2. **A bridge that reads as one**: from the shoreline out, the road is carried on a visible deck — piers, railings or an abutment where it leaves land — so it is plainly a bridge; another solution that reads as clearly is fine, proposed with a frame.

Art follows `botropolis/design/art-sources.md` (item 123): a licensed pack piece or geometry built in code, never a generated image.

## Tests and frames

- A test that the rail and the bridge road never share a tile at one level: where their paths cross, the crossing is an overpass, and the draw order puts the train beneath it.
- A test that the road's tiles over water are bridge deck, not road.
- Frames for Aria: the crossing with a train passing under and a car over it, and the shore where the road leaves the island, at the isometric camera's four headings.
