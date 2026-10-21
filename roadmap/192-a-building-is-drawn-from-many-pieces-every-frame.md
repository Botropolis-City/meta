# 192. A building is drawn from many pieces every frame, though its look rarely changes

**Open. Filed 2026-10-21 (r844) at Aria's request, from the design session's reading of items 156 and 161. Nobody's call — the session proposes the cache key and the night lights.**

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
