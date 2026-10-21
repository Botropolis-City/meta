# 192. A building is drawn from many pieces every frame, though its look rarely changes

**Done 2026-10-21 (`1b004a9`, r861). Filed 2026-10-21 (r844) at Aria's request, from the design session's reading of items 156 and 161. Nobody's call — the session proposed the cache key and the night lights.**

Depends on: 191
Landed: slice 1 (`1b004a9`, r861).

## What is wrong

Each frame, `isoBuilding` and its follow-ups (`drawSkip`, `drawWork`, `drawSpire`, the facade, the sign, lit windows) draw a building from its kit sprite plus every overlay, although what a building looks like changes only when its storeys, scaffold stage, heading, zoom, night, lit state, sign or tint change.

## The fix

Composite each building's look once into one small image, keyed by everything that changes it, and draw that image each frame; bake it again when the key changes.
Parts that animate (a blinking beacon, the hoist, smoke) stay as item 191's stamps drawn on top.
The cache is capped in bytes with least-recently-used eviction, its cap taken from the city's memory budget (`performance/budgets.md`), so memory grows with the city on screen, never with every possible variant.
Small managed images share Ebitengine's atlas, so cached buildings batch with each other and with the stamps.

The night lights (`beginLights`, `punch`, `endLights` in `pkg/render/windows.go`) must keep cutting out lights behind a building; the session proposes how before building.

## Judged by

Item 194's counts, and frames to Aria by day and night at fit and up close, identical to before.

## How it is being built (2026-10-21)

The design, approved by the roadmap manager for Aria:

- **Steps and runs.** A building's drawing is an ordered list of steps in today's paint order: courses, sprite, construction site, shutter or put-out, its own lights noted, beacon, sign, flags, celebration, smoke, selected outline, skip, scaffold, spire.
  Each step is static or live this frame, and each run of consecutive static steps is baked into one image, with live steps drawn directly between them.
  A still building is one image; a pulsing beacon makes two, either side of it.
  So the paint order stays exactly as it was, which matters because the beacon, sign and scaffold overlap.
- **Live** is anything that moves: rising, a haul's fade, settling, a construction site, a course pouring, a pulsing beacon, a flag being hoisted, a celebration, smoke, the hoist's loads and its work lights' flash, and trucks at the skip.
- **Baking** runs today's drawing code into an offscreen image through a camera shifted by a whole number of pixels, and blits it back at that offset, so the sub-pixel phase holds and nothing is filtered twice.
  Hit rects, the badge queue and the words seen are still noted in screen space every frame.
- **The key** is the session, the piece, the heading, the zoom, the foot's sub-pixel phase, the tint, whether the view recedes it, and each static step's own inputs.
  Panning by whole pixels keeps it.
  A key is baked only once it has held for two frames, so zooming and continuous motion draw directly, as before, instead of baking every frame.
- **The cache** is least-recently-used and capped at 32 MiB of image bytes, a sixteenth of the city's 512 MiB settled budget; eviction deallocates.
  The session reports the metropolis's baked bytes at fit and three notches in, and hits and misses a frame once settled; if close zoom wants more than the cap, it says so rather than thrash.
- **Night lights** stay out of the cache, since they are laid after the night wash.
  Each baked image cuts the lights behind it where its steps did, as the sprite does today.
  Overlays after a building's own lights (its sign, scaffold, spire, flags) now cut them too, which item 195 brings in for everything in the depth sort and Aria ruled is right: signs go in front of lit windows.
  The identity check excludes those steps' pixels, and the frame notes name the change.
  The cache builds on item 195's cuts once they land, painting a bake with the cut-noting switched off and punching the finished image instead.

Tests: `TestLookCache`, `TestLookCacheCap`, `TestLookKey` and `TestBuildingSteps` in `pkg/render`; `TestBuildingLooksCached` through `botropolis-demo sheet --check-looks`, and the existing lights checks run with the cache on; item 194's ceilings lowered, and *when the metropolis has settled at fit, and up close, it should bake nothing*.

## Closed (2026-10-21)

Done at `1b004a9` (r861): each building is drawn as steps in its paint order, each still run of them baked once into an image of its own and blitted after, through a 32 MiB least-recently-used cache.
`botropolis-demo sheet --check-looks` (`TestBuildingLooksCached`) holds every look, from every heading at zoom 1 and 2, by day and by night, to the building drawn directly, as first seen, baked, kept and changed; `TestTheLooksAFrameKeeps` gates that a settled metropolis bakes nothing at fit and three notches in.
Aria judged the frames (`botropolis/docs/screenshots/r861-item-192-*.png`, landed at r862) and approved them, the hoist column included.

**Item 194's counts**, the metropolis at 1600×900, worst settled frame, day / night:

| per frame | item 191 | item 192 |
| --- | --- | --- |
| indices | 75,504 / 78,570 | 34,008–53,772 / 37,290–57,012 |
| draw commands | 277 / 334 | 131–136 / 188–210 |
| render-target switches | 5 / 7 | 4–5 / 7 |

Indices are bimodal: a mover's frame in the window adds about 20,000, with no cache miss in it.
The ceilings came down to 54,900 / 58,200 indices and 139 / 215 commands.
The cache keeps 0.3 MiB at fit and 2.3 MiB three notches in.

**For item 193, the moving camera**, reported and not gated (the roadmap manager, 2026-10-21): a pan by a held arrow keeps every look, 30 hits and no bakes a frame.
A wheel zoom draws every building straight while it moves, as before this item, since a look is baked only once its key has held a frame; the frame after it stops bakes all 30 at once, about 430 commands, 86,000 indices and 58 switches, and about ten frames later Ebitengine moves each new look onto its atlas, one copy each, which is why item 194's test now counts from frame 20.

Deviations, each agreed with the manager or recorded here:

- At night a baked look cuts the lights behind it at its own alpha, where item 195 cuts a line as a bar a pixel wider, so beside a hoist line one more column of light shows; the night identity check leaves out what a building paints after its own lights.
- Three float ties made a scaffold's lamps, braces and hoist change corners with the camera's rounding, so a pan could flip them; each now treats heights within half a pixel as equal.
- `buildingItem` went: the work is a building's own steps, in its one place in the depth sort.
- `TestDrive` no longer compares how many sprites cut the lights, which settles as the looks bake.
- The see-through night check stands its buildings on whole pixels: off the grid, its notion of a solid pixel took in a soft edge.
