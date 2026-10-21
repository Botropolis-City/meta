# 193. A still city is redrawn whole every frame; only what moves should be

**Open. Filed 2026-10-21 (r844) at Aria's request, from the design session's reading of items 156 and 161. Nobody's call — the approach is set; the session proposes the occlusion detail.**

Depends on: 192

## What is wrong

Only the ground is cached (`staticCity` and `composeStatic`, `pkg/render/static.go`).
Every building, tree, lamp, landmark, monument and sign is made into a closure and depth-sorted every frame (`drawIso`, `pkg/render/iso.go`; `layered`, `pkg/render/drones.go`), on screen or not.
0.1.7 drew at 10–21 ms a frame with half of today's vector calls, so removing those (item 191) will not reach the 10 ms budget alone: drawing everything every frame is the floor.
The benchmark also counted 175 render-target switches a frame, from the hover fade layer (`fadeUnkept`, `fadeAll`), the night lights' cut-outs and the kit pages as separate textures; that is a second, smaller lever this item takes on.

## The fix

1. **The standing city goes into the cached layer**: buildings (item 192's images), trees, lamps, landmarks, monuments and signs, composed again when the layer's key changes (camera, view, night, hover) or a building's look changes.
   Each frame is then one copy of the layer plus the movers: cars, drones, trains, boats, tugs, hauls, messages, couriers.
2. **Occlusion.** A mover behind a standing object must stay behind it.
   First approach: redraw over each mover the cached objects that overlap it and stand in front of it, in depth order, as OpenTTD redraws only its dirty rectangles; movers are few.
   Only if that measures too slow: a depth image beside the layer and a shader that hides a mover's pixels behind it, as Pillars of Eternity sets 3D characters into pre-rendered scenes.
3. **Cull and stop allocating.** Skip anything off screen before sorting; reuse the draw list instead of a closure per item per frame; cache each label's rendered text.
4. **Hit testing** keeps working by replaying the layer's hits, as `static.hits` already does.
5. **Fewer target switches**: draw the hover fade and the night lights so they switch targets once a frame, not per object.

## Judged by

Item 194's counts, which should stop growing with the number of buildings, and frames to Aria of movers passing behind buildings, by day and night.

**This item does not close while any target case in `TestTheWorkAFrameTakes` still skips** (item 194; the roadmap manager, 2026-10-21).
Each of 191, 192 and 193 lowers that test's ceilings to what it reached; this one also adds its case that the metropolis costs no more than 1.25× the hamlet.
