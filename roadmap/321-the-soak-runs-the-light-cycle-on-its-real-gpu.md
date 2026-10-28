# 321. The soak box runs the light cycle as its first phase, on its real GPU

**Open. Filed 2026-10-28 (r1207), proposed by the performance manager from item 318's diagnosis. Nobody's call — a method addition, after 0.3.4.**

Depends on: 318

Item 318 showed the light-cycle check (item 308's slice 2) reads llvmpipe's arena growth under Xvfb and passes on a real GPU, so the method asks for a whole-process cycle on a real GPU before each release — which today means Aria's screen.
The soak box draws on a real iGPU, so the cycle can run there as the soak's first phase, before the visible and hidden phases, with no screen of Aria's needed.

## The fix

`perf-soak` gains a light-cycle phase at the start (night → day → night → day, 180 s each, judged on the last 30 s, each repeat within 4 MiB of the first), reported in `soak.md` beside the growth verdict; the pinned phases follow as now.
Tests in `perf_test.py` on staged samples; the method and `budgets.md` say the cycle is read from the soak.
