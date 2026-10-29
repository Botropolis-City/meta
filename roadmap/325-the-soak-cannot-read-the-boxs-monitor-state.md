# 325. The soak cannot read the box's monitor state, so a run that met every budget is stamped "not a measurement"

**Open. Filed 2026-10-29 (r1209), from 0.3.4's soak, the first to run to the end. Nobody's call — a defect in the tool.**

0.3.4's soak on server 3102814 met every budget (city +0.39 MiB an hour visible and +0.17 hidden, daemon −0.03 and +0.01, hidden at 14,400 s with the frames stopping there), and `perf-soak` still ended *not a measurement: the monitor was not on at the end (unknown)*: on the box, Xorg runs with no monitor to query, so `monitor_at_start` and `monitor_at_end` read `unknown`.
Aria shipped 0.3.4 on it, since the frame count (431,760 at 30 fps) shows the visible phase drew throughout.

## The fix

On a box with no physical monitor, the guard against a blank screen reads what it can: the X server's DPMS state is not the question there, so `perf-city` records that the display is a virtual one and judges the visible phase by its frame rate instead; the report then says which guard applied.
A test on the stub desk for each case.

## The method (performance manager, 2026-10-29)

The guard exists to refuse a visible phase that did not draw, and the frame count already measures that, so the verdict asks it directly.
1. `perf-city` records `monitor_*` as `none (virtual: forced EDID, no DPMS)` when the X server reports no DPMS, instead of `unknown`, and `unknown` stays only for a desk where the query failed.
2. `judge_soak` takes the visible phase as drawn when the frames by the hide are at least 90% of the phase's seconds times the city's frame cap (30), whatever the monitor reads; below that, "the visible phase drew too few frames" with the count, and a monitor reading `off` at either end still refuses the run.
3. `unknown` with frames at the cap passes with a note in `soak.md`, so a desk that cannot be queried is named, not failed.
Tests in `perf_test.py`: frames at the cap with `none`, with `unknown` and with `off`, and frames well under it.
