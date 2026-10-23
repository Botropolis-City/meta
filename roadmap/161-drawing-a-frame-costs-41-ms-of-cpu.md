# 161. Drawing a frame costs 41 ms of CPU in 0.2.2, against 21.6 ms in 0.1.7 and a budget of 10

**Open, in progress since 2026-10-22 in the session "item 161". Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the city CPU budget Aria set the same day. Nobody's call — the budget is set.**

Depends on: nothing
Landed: slice 1 (`8767ffe`, r912).
Landed: slice 2 (`b34cc7e`, r921).
Landed: slice 3 (`2da3143`, r927).
Landed: slice 4 (`6f139e4`, r935).

With `BOTROPOLIS_FRAMETIME=1`, the city on the laptop's integrated GPU spent **41.2 ms of CPU a frame in 0.2.2 against 21.6 ms in 0.1.7**, over the 33 ms a 30-tick frame has ([the laptop report](../performance/reports/2026-10-19-laptop-igpu-0.2.2.md), finding 8).
On the Core Ultra 7 265U the 0.2.2 window was never focused, so it drew nothing and measured no frame time; **0.1.7 was focused, and drew at 10.3 ms a frame while using 50–60% of a core** ([the 265U report](../performance/reports/2026-10-19-ultra7-265u-igpu-0.2.2.md)).
So the CPU-per-core budget is broken even where the per-frame one is met: ms/frame of drawing is not the whole cost of a frame.

**The budget** ([budgets.md](../performance/budgets.md), *City*): visible and drawing, **≤ 10% of one core mean and ≤ 10 ms of CPU a frame**.
That is a quarter of 0.2.2's cost and half of 0.1.7's, so this is not only a regression to bisect: even reverting it would leave the city over budget.

**This answers item 69's question.** Item 69 asked Aria whether 10% of a core was still the bar for a busy city; budgets.md now sets it for a city that is visible and drawing, busy or not.

**Leads, not established:**

- Item 102 (`5b304e9`) moved the roads' tags out of the cached static layer and lays every label out each frame; `BenchmarkDrawAFrame` in `testing/acceptance/frame_bench_test.go` reports the gap between labels on and off, and never gates.
- The draw-command queue that holds most of the city's heap (item 156) is filled from the same calls: `drawIso` → `drawSprite`/`kitLifted`, `queueDistrictPlate` → `plate` → `text`, `isoTree`/`agedLots`, `composeStatic`. Fewer triangles a frame is likely to buy both.

## The fix

1. Bisect r409..r745 for the doubling with `perf-city --bin` on the real display, focused, one build at a time (method.md, run 4); `BenchmarkDrawAFrame` can narrow it first, since it compares builds on any machine.
2. A CPU profile of a focused city (`perf-pprof-build`, `/debug/pprof/profile?seconds=60`) for where the remaining time goes, then cache what does not change between frames: label layout, plates and trees belong in the static layer unless the camera moved.
3. Make `BenchmarkDrawAFrame`, or a measure test beside it, gate at the budget's 10 ms rather than report.

Judge it with `perf-city` focused on integrated graphics, and quote ms/frame with the frame count.

## Measured 2026-10-21

Headless at r844 with Ebitengine's debug log, forcing anti-aliasing off in `vector.FillPath` cut the indices a frame 6.6× (734,811 to 112,135) with the same 476–478 draw commands, and the city drew 227 frames in 120 s against 101 (item 156 has the table and the method).
The debug log slows both builds, so the frame rate is a ratio, not a cost; a focused real-display `perf-city` run of the same two builds would give the ms/frame.

**Proposed fix, filed 2026-10-21:** items 191–194; this item closes when a focused city on integrated graphics meets the budget.

**Re-measured after items 191–195** (265U iGPU, `458454f`, r871, [report](../performance/reports/2026-10-21-ultra7-265u-igpu-r871.md)): on the metropolis demo a frame now takes 6–15 ms (settled, pan, zoom), against 20–172 ms in 0.2.2. **On the real history (198 transcripts, 144 projects) it is still 17–48 ms focused, 18–30 settled, 41–54 panning, 25–31 zooming**, 2–5× the 10 ms budget, and a focused city uses 83% of a core against 10%. So item 194's gate, which measures the demo, passes while the real history misses: the demo is too small to stand for it. Part of the 83% is the city laid out again on every daemon snapshot (item 197).

**Re-measured at r905** (`e6bde10`, 265U iGPU, focused, real history, [report](../performance/reports/2026-10-22-ultra7-265u-igpu-r905.md)): drawing takes **8.7 ms a frame at fit** (in budget; r871 17–48) but **18.9 ms at full zoom**, and a focused city uses **61% of a core at fit and 84% at full zoom**, against 10%. Draw is multi-threaded, so about 15 ms of CPU a frame; of Draw, text drawn every frame (`note` → `text/v2.Draw`) is 25%, the journal panel 16%, the group-review panel 9%. The metropolis demo: 5.5–6.1 ms a frame, but still 36% of a core.

## Slices (item session, 2026-10-22)

The real-history profiles at r905 (re-taken 2026-10-22, settled and focused, 60 s at fit and at full zoom) put the cost in two places.
At fit, `Game.text` is 28% of Draw's CPU, and 78% of that is the journal and group-review panels, each glyph a `DrawImage` every frame.
At full zoom, building shutters (`drawBuilding` → `drawRun` → `drawSteps` → `shutter`) are 36% of Draw, filled every frame outside item 192's look cache.
Group lines are 1.1% of Draw at fit and under 0.1% at full zoom.

