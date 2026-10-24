# 162. The city holds gigabytes of GPU memory, which on integrated graphics is system RAM

**Open, in progress since 2026-10-24 in the session "item 162". Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the city memory budgets Aria set the same day. Nobody's call — the budget is set.**

Depends on: nothing
Landed: slice 1 (`b2ec8b6`, r886).
Landed: slice 2 (`c47a2a3`, r884).
Landed: slice 3 (`d100abf`, r889).
Landed: slice 4 (`e6bde10`, r905).
Landed: slice 5 (`23ec6fa`, r908).
Landed: slice 6 (`66116ad`, r914).
Landed: slice 9 (`834af3c`, r957).
Landed: slice 10 (`c423817`, r960).
Landed: slice 11 (`29da884`, r962).
Landed: slice 13 (`d844660`, r968).
Landed: slice 14 (`cc2cd0c`, r976).

On integrated graphics, textures and buffers come out of system RAM and appear in no RSS or `Private_Dirty` figure; `perf-sample` reads them as `drm-total-*` from the DRM fdinfo.
The reference machine (budgets.md) is integrated graphics, so this is memory the user's laptop does not have.

| rig | build | GPU MiB settled | GPU MiB peak | own + GPU settled | report |
| --- | --- | --- | --- | --- | --- |
| Core Ultra 7 255H, Intel Arc (i915) | 0.1.7 | 939 | — | ~1.15 GB | [laptop](../performance/reports/2026-10-19-laptop-igpu-0.2.2.md) |
| Core Ultra 7 255H, Intel Arc (i915) | 0.2.2 | 1,920–3,002 | — | 4.5–7 GB | laptop |
| Core Ultra 7 265U, Arrow Lake-U (i915) | 0.2.2 | 988 | 1,659 | 1.94 GB | [265U](../performance/reports/2026-10-19-ultra7-265u-igpu-0.2.2.md) |
| Core Ultra 7 265U, Arrow Lake-U (i915) | r780 | 668 | 734 | 1.96 GB | 265U |

**0.1.7's 0.9 GB is itself far over budget**, so this is not only a regression: reverting would not meet it.

**What is resident**: `pkg/render/kits.go` keeps all eight kit pages of both zoom levels on the GPU whatever the zoom, each its own 2048-pixel unmanaged texture since item 70 (r765) — 128 MiB of RGBA before anything else is drawn, and more once the driver adds mipmaps or padding.
The rest is Ebitengine's offscreen images (the static layer, the shore texture sized to the island, item 85 slice 3), the window's framebuffers, and the vertex buffers the draw-command queue fills (item 156).
No one has broken the figure down yet.

**The budgets it breaks** ([budgets.md](../performance/budgets.md), *City*): **≤ 512 MiB `Private_Dirty` + GPU together**, settled with the window open, and **≤ 1 GB at any moment of start-up**.

## The fix

1. Break the GPU figure down: count every live `ebiten.Image` by size and purpose at a settled moment (a debug key, or a test through `render.NewDrive`), and compare with `drm-total-system0`.
2. Keep resident only the kit pages of the zoom in use, and load the other level's on a zoom change, a page at a time, as item 70 already does at start-up.
3. Size offscreen layers to the window, not the island, and drop what a hidden window does not need (item 163).

Tests: a measure test that counts the bytes of live images in a settled demo city, whose limit is the budget's share for textures; judge on the real display with `perf-city`, quoting `gpu_mib` with the GPU named.

