# 318. Each nightfall keeps its lights: the city retains about 40 MiB per night, outside the Go heap

**Open, in progress since 2026-10-28 in the session "item 318". Filed 2026-10-28 (r1204), from item 308's light-cycle check, measured by its session and the performance manager. Nobody's call — a defect against the growth budget.**

On the 600-district fixture at r1197, with 180 s settled phases, a city held at day stays flat (454 → 453 MiB over 15 minutes), but one cycled by the clock goes day 445–448 → night 490 → day 485–488 → night 522–536 → day 531–541 MiB of `Private_Dirty`, in two runs.
Each nightfall adds 40–46 MiB and the following day gives back 3–5; only about 9 MB of each night is Go heap (`inuse_space` +7.2 MB), so about 31 MiB is outside it — most likely night's textures, the lit windows and the lights layer, made at nightfall and never released at daybreak.
After two nights it settles at 522–541 MiB, above the 512 MiB settled budget (approximate under llvmpipe, where textures count in `Private_Dirty`).

In use the light switches twice a day, so this is about 40 MiB a day for as long as the city stays open, against the growth budget of 1 MiB an hour; a soak pinned to one light (item 308) cannot see it.

## The fix

Release, or reuse, night's images at daybreak so a second night costs what the first did.
The test is item 308's slice 2, `testing/acceptance/lightcycle_test.go` (held in item 308's worktree): night → day → night → day, each repeat within 4 MiB of the first; it lands with this fix, red first, unchanged.

## Diagnosis, 2026-10-28

The city does not leak at nightfall; the growth is llvmpipe's.
Item 308's cycle at r1204, unchanged, run both ways: headless under Xvfb and llvmpipe 466 / 503 / 500 / 547 / 571 MiB (+44 at the second night, +71 at the second day), and windowed on the reference machine's Intel GPU 333 / 339 / 339 / 340 / 340 (+1, +1, both subtests pass).
Ebitengine's own image memory steps once at the first nightfall (the two lights images, kept by day) and stays flat through the second night and day; a heap diff of the warm-up day against the second day is −0.8 MB.
Headless, the extra `Private_Dirty` is native: about 124 MiB in glibc malloc arenas belonging to llvmpipe's rasterizer threads, plus `[heap]` 14 → 29 MiB at the second daybreak.
Raw data: `~/.local/state/botropolis-perf/item-318/{cycle-1,windowed-1}`.

**Re-scoped** (manager, 2026-10-28): a measurement fix, off 0.3.4's path.
The light-cycle check and the settled and growth budgets, read under llvmpipe, must count something llvmpipe cannot inflate — Ebitengine's image memory plus the Go heap, or run with `MALLOC_ARENA_MAX` if a `malloc_trim` control shows the arenas are only kept free memory.
The method is the performance manager's to specify here; item 308's slice 2 lands with it.

## The method (performance manager, 2026-10-28)

The budgets count what the user's machine pays, the city's whole process (`Private_Dirty` + GPU), and that stays the rule; what changes is how a test under Xvfb reads it, because llvmpipe is not a renderer anyone draws the city with.

**A run with `MALLOC_ARENA_MAX=2` decides which of two methods the headless check uses** (corrected by the item session, with the performance manager's agreement, 2026-10-28).
A `malloc_trim` control says whether the arenas hold freed memory, but not whether fewer arenas stop the growth, so the deciding run is the one the first method would use: the same cycle headless, with `MALLOC_ARENA_MAX=2` on the city alone.

1. **If that run passes** (each repeat within 4 MiB of the first), the arenas held freed memory, which is fragmentation and not use.
   Then the headless check runs the city with `MALLOC_ARENA_MAX=2`, set by the test for the child process only, and keeps counting `Private_Dirty` of the whole process against the 4 MiB criterion, unchanged.
   It still catches any real leak, native or Go, and the product's environment is untouched.
2. **If it does not**, the process's `Private_Dirty` under llvmpipe cannot judge the city, whether the memory is llvmpipe's own or freed memory glibc keeps.
   Then the headless check counts what the city itself holds: Ebitengine's image memory (the debug log's image sizes, summed as RGBA) plus the Go heap's live bytes after a GC, each repeat within 4 MiB of the first.
   That misses a native leak in the city's own GL calls, so the whole-process check moves to a real GPU (below).

**The whole-process check on a real GPU, before each release, whichever method the headless check uses.**
The cycle windowed on a real GPU counting `Private_Dirty` + GPU, each repeat within 4 MiB of the first, as the reference machine passed it at r1204 (333 / 339 / 339 / 340 / 340).
The soak box draws on a real iGPU (Mesa on the i5-12500's UHD 770, not llvmpipe), so the check can run there as the soak's first phase, without Aria's screen; until it does, the reference machine's display with her leave.

**The settled and growth budgets elsewhere under llvmpipe** follow the same rule: a `Private_Dirty` read under Xvfb is reported with the arena share named, and a verdict against 512 MiB or 1 MiB an hour is taken on a real GPU.
`make test-performance`'s big city runs through `render.Drive` with no GL and is unaffected.

## The controls (item session, 2026-10-28)

Item 308's cycle at r1204, unchanged but for each run's one setting, headless under Xvfb and llvmpipe, settled `Private_Dirty` in MiB over each phase's last 30 s (warm-up day / first night / first day / second night / second day):

| run | settled | second night, second day against the first |
| --- | --- | --- |
| as it stands | 466 / 503 / 500 / 547 / 571 | +44, +71: red |
| `malloc_trim(0)` every 10 s | 468 / 487 / 488 / 473 / 475 | −14, −13: passes |
| `MALLOC_ARENA_MAX=2` on the city | 466 / 508 / 506 / 542 / 547 | +34, +41: red |
| windowed, the reference machine's Intel GPU | 333 / 339 / 339 / 340 / 340 | +1, +1: passes |

Trimming gives the growth back, so the arenas held freed memory and not live use; but with two arenas the same freed memory piles up in glibc's main heap instead (`[heap]` 68 → 100 → 143 MiB over the two nights), so `MALLOC_ARENA_MAX=2` does not make `Private_Dirty` under llvmpipe a fair reading.
**The second method applies.**
The trim was continuous rather than taken at each phase's end, so its row is the growth while trimmed, read against the first row.
Raw data: `~/.local/state/botropolis-perf/item-318/{cycle-1,trim-1,arena2-1,windowed-1}`.

**Done when:** the control's result is recorded here, the check uses the method it selects, it passes on this tree headless, and one real-GPU cycle passes; `performance/method.md` then says so, which the performance manager writes.
