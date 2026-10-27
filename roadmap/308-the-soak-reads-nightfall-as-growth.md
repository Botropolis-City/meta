# 308. The soak reads nightfall as growth, because the box's clock decides when the city lights up

**Open. Filed 2026-10-27 (r1192), from 0.3.3's soak, the first to run. Nobody's call — the method is the performance manager's to specify, its build an item session's.**

0.3.3's soak (server 3101537, from 11:47 MDT) measured the city's memory and GPU flat for 122 minutes, +0.61 MiB an hour, and then 325 → 375 MiB in one 10-second sample at 21:00:05 UTC: Private_Dirty +16 MiB and GPU +32 MiB, flat again after (−3.0 MiB an hour).
21:00 is `NightFrom` (`pkg/city/scene.go`) on the box's clock, which the city reads in UTC: the windows lit and the lights were drawn.
`performance/method.md` fits one least-squares slope per phase, so a one-time step inside a phase reads as hourly growth, +21 MiB an hour against the 1 MiB budget; whether a soak crosses 21:00 or 06:00 depends only on when it was ordered.

## The fix

1. `perf-soak` pins the city's light for the run, forced day or forced night, through the city's own setting or the demo's clock, so the wall clock cannot change what is drawn; or each phase runs wholly in one light. The 1 MiB an hour budget does not change.
2. The report names any step it finds, its time and size, and the slopes either side, so a reader sees a step as a step.
3. Recorded here: the switch to night costs about 49 MiB, 32 of it GPU, once a night, within the settled budgets.