**Re-measured after items 191–195** (265U iGPU, `458454f`, r871, [report](../performance/reports/2026-10-21-ultra7-265u-igpu-r871.md)): GPU alone is down to 196–331 MiB (0.2.2: 1,265–1,669), but **own plus GPU settled is 715–817 MiB against 512**. At 60 s, 96 MB of the heap is kit-page pixels kept after upload (`kits.uploadNext` → Ebitengine's `bytesPool`), and 51 MB is HarfBuzz shaping for the group-review panel.

**What it was, and what landed** (2026-10-22).
The 96 MB was not the pool: Ebitengine keeps an image's written pixels on the CPU until the image is first drawn from, and z2 is drawn only from zoom 1.98, so its six pages stayed on the heap whole.
Slice 1 draws a pixel from each page as it goes up, and sends pages in 64-row strips so the pool keeps at most 31 × 512 KiB; a test fails when the build's Ebitengine is not v2.10.2, which those facts were read from.
Slice 2 clips text by doubling and halving a prefix, memoised, so the group-review panel no longer fills the shaping cache with near-whole rows.
Slice 3 keeps resident only the kit level the camera picks, puts the other up a page an update on a zoom across the threshold, and lets a level go after 300 updates unpicked.
Slice 4 is the guard the Tests line asks for, made whole instead of partial (the roadmap manager, 2026-10-22): a sum of the city's own images would miss Ebitengine's, which is where the 96 MB hid, so `TestSettledMemory` gates a settled metropolis under Xvfb, where the software renderer's textures are the process's own memory, at 512 MiB of `Private_Dirty`.
On the way, the night draw-command ceiling went to main's own worst, 42, and frame work is counted from the city's first drawn frame.

**Measured after slices 1–3** (265U iGPU, `d100abf`, r889, [report](../performance/reports/2026-10-22-ultra7-265u-igpu-item-162.md)), on the metropolis demo at fit: **own plus GPU settled 355 MiB** (76 own, 279 GPU), against 689 at r871 (310 and 379); Go heap live 24 MB against 141; under Xvfb 250 MiB against 528.
**Owed:** the same on the real history, where the budget is set, through a scratch daemon on a copy of the state directory; and at full zoom. Both need a focused window, and the desk was in use, so the roadmap manager is having them run with items 161 and 163's re-measure.

**Measured on the real history at r905** (`e6bde10`, [report](../performance/reports/2026-10-22-ultra7-265u-igpu-r905.md)): **met at fit**, 398–400 MiB own plus GPU (r871: 715–817); **not at full zoom**, 618–620 MiB, about 110 over 512. The metropolis meets both (342 and 481).

**What full zoom added, and slices 5–7** (2026-10-22). A census under Xvfb at r905 (Ebitengine's own image total, `ReadDebugInfo`, beside the heap) found the full-zoom rise on the real history in three places: kit textures, 2 pages to z2's 6; eight look pages, 32 MiB, made at full zoom and never let go, so a city that had zoomed in once stayed heavier at fit; and the Go heap held from the OS, 113 to 226 MiB, 23 MB of it Ebitengine's upload pool.
Slice 5 lets the look cache go whole once nothing has been drawn from it for 600 frames.
Slice 6 decodes each kit page only as tall as its lowest sprite (z2's last page uses 701 of its 2,048 rows, z1's 943) and sends pages in 8-row strips, so the pool keeps under 2 MiB.
At r914 the heap held at full zoom is 158 MiB against 151 at fit, and the metropolis comes back to 228 MiB at fit after full zoom, against 380.
**Slice 7 was dropped** (the roadmap manager, 2026-10-22): putting z2's pages up only when drawn from needs z1 resident as the fallback, 23 MiB, and the same census found the real history drawing from all six z2 pages at full zoom, and the metropolis from five, so it would have added memory.
**Slice 8 was dropped** (the roadmap manager, 2026-10-22): a soft Go memory limit for the city saves nothing once slices 5–6 are in, because the heap held from the OS barely moves with zoom. At full zoom on the real history (r914, Xvfb, 50 s each) Private_Dirty was 502–503 MiB with no limit, 530–540 at `GOMEMLIMIT=192MiB` and 499–517 at 160, while collections went from 35 to 41 and their CPU from 18.6 to 21.0 ms a second.

**What is left is the driver's** (2026-10-22). On the real display at r921, full zoom held 685–693 MiB own plus GPU at r905 and r921 alike, about 175 over, and fit 575–581 at r921 (item 161 is chasing the +115 there).
Ebitengine's own images, counted at their internal texture sizes, are 113–119 MiB at fit and 207 at full zoom, so about 175 MiB at fit and 235 at full zoom of the i915 figure is no image of the city's at all, and it grows with the draw traffic.
Xvfb cannot see it, because the software renderer keeps no driver buffers. The likeliest part is Mesa's cache of freed buffer objects, fed by vertex and index uploads every flush; the window's swap chain and Mesa's own batches are the rest.
The benchmark session is adding the shared, resident, purgeable and active DRM figures to `perf.py` and running r914 against r905 on the real display; the fix follows what dominates.

**The driver's breakdown, r914 against r905** (2026-10-23, real display, focused, real history; the sampler's new columns, meta `a4ed5ab`; MiB, means over each phase):

| phase | build | GPU | shared | resident | purgeable | active | own | own + GPU |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fit | r914 | 275 | 20 | 275 | 4 | 100 | 220 | 472–495 |
| fit | r905 | 247 | 20 | 247 | 3 | 116 | 209 | 456–458 |
| full zoom | r914 | 407 | 20 | 406 | 14 | 199 | 255 | 661–666 |
| full zoom | r905 | 381 | 20 | 380 | 19 | 184 | 303 | 680–685 |

The driver's buffer cache was not the gap: resident is the whole of it and purgeable under 20 MiB, and shared, the window's buffers, is a flat 20.
At full zoom slices 5–6 are a net 14–24 MiB (own 48 lower, GPU 26 higher, the GPU rise unexplained and at fit too); full zoom is still about 150 over.
Main at r935, after item 161's culling and one-mesh shutters, read 200 MiB of GPU at fit and 269 at full zoom the same morning, which points at the rest: a buffer that grows with what is drawn.
Ebitengine's OpenGL driver keeps one vertex and one index buffer, sized to the power of two above the largest flush and never shrunk; r905's heap held 33 MB of queued vertices and 7 MB of indices at fit, which is 64 and 8 MiB on the GPU.

**Slices 9–11, and slice 12 dropped** (2026-10-23). A texture inventory at r954 (a scratch copy of Ebitengine listing its backends, never committed; real history, Xvfb, the window at 1920×1200) found 247 MiB of images at full zoom and 10 of vertex and index buffers, every texture rounded up to a power of two a side: z2's kit pages 88, four window-sized layers at 2048² each 64, Ebitengine's shared atlas 32 for 9.4 MiB of pixels (7.9 of them the shore, which grew it), look and label pages 36, the two panel bakes 16.
Slice 9 lets the scratch a pan shifts layers through go 300 frames after the last pan.
Slice 10 makes the shore its own texture; the atlas stays at 1024², and the images went from 247 MiB to 235.
Slice 11 packs the kit atlases a page at a time (`tools/render-sprites/pack.py`, used by `render.py` and by `tools/repack-atlas`): z2 88 MiB of texture to 66, z1 24 to 18, every sprite's pixels identical, checked by `tools/atlas-diff.py`, which now compares a re-laid level sprite by sprite, and by a per-sprite comparison.
**Slice 12 was dropped** (the roadmap manager, 2026-10-23): the look pages are already powers of two, and the two panel bakes are each taller than 1024, so packed together they still need one 2048² page, the 16 MiB they cost now; with the strips it would save about 2.5.

**Where it stops, and what it waits on** (2026-10-23, released by the session "item 162" at the roadmap manager's word). At r964 fully zoomed in on the real history the city is estimated at about 550 MiB own plus GPU and fit at about 450 (the r962 texture census applied to r954's display figures; the benchmark session is measuring r964 on the real display for 0.3.0), so about 35 MiB over 512 fully zoomed in.
The rest waits on **two visual calls Aria makes after 0.3.0**, which the roadmap manager will put to her with frames:
1. **A coarser shore texel**, so the shore's texture fits 1024 a side: on the real history it is 1464×1416 at 4 world units a texel, a 2048² texture, 16 MiB, and at about 5.7 it would be 1024², 4 MiB, **−12 MiB** at fit and full zoom alike; the shore's bands are soft gradients drawn with linear filtering.
2. **A middle kit level**, cut at about zoom 1.5 and drawn up to 2.0 in place of z2: about 56% of z2's sprite area, so roughly 2.2 pages against z2's 4.1, **about −30 MiB or more** fully zoomed in, with slightly softer sprites at the closest zoom.
Either would bring full zoom near the budget and both under it. Beyond them nothing here explains the ~110 MiB of the i915 figure that is no image and no vertex buffer (Mesa's own; resident, not purgeable).
How to measure what a change does: build the city against a scratch copy of Ebitengine (a `replace` in a copy of the tree, never committed) that logs its backends with their internal sizes and what sits on its shared atlas, and run it on a copy of the state directory under Xvfb with the window at 1920×1200, holding the landing lock; texture sizes do not depend on the renderer.

**Aria's verdict on the two options, and slices 13–14** (2026-10-24).
Both were framed on the metropolis demo, before and after at one camera, at fit and at zoom 2.0 with 3× crops; the middle level was a real z1.5 cut from the same kits, whose fresh z2 matched the committed one within `atlas-diff`'s noise floor.
Aria: *"Honestly all of these options look great. I can't really tell the difference between before and after."*
At her request the roadmap manager decided, and both are built:
slice 13 sizes the shore's texel to fit 1024 a side, `4 × longest side / 1024` and never finer than 4, so the 12 MiB holds as the island grows, where a fixed 5.72 would have lost it at the real history's next growth (1023 texels wide);
slice 14 replaces z2 with z1.5, picked only where z1 would be drawn up by 1.75× or more, so zoom 1.5 keeps drawing z1 drawn up and costs nothing extra.
Kit texture settled, now against after: 18 against 18 MiB at zoom 1.5, 18 against 40 from 1.75 (no wheel step is there), 66 against 40 at 2.0.
Together about −38 MiB fully zoomed in, which leaves about 16 over 512; the session measures again after both land and reports what is left before closing.
Her two other observations, the rail drawn over the trees and a car on the kerb at z2, are in both halves and filed as items 221 and 222, and the demo's "millrace" labels as 223.

**Slice 14, as handed over** (2026-10-24, the session "item 162", stopped before any edit for a reboot; the roadmap manager approved this test tree as written).
The rule: `kitDrawUpMost = 1.75`, living in `pkg/assets` and read by `pkg/render`'s `kits.index`: the camera draws with the lowest kit level that draws its zoom up by less than 1.75×, so with z1 and z1.5 it picks z1.5 from zoom 1.75 exactly.
The cut: z1.5 replaces z2 in `pkg/assets/kits` (624 sprites, 3 pages, the last 725 rows), and `make sprites` and `render.py`'s default go to `--zooms 1,1.5`.
A cut is in the botropolis worktree's git-ignored `dist/item-162-options/kits-z1.5-cut/`, made by `blender -b --python tools/render-sprites/render.py -- atlas --zooms 1.5,2 --out <dir>` from the kits `make kits` fetches (about 13 minutes a level); the same run's z2 matched the committed one within `atlas-diff`'s noise floor.
Re-cut it if that directory is gone, and look at every page before it goes on `make publishable`'s reviewed list.
The tests, all approved:
- `pkg/render/kitresidency_test.go`: `TestKitLevelPick`, data-driven: zoom 0.2, 1, 1.5 and 1.74 pick z1, 1.75 and 2.0 pick z1.5 ("when the camera is at zoom Z / it should pick L"). And `TestKitResidentCost`: settled past `kitHoldUpdates` at zoom 1.5, 1.75 and 2.0, "it should hold no more than 18 / 40 / 40 MiB of kit texture", measured through the lazy loader with `internalSide`. The existing residency tests carry over with z2 read as z1.5.
- `pkg/render/kittrim_test.go`: `TestKitTextureCost`'s z2 ≤ 72 MiB becomes z1.5 ≤ 40.
- `pkg/assets/ladder_test.go`: "when the wheel walks its steps / it should never draw a sprite up by more than 1.75×" (the least of step ÷ level zoom, against `KitDrawUpMost`), and "it should end at the top of the ladder" unchanged.
  The assertion "it should still have a sprite to draw, rather than stretching one" (the highest level at least `MaxZoom`) is retired on Aria's verdict of 2026-10-24, and the comments in that test and `pkg/city/camera.go` that cite it say so.
- `pkg/assets/panes_test.go`: the cottage's five windows are checked on the highest level, not `Zoom == 2`.
- Tools: `check-asset-sources`' manifest pattern takes `kits-z1.5.json`; `read-road-pieces.py` and `atlas-cost.py` read the highest level, not z2 by name.
- Unchanged, as the guards: `TestSettledMemory` keeps its limit at the 512 MiB target, never today's figure, skipping as unmet in item 194's shape if it is still over; the drawn-size test in `kits_test.go` holds across the levels.
After it lands, measure full zoom on the real display the way the 0.3.0 table was (r964's method: the real history through a scratch daemon on a copy of the state directory, focused window, `perf-city`, `gpu_mib` with the GPU named), and send the roadmap manager the number and what is left against 512 before closing.

## Answered while building, slice 14

- **What slice 14 found beyond its tree** (the session "item 162", 2026-10-24, fixed in the slice): tests that set the camera to `atlas.Zoom` had silently stopped testing z1.5, since zoom 1.5 now picks z1; a `zoomPicking` helper gives each test a zoom that picks the level it means, with a precondition (`TestBridgeClearance` caught it; `TestPanesStayOnOneFace` and `TestBridgeRamp` had been checking z1 twice). The landmark-walls table's three art hashes changed, redrawn with `tools/landmark-walls` over the z1.5 sprites. `tools/atlas-cost.py` crashing on `main` is filed as [item 229](229-atlas-cost-crashes-before-it-prices-anything.md).
- **The real-display full-zoom measurement** (Aria, 2026-10-24, asked whether it may have the screen and when: *"Now, once slice 14 lands"*): this session runs it right after slice 14 lands, holding the landing lock, with the r964 method. It writes the XTEST zoom timeline itself, into `performance/tools/` beside `perf-city`, so the performance manager can rerun it; the raw runs go in `~/.local/state/botropolis-perf/`.
- **The full-zoom measurement tool** (manager, 2026-10-24): `performance/tools/perf-fitzoom`, `lib/xin.py` and `perf.py phase-summary`, made rerunnable from the r964 driver with its method unchanged; its tree approved with "least, most and mean" split into three data-driven tests; `performance/method.md` names it.
- **The see-through guard at drawn-up zooms** (manager, 2026-10-24): slice 14's landing failed `TestBuildingSheetLights` and `TestBuildingLooksCached` at zoom 2 on a 1-pixel line along the front building's rim, where `seenThroughFront`'s 2-pixel solid margin is narrower than a drawn-up sprite's soft rim (the check fails on `main` at zoom 1.5 too). The margin follows the draw-up — 2 pixels at a level's own size, ceil(2 × scale) + 1 when drawn up — which corrects the measurement without loosening what it guards, proved by a mutation: lights drawn over a front building's interior still fail at every zoom checked. The cached looks that differ at zoom 1.5 are filed as [item 233](233-cached-building-looks-differ-when-drawn-up.md).
