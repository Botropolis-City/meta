# 308. The soak reads nightfall as growth, because the box's clock decides when the city lights up

**Done 2026-11-02 (`ef2458e`, r1217). Filed 2026-10-27 (r1192), from 0.3.3's soak, the first to run. Nobody's call — the method is the performance manager's to specify, its build an item session's.**

Depends on: 311, 318
Landed: slice 1 (`8003765`, r1193).
Landed: slice 2 (`ef2458e`, r1217).

0.3.3's soak (server 3101537, from 11:47 MDT) measured the city's memory and GPU flat for 122 minutes, +0.61 MiB an hour, and then 325 → 375 MiB in one 10-second sample at 21:00:05 UTC: Private_Dirty +16 MiB and GPU +32 MiB, flat again after (−3.0 MiB an hour).
21:00 is `NightFrom` (`pkg/city/scene.go`) on the box's clock, which the city reads in UTC: the windows lit and the lights were drawn.
`performance/method.md` fits one least-squares slope per phase, so a one-time step inside a phase reads as hourly growth, +21 MiB an hour against the 1 MiB budget; whether a soak crosses 21:00 or 06:00 depends only on when it was ordered.

## The fix

1. `perf-soak` pins the city's light for the run, forced day or forced night, through the city's own setting or the demo's clock, so the wall clock cannot change what is drawn; or each phase runs wholly in one light. The 1 MiB an hour budget does not change.
2. The report names any step it finds, its time and size, and the slopes either side, so a reader sees a step as a step.
3. Recorded here: the switch to night costs about 49 MiB, 32 of it GPU, once a night, within the settled budgets.

## The method (performance manager, 2026-10-27)

**Pin the light at start, not with a key.**
Today the light is pinned only by `n` in the city (`cycleLight`, `pkg/render/keys.go`), which needs the window focused, and the soak hides the window halfway through.
So the city takes the light as a start-up setting, `--light night|day|live` with `live` the default, setting `Scene.light` before the first frame, and `perf-soak` passes `--light night` to every run.
Night is the pin because it draws everything day draws plus the lit windows and the lights stream (item 236), so it is the one that can grow more.
`perf-soak --light day` stays available for a day run, and the report names the light it ran in.

**Every phase runs in one light, and the verdict does not change.**
Each phase's least-squares slope from 600 s stays the verdict, at most 1 MiB an hour, exit 1 over it.
A pinned run has no clock step to explain, so nothing is subtracted, split out or excused.

**Steps are named, not excused.**
`soak.md` lists every step it finds: two samples 10 s apart differing by more than 8 MiB of `Private_Dirty` + GPU, or by more than four times the phase's noise, whichever is larger.
The noise is 1.4826 times the median absolute deviation of the sample-to-sample differences, not the residual of the fitted slope:
a residual includes the step itself, so a 49 MiB step would raise its own threshold to about 56 MiB and hide.
A run whose samples barely move has a noise near 0, and the 8 MiB floor holds it.
For each step it gives the time on the box's clock and in UTC, its size split into `Private_Dirty` and GPU, and the slopes either side.
A step still counts toward its phase's slope, because memory taken in a step is memory taken.
The table is what tells a reader whether an over-budget slope is a ramp or a step.

**Prove the switch gives its memory back.**
The 49 MiB at nightfall is within the settled budgets, but only if it is paid once.
The item's acceptance adds one short check: the city on the 600-district fixture, `--light live` with the scene's clock scrubbed across night → day → night → day, sampled as the soak samples.
It passes when the second night settles within 4 MiB of the first, and the second day within 4 MiB of the first day.
If a second night adds again, that is a leak at the light switch, and its own item.

**Done when:** a soak run with `--light night` reports one light, an empty or explained step table, and both phases within 1 MiB an hour; the light-cycle check passes; and `performance/method.md` step 8 says all of this, which the performance manager writes once it lands.

## Slices (item session, 2026-10-27)

The light is the config key `light = live | night | day`, set for one run with `--set light=night`, not a flag: the soak measures the release build, which has no devtools flags, and a key adds no public flag (item 149).
`perf-soak --light night|day|live` passes it through `perf-busy-city --set`; `live` sets nothing, so a build from before the key can still be soaked.

1. **Slice 1, landed:** the key, the hostile config set to night, an acceptance test that shoots the city at noon pinned to night against day and at midnight live, and the perf tools' `--light` and step table.
2. **Slice 2, landed with item 318:** the light-cycle check, `testing/acceptance/lightcycle_test.go`.
   It first found item 311: a `--record` city on the 600-district fixture wrote no frame, while using about six cores.
   The paced first read suspected here was not the cause; a recording whose first tick beat its first snapshot deadlocked (item 311).
   It then found the growth item 318 traced to llvmpipe, not the city.

## Closed (item session, 2026-11-02)

Slice 1 (`8003765`, r1193; meta `43eb653`) pins the light: the config key `light`, and `perf-soak --light night` by default, with `soak.md` naming the light and listing every step.
Slice 2 landed with item 318 (`78f5f7c`, r1216, and `ef2458e`, r1217): the light-cycle check, in 180 s phases judged on their last 30 s.
Under llvmpipe it counts the city's images and its live Go heap, each repeat within 4 MiB, and `TestLightCycleOnARealGPU` keeps the whole-process reading on a real GPU.

Against **Done when**:

- 0.3.4's soak ran with `--light night`, found no steps, and met every growth budget ([report](../performance/reports/2026-10-29-i5-12500-igpu-soak-0.3.4.md)).
- The light-cycle check passes headless.
- `performance/method.md` step 8 covers the pinned light and the step table.

**Deviations, for Aria:**

- The light-cycle check counts the city's images and heap under llvmpipe, not whole-process `Private_Dirty`, as item 318's method records.
- Its 40 s phases became 180 s, because the shorter phases had not settled.
- Method step 8 does not yet describe the light-cycle check; the performance manager is adding it.
- The real-GPU variant has not yet completed a run (item 318).
