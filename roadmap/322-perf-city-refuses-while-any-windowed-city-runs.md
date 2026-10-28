# 322. perf-city refuses while any windowed city runs, so another session's test fails every perf tool test

**Open. Filed 2026-10-28 (r1207), from item 319's first `make test`. Nobody's call — a defect in a guard.**

`perf-city` refuses to start while any windowed city is running, which is right for a measurement on Aria's screen and wrong for the acceptance tests of `perf-soak` and `perf-busy-city`, which run on stub desks: item 319's `make test` saw 58 failures while item 318's 15-minute cycle had a real city open, and a clean rerun passed.
With several sessions running cities under the lock, every `make test` in meta is at the mercy of whoever has a window up.

## The fix

The refusal looks only at cities on the display the tool is about to use (`$DISPLAY`), never at cities on other displays or on a stub desk; and the acceptance tests give their stub desk its own display name so a real city elsewhere cannot touch them.
A test: with a city recorded on another display, `perf-city` starts; with one on its own display, it refuses as now.
