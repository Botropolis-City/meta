# 161. Drawing a frame costs 41 ms of CPU in 0.2.2, against 21.6 ms in 0.1.7 and a budget of 10

**Open. Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the city CPU budget Aria set the same day. Nobody's call — the budget is set.**

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
