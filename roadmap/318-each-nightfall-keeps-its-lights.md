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
