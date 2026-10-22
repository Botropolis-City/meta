# 193. A still city is redrawn whole every frame; only what moves should be

**Done 2026-10-21 (`e54a875`, r870). Filed 2026-10-21 (r844) at Aria's request, from the design session's reading of items 156 and 161. Nobody's call — the approach is set; the session proposes the occlusion detail.**

Depends on: 192
Landed: slice 1 (`b8f2f33`, r863).
Landed: slice 2 (`a58bb78`, r868).
Landed: slice 3 (`e54a875`, r870).

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

## How it is being built (2026-10-21)

**Measured first**, the metropolis at 1600×900, settled, by day at r862: 131 commands and 34,002 indices.
The group lines are 20,520 of those indices, in one run drawn after the sort, and the whole sorted list is 7,374: the bridge 3,300, trees 1,794, the plant's stack 1,542, buildings 528 and movers about 200.
Chrome text is about 5,000 and map labels 1,104.
By night it is 188 commands, and the 57 extra are the lights laid one op at a time.
The hamlet is 69 commands and 10,644 indices.
Render-target switches already meet their target (6 and 8 against 30), so fix 5 is confirmed, not rebuilt.

The design, approved by the roadmap manager for Aria:

- **A dry pass.** Every drawable runs each frame exactly as before, onto a stand-in destination: each raw draw skips the GPU and instead widens the drawable's screen box and hashes what it would have drawn (source, transform, colour, vertices, words).
  Every side effect — hits in depth order, the night's light ops, words seen, boards signed, looks baked — happens there, once, as before, so hit testing needs no replay.
- **Still or moving, by kind.** Cars, drones and their shadows, trains, boats, tugs, hauls, messages, couriers, inspectors, deliveries, ribbons, the fountain, power-line sparks, overgrowth and a building with a live step this frame move; everything else is still.
  The still layer's key is the ground layer's key and the hash of every still's dry draws in order, so it is composed again exactly when something still would paint differently.
  This supersedes the list in the fix ("camera, view, night, hover, or a building's look"), and is strictly more complete: there is no hand-kept signature to go stale.
- **Composing**: the ground and every still drawn into one image, in depth order. A settled frame is one blit of it.
- **Occlusion by dirty rectangles, replayed exactly.** Each mover's box is merged into rectangles; in each, the ground is copied back and every drawable whose box meets it, still or moving, is drawn again in the frame's order, clipped to the rectangle, so inside it the same draws land in the same order.
  A clipped destination is a scissor in Ebitengine 2.10, and draws to different regions merge into one command.
  Two approaches were rejected.
  Redrawing only the occluders in front over the mover double-blends their soft edges, by up to about 64 levels.
  A depth image and a shader cannot hold the pairwise order a scalar depth cannot encode (bug 42), and drop soft edges.
- **Night**: the stills' light ops are laid once into a lights image of their own; each frame it is copied, and inside each rectangle cleared and laid again from the ops of the drawables in it.
- **The hover fade** works the same in composing and in replay, its layer sized to the frame.
- **Group lines are part of the standing city** (the roadmap manager): a layer of their own over the movers, keyed by their dry hash. A line that animates would be a mover, and the session says which and what it costs.
- **Slices**: 1, all of the above with the ceilings lowered; 2, culling off-screen drawables before the sort, reusing the draw list and caching label text; 3, only if needed, the hamlet comparison and what is left.
- **Reported, not gated**: a benchmark of the dry pass's time and allocations on the settled metropolis against the draw it replaces, since the budget is 10 ms of CPU and item 194's counts do not see CPU; if hashing costs more than the submission it saves, the session says so before slice 2. Also the layers' memory at 1600×900 and in a 4K window against the 512 MiB budget, and the panning numbers, as 192 reported them.
- **The identity check** compares each frame with the still layer off and on, within 192's tolerance of 3.

Tests: `TestInk`, `TestDirtyRects`, `TestStillLayer` and `TestRawDrawSites` (a source guard on the parsed calls) in `pkg/render`; `botropolis-demo sheet --check-frames` (`TestTheStillCityMatchesTheCityDrawnDirectly`) over 60 frames by day and by night, with a car hovered, a view up and a building selected, and a mover passing behind a building; `TestTheStillLayerAFrameKeeps`; item 194's ceilings lowered and its 1.25× case added.

## Slice 2 (2026-10-21)

Slice 1 landed at r863; Aria approved its frames (`botropolis/docs/screenshots/r863-item-193-*.png`, landed at r864).
It measured a settled frame by phase, metropolis against hamlet, in commands: movers drawn again 43 against 17, map labels 2 against 2 (1,608 indices against 300), chrome 15 against 9, and by night the lights laid again 49 against 9.

The plan, approved by the roadmap manager:

- **A whole-pixel pan shifts the layers** — ground, still city, its lights, group lines — and composes only the strips it exposes; positions are hashed relative to the camera's origin, so a whole-pixel move leaves every hash as it was.
- **The rectangles of movers are played as one stream**, in the frame's order, so draws from one source merge across them; the night's lights the same.
- **Each map label is cached as one image.**
- **Chrome must stop growing with the city too** (the roadmap manager, for Aria): not by leaving it out of the comparison, since a target is never loosened quietly. First, draw the status dots in one pass and the text in another, which is exact; or cache the panel. Only if neither suffices, nearest-filtered dots with a crop to Aria.
- Culling and reusing the draw list, reported by the benchmark.

