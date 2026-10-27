# 309. The soak box cannot hide the city, so four hours in, the soak stops being a measurement

**Open, in progress since 2026-10-27 in the session "item 309". Filed 2026-10-27 (r1192), from 0.3.3's first full soak. Nobody's call — a defect in the set-up.**

0.3.3's soak (server 3101537) ran its visible phase, then at 14,400 s `perf-city` reported *could not hide the window at 14400s (needs i3 and xprop); the rest of the run is NOT a hidden window*, and the city stayed at 45–48% of a core; `perf-soak` will end it as *not a measurement*.
`testing/machines/soak/setup` installs `x11-xserver-utils` (xset) but not `x11-utils` (`xprop`, `xwininfo`), so `perf-city` never found the window (`window_at_start=unknown`) nor checked the monitor (`monitor_at_start=unknown`).

## The fix

1. Install `x11-utils` beside `x11-xserver-utils`.
2. Before the soak starts, check as the soak user on `:0` that `xprop`, `xwininfo`, `i3-msg` and `xset` all run and that the city's window can be found and hidden and shown once, so a missing tool fails in the first minute, before anything is spent waiting, with the box kept or cancelled as the runner's failure rules say.
3. Tests: the set-up's package line names `x11-utils`; the pre-flight fails, naming the tool, when one is missing (a stubbed PATH); the runner stops before the soak when the pre-flight fails.
