# 124. Two tests with wall-clock deadlines fail under load

**Fixed 2026-10-18 (`e2037b2`, r659; `783c579`, r660). Filed 2026-10-18 (r628), from what item 114 found. Nobody's call — a defect.**

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

## Closed

Reproduced first, as item 114 saw it: at a load around 75, the demo test failed 4 of 30 at 5.0 s and the daemon test 1 of 30.

- **Slice 1** (`e2037b2`, r659): `Sleepers` lists each stand-in with its start time, field 22 of `/proc/<pid>/stat`, and `Unstage` signals a pid only while its process started then.
  `TestUnstage` covers a stand-in still carrying its parent's name, which is the case that failed.
  The integration test now waits only on the reaper, behind a 30 s backstop: 50 of 50 at a load of about 100, the slowest in 0.06 s.
- **Slice 2** (`783c579`, r660): the daemon scans, starts watching, waits until it is watching, and scans again before it serves.
  `TestDaemonStart` makes the change inside that window and reads the snapshot once, with no clock.
  The `botropolisd` test waits on the daemon's update over `Subscribe`, behind a 30 s backstop: 50 of 50 at a load of about 77, the slowest in 0.59 s.
  The CHANGELOG says so under Fixed, because the window was there for every user at start-up.

For Aria: `botropolis/CLAUDE.md`'s gotcha says commits are signed over SSH with `id_ariavesta_sign_ed25519`, but every commit on main, these included, is signed with the GPG key `C39F068679829540` for `dev@ariavesta.com`.
The signatures are good; the gotcha looks out of date.