Tests: `TestStillShift`, `TestDirtyStream` and `TestLabelCache`; the frame check's variant panning a pixel a frame; *when the camera pans with an arrow held, it should compose only strips*, reporting the pan's counts against the targets.

**Aria, 2026-10-21, on the 1.25× ratio** (with movers about 20 draw calls in the metropolis against 5 in the hamlet after slice 2): *"Hold movers equal."* The ratio compares the two cities with the same activity: the standing city must not grow with the size of the city, and more activity may cost more. The absolute targets still gate with movers as they are. She also approved the r867 night before/after.

Slice 2 landed at r868: by day 34 commands and 5,232 indices, by night 51 and 6,084, a held arrow's pan 41 and 7,302, every absolute target met.
Against r862 from the same staged moment no pixel differs by more than 3 levels by night or 2 by day, and Aria approved that frame (`botropolis/docs/screenshots/r867-item-193-night-before-after.png`, 2026-10-21).

**Hold movers equal** (Aria, 2026-10-21, quoted as she ruled it): what was left over 1.25× the hamlet was the movers themselves — the metropolis has twice the activity — so the comparison holds the movers equal and is named for it, *when the hamlet and the metropolis have the same movers, it should cost the metropolis no more than 1.25× the hamlet*; the absolute targets go on gating with every mover drawn.
And the switches over the hamlet's in the counted window are Ebitengine moving item 192's freshly baked looks onto its atlas, so slice 3 puts the looks on pages of their own, as slice 2 did the labels (the roadmap manager, 2026-10-21: removing the cause rather than moving the window).

## Closed (2026-10-21)

Done at `e54a875` (r870), in three slices (r863, r868, r870).
Every drawable is recorded in a dry pass; the ground and the still city are composed once, and composed again only where something still would paint differently; what moves is drawn again from the ground up inside rectangles, the same draws in the same order, so a mover behind a building stays behind it.
A whole-pixel pan shifts the layers and composes the strips it uncovers; the rectangles of movers are played as one stream, batched by source; map labels are baked onto a page of their own and go down with the group lines' layer; building looks are baked onto pages of their own.

| the metropolis at 1600×900, a frame | r862 | item 193 |
| --- | --- | --- |
| settled by day: commands, indices, switches | 131–136, 34,000–53,800, 4–5 | 22, 4,890, 2 |
| settled by night | 188–210, 37,300–57,000, 7 | 40, 5,742, 4 |
| a held arrow's pan | 138, 54,500 | 29, 5,688 |

**Every target case in `TestTheWorkAFrameTakes` gates, none skipping**: the absolute targets with every mover drawn, and *when the hamlet and the metropolis are drawn with the same movers, none: no travellers and no building animating, it should cost the metropolis no more than 1.25× the hamlet* — Aria's ruling, in the words she chose (2026-10-21): *"compare the two cities with the same activity: the still city must not grow with size; more activity may cost more"*, recorded as "Hold movers equal". A pulsing beacon, a scaffold or smoke is a session at work, so it is activity and left out in both (the roadmap manager, confirming); the fountain stays.
With the same activity the two cities cost the same: 9 commands each by day and 14 by night, indices within 5%.

`botropolis-demo sheet --check-frames` (`TestTheStillCityMatchesTheCityDrawnDirectly`) holds every frame within 3 levels of the city drawn straight, by day and by night, as it stands, with a building selected, with traffic and a car hovered, with a view up, and panning by whole and by part of a pixel; each of its mechanisms was mutated and caught.
`TestRawDrawSites` holds every draw to the record or a listed reason; `TestTheStillLayerAFrameKeeps` gates that a settled frame composes nothing and a held arrow's pan only strips.
Aria approved the frames (`botropolis/docs/screenshots/r863-item-193-*.png`) and the city against r862 by night from the same staged moment, no pixel more than 3 levels apart (`r867-item-193-night-before-after.png`).
The CPU of a driven frame fell from 3.05 ms to 2.14 by day and 3.74 to 2.70 by night, with half the allocations (`BenchmarkTheStandingCity`, reported).

Deviations, each agreed with the roadmap manager or recorded here:

- **Fix 2 replays the record, not the drawables**, so nothing a drawable notes can happen twice; and the ground is recorded too, so a snapshot that changes nothing composes nothing.
- **Fix 3**: label text is cached; culling off-screen drawables before the sort was not done, since the dry pass already costs less CPU than the drawing it replaced and no target needed it. A closure per drawable per frame remains; the record reuses its buffers.
- **Fix 5** was already met by items 192 and 195 (6 and 8 switches against 30); slice 2 also stopped clearing the faded labels' layer every frame.
- **Every layer the frame's size has its own texture**: on Ebitengine's shared atlas a cut laid onto the still lights left a lit pixel dark, and the ground lost a rail's end pixel.
- **A cut meets the pixel a pane's light spreads into**, so where it lands no longer depends on what other windows are laid.
- **Item 192's looks are baked onto pages of their own** (the roadmap manager: removing the cause of the switches over the hamlet's, not moving the counted window); a full page starts again only at the next frame.
- **`TestDrive` no longer compares the sprites a frame draws**: a look baking two ticks in took the hamlet from 166 to 165, which had blocked every landing.
- It holds about 30 MB more at 1600×900, and about 135 MB in a 4K window, against the 512 MiB budget.
