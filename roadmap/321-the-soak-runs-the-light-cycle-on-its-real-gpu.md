# 321. The soak box runs the light cycle as its first phase, on its real GPU

**Open. Filed 2026-10-28 (r1207), proposed by the performance manager from item 318's diagnosis. Nobody's call — a method addition, after 0.3.4.**

Depends on: 318

Item 318 showed the light-cycle check (item 308's slice 2) reads llvmpipe's arena growth under Xvfb and passes on a real GPU, so the method asks for a whole-process cycle on a real GPU before each release — which today means Aria's screen.
The soak box draws on a real iGPU, so the cycle can run there as the soak's first phase, before the visible and hidden phases, with no screen of Aria's needed.

## The fix

`perf-soak` gains a light-cycle phase at the start (night → day → night → day, 180 s each, judged on the last 30 s, each repeat within 4 MiB of the first), reported in `soak.md` beside the growth verdict; the pinned phases follow as now.
Tests in `perf_test.py` on staged samples; the method and `budgets.md` say the cycle is read from the soak.

## The method (performance manager, 2026-10-28)

**What the phase counts:** the whole process, `Private_Dirty` + DRM-resident from the city's `fdinfo`, the reading `perf.py` already takes as `gpu_kib` for the budgets, so the cycle and the growth verdict count the same thing; item 318's real-GPU measure, unchanged.

**How it runs:** before the pinned phases, the same city and desk, with `--set light=live` and the scene's clock scrubbed as item 308's check scrubs it (`]`), warm-up day then night → day → night → day, 180 s a phase, sampled every 10 s as the soak samples, judged on each phase's last 30 s, which must hold a slope under 0.1 MiB/s or the phase is reported as unsettled.
Then the city is restarted with the soak's pinned light, so the cycle's images and arenas cannot carry into the growth phases.

**Its verdict:** each repeat within 4 MiB of the first of its light, as item 318's check; `soak.md` gets a "Light cycle" table (phase, light, MiB, change from the first of its light, settled or not) and its own line in the verdict.
A cycle that fails makes the run "over" as a growth slope over 1 MiB an hour does, since a switch that keeps memory is growth in use; one that cannot be judged (a phase unsettled, the scrub key not taken) makes the run "not a measurement".

**What must be true of the box first:** the pre-flight (items 309, 319) checks that the city draws on the GPU, not llvmpipe: `GL_RENDERER` from the city's log, or `glxinfo -B` as the soak user on `:0`, must not name llvmpipe or softpipe, or the pre-flight fails, since a cycle read through llvmpipe is the false red item 318 found.

**Done when:** a soak on a real box writes the "Light cycle" table and line, a staged run in `perf_test.py` covers pass, over and unsettled, and `performance/method.md` step 8 says the cycle is the soak's first phase, which the performance manager writes.
