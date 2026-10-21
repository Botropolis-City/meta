# 156. The city's Go heap reaches several gigabytes within seconds of start-up and keeps gigabytes of it

**Open. Filed 2026-10-19 (r780), from the 0.2.2 performance reports, against the city memory budgets Aria set the same day. Nobody's call — a defect; what causes it is not yet established.**

Depends on: nothing

**What it does**, from `GODEBUG=gctrace=1` on the real display, integrated graphics:

| rig | build | Go heap at its peak | live heap settled | report |
| --- | --- | --- | --- | --- |
| Core Ultra 7 255H | 0.1.7 | — | 161 MB | [laptop](../performance/reports/2026-10-19-laptop-igpu-0.2.2.md) |
| Core Ultra 7 255H | 0.2.2 | 5–8 GB within 4 s (live 2.1 → 4.1 → 7.7 GB) | 2.4–3.7 GB | laptop |
| Core Ultra 7 265U | 0.2.2 | 2.3 GB at 3–6 s (live 1.7 GB) | 798 MB | [265U](../performance/reports/2026-10-19-ultra7-265u-igpu-0.2.2.md) |
| Core Ultra 7 265U | r780 | 1.31 GB at 2.4 s (live 1.21 GB) | 1.21 GB | 265U |

Under Xvfb, where the burst is smaller but the same shape, 0.1.7 settled at 86–98 MB and 0.2.2 climbed to 475 MB within 3.3 s (laptop); on the 265U, 0.2.2 peaked at 538 MB and r780 at 567 MB, so **item 70's page-at-a-time upload (r765) did not remove the burst**.

**Where it is**: a heap profile of 0.2.2 (`perf-pprof-build`, under Xvfb on the laptop) puts **~80% of the heap in Ebitengine's draw-command queue**, `graphicscommand.(*commandQueue).EnqueueDrawTrianglesCommand`, reached from `render.(*Game).Draw` → `drawIso` (`pkg/render/iso.go`) through `drawSprite`/`kitLifted` (49%), `queueDistrictPlate` → `plate` → `text` (28%), `isoTree`/`agedLots` (24%) and `composeStatic` (9%).
A heap profile of r780 on the 265U's real display, three seconds in and again at sixty, says the same and adds one thing: **85% of 1.2 GB is in the command queue, and it got there through Ebitengine's `vector` package**.
The stack runs `DrawImage` → `invokeUsageCallbacks` → `vector.fillPathCallback` → `fillPaths` → `DrawTrianglesShader32` → `EnqueueDrawTrianglesCommand`: `vector` defers path fills and strokes, and flushes them as triangles when an image they touch is next drawn.
So `kitRising`/`kitAt` (542 MB), `isoTree` (294 MB) and `vector.FillRect` (236 MB) are where the deferred fills were **flushed**, not where they were issued, and the sprites are not the cost.
`vector` fill and stroke calls in `pkg/render` went from 72 call sites in 0.1.7 to 161 in 0.2.2, with Ebitengine at v2.10.2 throughout.
The queue reuses its buffers across frames, so whatever the first frames enqueue, the capacity they grew to is kept: that is why the peak becomes the settled figure.
**What makes the first frames enqueue so much is not established.**

**The budgets it breaks** ([budgets.md](../performance/budgets.md), *City*): ≤ 512 MiB `Private_Dirty` + GPU together, settled with the window open; ≤ 1 GB `Private_Dirty` + GPU at any moment of start-up.
On integrated graphics the GPU's share is system RAM too (item 162), so the Go heap's share of either budget is a few hundred MB at most.

## The fix

1. **Bisect r409..r745** with `perf-city` on the Go live heap (method.md, run 4), one build at a time; `--headless` is fine for the heap, which does not depend on which GPU draws, and halves the time.
   Candidates in that window, from 0.2.2's own change list: the district plates and map labels (`5b304e9`, item 102), the car-fade and plan layers (items 108 and 106), the shore texture sized to the island (item 85 slice 3).
2. **Profile the first seconds** with `perf-pprof-build` on the real display, where the city is one process.
   Under `--headless` the city runs as two `botropolis` processes and the outer one takes the `PERF_PPROF` port, so a headless heap profile is of the wrong process (found 2026-10-19; see the 265U report).
3. Find what the first frames draw that later frames do not — a static layer composed in one frame, every label laid out before the camera settles — and spread it, cache it, or draw it once into an image instead of as triangles.

Tests: `testing/acceptance/memory_test.go` already gates the atlas's start-up heap (item 70); add a measure test of the Go heap's peak over the first ten seconds of the largest demo, whose limit comes from the budget, not from today's figure.

**The demo's start-up gate now sits at its limit** (item 182, 2026-10-20). `TestStartUpPeak` (Go heap at GC start, limit 240 MB) measured 239 207 209 226 226 MB in five isolated runs on main before item 182's slice 2, so it passes by 1 MB at best and failed at 258 MB under full-suite load. Item 70 measured 205 MB. The limit is the goal and stays; what moved the start-up heap by ~35 MB since is part of this item's bisection. Held with the rest of the performance work for Aria's pass, so until then this gate can fail a landing on load alone: rerun, don't raise it.
- Item 185, same day: 290 MB under load on its first `make land`; passed 4 of 4 alone and on the retry.

## Measured 2026-10-21: anti-aliased vector fills are the volume, not the command count

The design session proposed a mechanism: about 100 of `pkg/render`'s vector calls are anti-aliased, Ebitengine v2.10 defers each one per destination and flushes it through several jittered stencil passes, and drawing in depth order makes every shape flush on its own.
Measured on the 265U at r844 (`bd67029`), headless (Xvfb, llvmpipe), the `metropolis` demo at 1600×900, the city built with `-tags 'ebitenginedebug devtools'`, every draw command counted per frame from Ebitengine's own log, 120 s per build:

| per frame, after the first 20 | HEAD | HEAD with `AntiAlias` forced off in `vector.FillPath` |
| --- | --- | --- |
| draw-triangles commands | 478 | 476 |
| render-target switches | 175 | 175 |
| indices | 734,811 | 112,135 |
| Go live heap | 418 MB | 142 MB |
| frames drawn in 120 s | 101 | 227 |

- **Anti-aliasing is most of the heap**: forcing it off took the live heap from 418 to 142 MB and the indices a frame down 6.6×, with the same commands.
- **It is not more commands or more batch breaks**: both counts are identical with it off. The 175 target switches a frame are there either way, from the other causes the design session named (the fader layer, the night lights' punches, one texture per kit page), and are a separate cost.
- So a gate on **commands per frame would not have caught this; indices (or vertices) per frame would**. Both are counts of work, not seconds, and the debug log gives both.
- The first five frames issue about as many commands as later ones (415 against 478), so this headless run does not show the real display's start-up burst; that still needs the real-display profile in step 2 of the fix.

The forced-off build is an upper bound: it drops anti-aliasing from every vector call, chrome included, and nobody has looked at the frames.
The fix this points at is fewer anti-aliased fills in the world (non-AA where the zoom hides the difference, or shapes baked once into images), measured by indices per frame.

**Proposed fix, filed 2026-10-21:** items 191 (world shapes as stamps), 192 (a building's look cached), 193 (a still city cached, only movers drawn) and 194 (counting a frame's work). This item stays open for the start-up burst on the real display, and closes on measurement.
