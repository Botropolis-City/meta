# 309. The soak box cannot hide the city, so four hours in, the soak stops being a measurement

**Fixed 2026-10-27 (`2c7c9e0`, r1143 of meta). Filed 2026-10-27 (r1192), from 0.3.3's first full soak. Nobody's call — a defect in the set-up.**

0.3.3's soak (server 3101537) ran its visible phase, then at 14,400 s `perf-city` reported *could not hide the window at 14400s (needs i3 and xprop); the rest of the run is NOT a hidden window*, and the city stayed at 45–48% of a core; `perf-soak` will end it as *not a measurement*.
`testing/machines/soak/setup` installs `x11-xserver-utils` (xset) but not `x11-utils` (`xprop`, `xwininfo`), so `perf-city` never found the window (`window_at_start=unknown`) nor checked the monitor (`monitor_at_start=unknown`).

## The fix

1. Install `x11-utils` beside `x11-xserver-utils`.
2. Before the soak starts, check as the soak user on `:0` that `xprop`, `xwininfo`, `i3-msg` and `xset` all run and that the city's window can be found and hidden and shown once, so a missing tool fails in the first minute, before anything is spent waiting, with the box kept or cancelled as the runner's failure rules say.
3. Tests: the set-up's package line names `x11-utils`; the pre-flight fails, naming the tool, when one is missing (a stubbed PATH); the runner stops before the soak when the pre-flight fails.

## Decided

- **The design and the test tree** (manager, 2026-10-27): approved, with one addition: a normal soak that will hide the window also refuses at the start, exit 2 and naming the tool, when one is missing, so no machine soaks for hours towards a run that cannot be a measurement.

## Fixed

`2c7c9e0` (r1143 of meta):

- `soak/setup` installs `x11-utils` beside `x11-xserver-utils`.
- `perf-soak --preflight` checks that `xprop`, `xwininfo`, `i3-msg` and `xset` are installed and reach the display,
  then opens the city for a minute through `perf-busy-city`, in the soak's light, and finds its window, hides it and shows it again.
  It exits 2 naming the missing tool or the failed step.
- A `perf-soak` that will hide the window runs the same tool check when it starts and exits 2 at once.
- `perf-city` counts a hide only once `xwininfo` says the window is not viewable, and takes `--show-after`; `perf-busy-city` passes it through.
- The runner runs the pre-flight as the soak user on `:0` after the copy and before the detached start.
  A failure collects the diagnostics and cancels the box, or keeps it with `KEEP_ON_FAILURE=1`; a pass is recorded in `machine.txt`.

The tests are in `testing/acceptance/`: `perf_soak_test.py` and `perf_busy_test.py` against a fake desk (stubs of the four tools that find, hide and show the stub city's window, or are missing or broken one at a time), and `machines_test.py` against the fake transport.
The pre-flight runs after the copy, not in the first minute, because it needs `perf-soak` and the build on the box: minutes after delivery, not hours.
It has not yet run on a real box; the next soak is its first.