- **Slice 1, text** (landed): an opted-in panel, the journal and the group review, is recorded rather than drawn, baked once its record holds and blitted while it does. The frame check draws each straight and through its bake and requires them within the look tolerance.
- **Slice 2, full zoom** (landed). Nothing culled: every building in the city was drawn every frame, and at full zoom (217 sessions, 1920×1200, Drive) 37 are on screen. The other 180 filled the 32 MiB of look pages, so about 190 of 217 looks a frame were drawn straight, and the cache's counts did not show it, because a bake that found the pages full was counted as nothing. Four parts: such a bake counts as a miss; a building whose cull bound (its look's bounds padded by half its sprite's width) misses the frame is not drawn; a look page drawn from the frame before is never started again; and a building's shutter panes are one mesh. `BenchmarkAFullZoomFrame`, on a machine at load 8–40: 19–30 ms a frame before, about 4–6 after, with no look baked again. The guards: every building of four cities is recorded whole and must ink inside its bound, lights included (with no padding it fails by 6–7 px), and the frame check has a full-zoom variant with a building across the edge (a bound shrunk by 40% failed it by 7,054 pixels).
  **What is left at full zoom is capacity**: the visible looks are about 27 MB in a 32 MiB cap, and shelf packing wastes enough that 8 or 9 of 46 find no room and are drawn straight. The same 32 MiB as two 2048-pixel pages rather than eight of 1024 holds more: 13–23 straight on the smaller pages, 8–9 on the larger. Aria held the 512 MiB budget on 2026-10-22, so no larger cap; a better packer is for later, if the real history needs it. The test holds 9 as a ceiling against regressions, not a target. It is 8 or 9 by the path of the test's temporary home, not by the order looks bake: a home at a fixed path gave 8 on six runs, and five paths gave 8, 9, 8, 9 and 8, as the layout put 46 or 47 runs on screen. A given history packs the same every time.
- **Re-measured at r921** (`b34cc7e`, 265U iGPU, focused, real history, against r905 the same evening at load 8–11): full zoom 27.1 → 12.6 ms a frame and 95% → 58% of a core; fit 12.8 → 13.4 ms, 67% → 61%, the panels' share of Draw 21% → 4%, and the world now 83% of it (`agedLots` 23% is item 207's; `paintStill` 16% is next here). But **own + GPU at fit rose from 461–464 MiB to 575–581**, over the 512 MiB budget r905 met.
- **Slice 3, memory at fit.** **Ebitengine gives every unmanaged image a power-of-two texture**, so a bake is as costly as the next power of two of its larger side. A panel's first draw is a scrim over the whole frame, so each bake was 2048×2048 at 1920×1200, 16 MiB, for two panels 32. **Any panel baked later will do the same unless its full-frame draws stay out of the bake.** And two 2048-pixel look pages put a city at fit, whose 3.5 MB of looks fit one page, on 16 MiB where r905 had 4. Measured under Xvfb with Ebitengine's own image total (217 sessions at fit, both panels open): 378 MiB with the bakes against 346 with the panels drawn straight. The scrim is now drawn each frame and only what lies on it is baked (826×1142 and 886×165, 9 MiB). The look pages open as four of 1024 and then one of 2048, the same 32 MiB, so a city at fit holds one 4 MiB page; full zoom draws 7 or 11 looks straight a frame by the test's layout, against 8 or 9 on two large pages, and the regression ceiling is 11 (the large page opened second gave 8, 10 or 13). The same run holds 343 MiB, against 334 straight. The rest of the 115 MiB is not in that harness, where r905 holds 368 MiB of images and 467 of Go heap, r921 378 and 381, and slice 3 343 and 388. Whether fit is back under 512 on the real display is for the re-measure; if not, the 9 MiB the panels cost goes to Aria.
- **Slice 4, the standing city's redrawn rectangles** (`paintStill`, 13% of Draw at fit at r921). Over half of it was `batch()`, which orders the draws inside the rectangles something moves in so Ebitengine can merge them: it asked for each draw's box and source again on every comparison, and a source reflected on Ebitengine's private field for the image a sub-image was cut from, by name, every call. Each is now asked for once, overlaps are compared within a rectangle only, and the page is kept beside the draw by whoever cut the sub-image; the reflection is left only in a test, as the reference. On the metropolis demo, 400 frames by night, `paintStill` took 0.34 s of CPU before and 0.17 after.
- **Re-measured at r935** (`6f139e4`, 265U iGPU, focused, real history, paired with r921 on 2026-10-23 at load 1.5–3.9): fit **11.0 ms a frame, 60% of a core, 376–378 MiB own + GPU** (r921 16.8 ms, 73%, 390–403 MiB); full zoom 13.1 ms, 60%, 463–466 MiB (r921 14.1 ms, 65%). **Memory is within budget**, so the panels' 9 MiB stands. `paintStill`'s share of Draw at fit fell from 45% to 26%. r921 read 575–581 MiB at fit the day before and 390–403 this day, the same binary on another copy of the real state, so the two days do not compare; in this pair slice 3 saved 14–25 MiB at fit.
  **Still over the CPU budget**, about 6× at fit and at full zoom. What is left, by share of Draw: at fit `agedLots` 18% (item 207), overlay 17%, `drawList.Mesh` 15%, text 8%; at full zoom the shutters 32% and `drawBuilding` 34%. That is the looks on screen that find no room in the 32 MiB of pages and are drawn straight: on the real history more of them than in the test's city.
- **Later, group lines** (parked): on a synthetic history with many more grouped sessions than Aria's, the group lines were 71% of Draw, because the dry pass tessellates and hashes every dash every frame only for the overlay to find its hash unchanged. The manager approved a tree that lays them out only when what they paint changes, relative to the camera's whole-pixel origin. Under it **a hovered car still lays them out every frame**, as now, because the city recedes under it in fade groups. The red test is on the local branch `item-161-lines-parked`.
