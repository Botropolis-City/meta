# 161. Drawing a frame costs 41 ms of CPU in 0.2.2, against 21.6 ms in 0.1.7 and a budget of 10

**Open, in progress since 2026-10-22 in the session "item 161". Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the city CPU budget Aria set the same day. Nobody's call — the budget is set.**

Depends on: nothing

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

- **Slice 1, text**: a panel is recorded rather than drawn, and baked once its record holds; the manager has the test tree.
- **Slice 2, shutters**: into the look cache, with item 162, which is changing it too.
- **Later, group lines** (parked): on a synthetic history with many more grouped sessions than Aria's, the group lines were 71% of Draw, because the dry pass tessellates and hashes every dash every frame only for the overlay to find its hash unchanged. The manager approved a tree that lays them out only when what they paint changes, relative to the camera's whole-pixel origin. Under it **a hovered car still lays them out every frame**, as now, because the city recedes under it in fade groups. The red test is on the local branch `item-161-lines-parked`.
