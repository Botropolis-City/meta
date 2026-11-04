# 321. The soak box runs the light cycle as its first phase, on its real GPU

**Open, in progress since 2026-11-02 in the session "item 321". Filed 2026-10-28 (r1207), proposed by the performance manager from item 318's diagnosis. Nobody's call — a method addition, after 0.3.4.**

Depends on: 318
Landed: slice 1 (`2adcd23`, r1220).

Item 318 showed the light-cycle check (item 308's slice 2) reads llvmpipe's arena growth under Xvfb and passes on a real GPU, so the method asks for a whole-process cycle on a real GPU before each release — which today means Aria's screen.
The soak box draws on a real iGPU, so the cycle can run there as the soak's first phase, before the visible and hidden phases, with no screen of Aria's needed.

## The fix

`perf-soak` gains a light-cycle phase at the start (night → day → night → day, 180 s each, judged on the last 30 s, each repeat within 4 MiB of the first), reported in `soak.md` beside the growth verdict; the pinned phases follow as now.
Tests in `perf_test.py` on staged samples; the method and `budgets.md` say the cycle is read from the soak.

## The method (performance manager, 2026-10-28)

**What the phase counts:** the whole process, `Private_Dirty` + the GPU memory `perf.py` already reads as `gpu_kib` for the budgets (`drm-total-*` from the city's `fdinfo`, summed over each distinct driver and client), and a run whose GPU reading is 0 is refused, so the cycle and the growth verdict count the same thing; item 318's real-GPU measure, unchanged.

**How it runs:** before the pinned phases, the same city and desk, with `--set light=live` and the scene's clock scrubbed as item 308's check scrubs it (`]`), warm-up day then night → day → night → day, 180 s a phase, sampled every 10 s as the soak samples, judged on each phase's last 30 s, which must hold a slope under 0.1 MiB/s or the phase is reported as unsettled.
Then the city is restarted with the soak's pinned light, so the cycle's images and arenas cannot carry into the growth phases.

**Its verdict:** each repeat within 4 MiB of the first of its light, as item 318's check; `soak.md` gets a "Light cycle" table (phase, light, MiB, change from the first of its light, settled or not) and its own line in the verdict.
A cycle that fails makes the run "over" as a growth slope over 1 MiB an hour does, since a switch that keeps memory is growth in use; one that cannot be judged (a phase unsettled, the scrub key not taken) makes the run "not a measurement".

**What must be true of the box first:** the pre-flight (items 309, 319) checks that the city draws on the GPU, not llvmpipe: `GL_RENDERER` from the city's log, or `glxinfo -B` as the soak user on `:0`, must not name llvmpipe or softpipe, or the pre-flight fails, since a cycle read through llvmpipe is the false red item 318 found.

**Done when:** a soak on a real box writes the "Light cycle" table and line, a staged run in `perf_test.py` covers pass, over and unsettled, and `performance/method.md` step 8 says the cycle is the soak's first phase, which the performance manager writes.

## The 0.4.0 soak's cycle (item session, 2026-11-04)

The first real-box run, server 3105798 (i5-12500, Mesa on the UHD 770), from 2026-11-03 09:51.
The laptop rebooted at about 18:11 and its runner died, so the soak's end and `soak.md` were not fetched; the cycle's samples were already on the laptop, complete, in `~/.local/state/botropolis-perf/soak-20261103-094734/cycle/`.
Judged from them by `perf.py soak-verdict --cycle`:

| phase | light | MiB | change from the first of its light | settled |
| --- | --- | --- | --- | --- |
| warm-up day | day | 218.9 | - | yes |
| first night | night | 219.7 | +0.0 | yes |
| first day | day | 220.0 | +0.0 | yes |
| second night | night | 219.8 | +0.2 | yes |
| second day | day | 220.3 | +0.3 | yes |

Every press was taken with the city focused, and the renderer was the GPU's, not llvmpipe.
So the cycle reads a pass on the whole process, `Private_Dirty` + GPU.
**That the light switched is unproven:** GPU memory holds at about 73 MiB with no step at either nightfall, where item 318's real-GPU run stepped about 6 MiB at the first, so a city that ignored `]` would read the same.
The growth verdict is not a measurement only because the run's end never reached the laptop.

**The proof is slice 2** (manager, 2026-11-04): a frame on the box's private display at each phase, harness only, since 0.4.0 is frozen.
The city logging its light change can be its own item later, if the frames are not enough.

## Decided

- **Slice 2's design and test tree** (manager, 2026-11-04): approved, including the gate in `lib/xin.py` that refuses an empty display, `:0` or `:0.0` on any machine without the soak box's marker, which also closes slice 1's hazard of pressing keys on whatever screen `perf-soak` was given.
- **The frames are report-only until a box gives a number** (manager, 2026-11-04): each frame's mean luminance and each night's ratio to the day before go in `busy.txt` and the Light cycle table, and the verdict says "light switch: unproven, no bound yet" rather than fail the cycle.
  A missing or refused frame is still not a measurement.
  75% stays in the code as the documented candidate, not as the gate; the bound is set from the first box run's data and goes to Aria, since a limit is hers.
