# 124. Two tests with wall-clock deadlines fail under load

**Open, in progress since 2026-10-18 in the session "item 124". Filed 2026-10-18 (r628), from what item 114 found. Nobody's call — a defect.**

Landed: slice 1 (`e2037b2`, r659).
Landed: slice 2 (`783c579`, r660).

In thirty uncached runs of the unit and integration suites at a load of 18 to 30, item 114 saw two tests fail on a fixed wall-clock deadline:

- `testing/integration/demo`, `TestStagedHomeLoadsAsTheScenarioSays` / "when the home is unstaged" / "it should leave no session alive" (`stage_test.go:94`): 4 of 30, each at exactly 5.00 s, its `assert.Eventually` deadline. It is the area of item 104's `demo.Unstage` fix.
- `cmd/botropolisd`, `TestRun` / "and a transcript changes on disk" / "it should pick it up" (`main_test.go:119`): 1 of 30, at its 3 s `Eventually`.

The testing rules ask for no wall-clock assertions; an `Eventually` with a fixed deadline is one, so under load it cannot tell a slow machine from a real bug like item 104's.
For each test, find which it is: if the code under test is waiting on something it could be told about (a process's exit, a file watcher's event), make the test wait on that signal rather than a clock; if it is genuinely slow under load, say why that is acceptable, and give it a deadline the suite cannot plausibly reach.

## Done when

Each test's cause is named here, and both pass `-count=50` at a load like the one they failed under.

## Answered while building

- **Both are missed signals, not slow machines** (item 124's session, 2026-10-18). Unstage read a stand-in's name before the kernel had renamed the child — 1,342 of 3,000 times even unloaded — and skipped it; it now matches the process's start time, recorded when the stand-in started, which also guards a reused pid. The daemon began serving before its directory watches were in place, so a change landing during start-up went unseen until the next write: a product bug, fixed by scanning, watching, waiting until watching, and scanning again before serving.
- **The deadlines** (manager, 2026-10-18): the daemon test waits on the daemon's own update rather than polling; both keep a 30 s backstop, out of reach when working, so a hang is a readable failure rather than the test runner's ten-minute panic.
