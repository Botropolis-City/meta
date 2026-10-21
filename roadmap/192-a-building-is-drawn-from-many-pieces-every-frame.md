# 192. A building is drawn from many pieces every frame, though its look rarely changes

**Open, in progress since 2026-10-21 in the session "item 192". Filed 2026-10-21 (r844) at Aria's request, from the design session's reading of items 156 and 161. Nobody's call — the session proposes the cache key and the night lights.**

Depends on: 191

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
