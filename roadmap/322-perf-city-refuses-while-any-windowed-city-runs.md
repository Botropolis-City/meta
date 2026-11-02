# 322. perf-city refuses while any windowed city runs, so another session's test fails every perf tool test

**Fixed 2026-11-02 (`50ddaaa`, r1218 of meta). Filed 2026-10-28 (r1207), from item 319's first `make test`. Nobody's call — a defect in a guard.**

`perf-city` refuses to start while any windowed city is running, which is right for a measurement on Aria's screen and wrong for the acceptance tests of `perf-soak` and `perf-busy-city`, which run on stub desks: item 319's `make test` saw 58 failures while item 318's 15-minute cycle had a real city open, and a clean rerun passed.
With several sessions running cities under the lock, every `make test` in meta is at the mercy of whoever has a window up.

## The fix

The refusal looks only at cities on the display the tool is about to use (`$DISPLAY`), never at cities on other displays or on a stub desk; and the acceptance tests give their stub desk its own display name so a real city elsewhere cannot touch them.
A test: with a city recorded on another display, `perf-city` starts; with one on its own display, it refuses as now.

## Closed

`perf-city` reads each running windowed city's `DISPLAY` from `/proc/<pid>/environ` and refuses only when it matches its own; a city whose environment cannot be read still counts as a match, so a measurement never shares a screen by accident.
Each stub desk gets its own display, `:perf-test-<dir>`.
`testing/acceptance/perf_city_test.py` shows both halves, and `perf_busy_test.py` runs `perf-busy-city` to the end with a windowed city open on the caller's display, the case that gave item 319 its 58 failures.
The stub city never tripped the old guard, because `env` runs it as `bash`; the tests open a city through a symlink named `botropolis` so the guard sees it.
