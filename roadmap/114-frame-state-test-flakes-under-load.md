# 114. The private-state acceptance test fails under load and leaves a directory behind

**Fixed 2026-10-18 (`e6c8539`, r638). Filed 2026-10-18 (r609), from what item 109 found. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`66da47e`, r618).
Landed: slice 2 (`d79558f`, r621).
Landed: slice 3 (`5a50f4e`, r625).
Landed: slice 4 (`e6c8539`, r638).

`TestFrameRunsKeepTheirOwnState`, item 111's acceptance test for frame and `--home` runs keeping a private state directory, failed once in a full `make test` run in item 109's worktree and left a `botropolis-state-*` directory in the temporary directory; it passed four times in a row run alone.
So under load something — most likely the run exiting before its private directory's cleanup finishes, or the test reading the directory before the child has removed it — races.

A test that fails one time in many is found, not retried (item 104's flaky unstage was a real bug in `demo.Unstage`).
And a frame run that leaves its private state behind is the leak item 111 exists to prevent, so the fix may belong in `pkg/statedir`'s cleanup rather than in the test.

## Done when

The cause is named in this item, the test passes `-count=50` under `make test`'s load, and no run leaves a `botropolis-state-*` directory behind.

## Answered while building

- **A likely cause** (item 113's session, 2026-10-18): `pkg/render/run.go` calls `os.Exit(0)` from a goroutine as soon as Ebitengine's `Run` returns, which can beat the caller's deferred removal of the private state directory; the `--headless` case is the one seen failing. Confirm it, then make the exit wait for cleanup.
- **The cause, confirmed** (item 114's session, 2026-10-18): `run.go`'s goroutine waited on a context that `Run`'s own deferred cancel cancels, so every scripted run, on returning, saved the layout — recreating the private directory — and called `os.Exit(0)`, racing the caller's cleanup (8 of 9 runs failed under load); and on SIGINT or SIGTERM it exited before `Run` returned, so a `--home` city interrupted with Ctrl-C always leaked its directory. The fix stops the game through `ebiten.Termination` instead of exiting from render.
- **A second signal exits at once** (manager, 2026-10-18): no timed backstop, which would be a silent fallback; the first signal stops gracefully, and a second exits immediately and says so, so a stalled loop never ignores Ctrl-C.
- **Slice 2, `--headless`**: its parent runs the city under `xvfb-run` with `exec.CommandContext`, which SIGKILLs `xvfb-run` on a signal, and `xvfb-run` traps nothing.
  A terminal's Ctrl-C reaches Xvfb too, so the city's display dies under it before it can clean up, and a SIGTERM to the parent alone leaves the city orphaned and running; both leave the directory.
  So the parent owns the private directory: it hands it to the child, and on a signal kills the child's process group, waits for it to be gone, then removes it.
- **Slice 2, the headless parent** (manager, 2026-10-18): a `--headless` city leaked on a signal too, its parent killing the virtual display or orphaning the child; the parent now owns the private directory, hands it to the child through an internal variable no user is meant to set, and on a signal stops only the process group it made for the child, waits, and removes the directory — never touching the terminal's own group.
- **Slice 2's two cautions** (the manager, 2026-10-18): the variable handing the directory to the child is `BOTROPOLIS_INTERNAL_PRIVATE_STATE`, is no setting, and is honoured only alongside the headless child's own marker; and the parent kills only the process group it made for the child, which each interrupt case checks with a sibling in the terminal's group that has to survive.
  That sibling check was not mutated red: killing the terminal's group from the city was refused as a permission, so it stands as written.
- **The sibling check stands unmutated** (Aria, 2026-10-18): the mutation that would have killed the parent's own process group was refused by the permission check, and she accepted the check as it is.
- **Slice 3, the feed** (the manager, from item 110, 2026-10-18): `Run` started the feed, which saves `sessions.json` into the state directory, and never waited for it, so a snapshot under way at shutdown could write into a removed private directory; item 110's leftover held `layout.json` and `sessions.json`.
  `Run` now cancels the feed and waits for it before returning (`startFeed`, unit-tested); the acceptance cases' check that no `botropolis-state-*` directory is left covers `sessions.json` with everything else in it.
- **Found on the way, not fixed here**: `make test-acceptance` reported `(cached)` after `pkg/render` and `pkg/app` had changed, because the acceptance binary is built by `go build` in `TestMain` and the package imports neither, so Go's test cache cannot see the code it tests. This item's slices were each checked with `go test -count=1 ./testing/acceptance/...`.
- **The soak after slice 3** (this item's session, 2026-10-18): 49 of 50 at load around 29; the one failure was a `--home` screenshot run that segfaulted (exit 139), GLFW's terminate unloading EGL under a live Mesa thread, and no run left a directory with a clean exit.
  Item 110's single `--script` failure at `cb0d03d` lost its output and stays unexplained; its 5.51 s fits either crash below.
- **An A/B under load** (this item's session, 2026-10-18), 60 `--home` screenshot runs each, side by side at load around 29: before slice 1, 3 segfaults, 7 exits of 1 and 13 clean exits that left the directory; after slice 3, 2 segfaults, 9 exits of 1 and none.
  So the slices did what they should, and the segfault predates them.
  The exits of 1 are the X server vanishing under the city: concurrent `xvfb-run -a` starts sharing a display, five of eight on `:484`. Xlib then calls C's `exit`, so no Go cleanup can run.
  Both are filed: the segfault as item 125 (*the city segfaults at teardown in Mesa*) and the collision as item 126 (*tests collide on Xvfb displays*).
- **Slice 4, best effort** (Aria, 2026-10-18: *"We should do our best to cleanup if possible, but obviously there's no 100% guarantee"*): each private directory names its owner, pid and start time, in `owner`, and `MakePrivate` first removes every one whose owner is gone, a reused pid included; one with no owner file is left alone.
  Both halves were mutated red.
- **Done when, revised** (the manager, 2026-10-18): the soak passes at load 30 except for runs that crash in Mesa or lose their X server, each counted and reported, and none of those leaves a directory behind for the next run.

## Closed

Four slices, all in botropolis.
Slice 1, `66da47e`: a signal stops the game through `ebiten.Termination` rather than exiting from `pkg/render`, and a second signal exits at once and says so (`pkg/interrupt`).
Slice 2, `d79558f`: a `--headless` city's parent owns the private directory, kills only the process group it made for the child, and removes the directory once that group is gone.
Slice 3, `5a50f4e`: `Run` waits for the feed, which writes `sessions.json`, before it returns.
Slice 4, `e6c8539`: each private directory names its owner, and the next run that makes one sweeps those whose owner is gone.
The user-facing change is in botropolis's changelog, `099e0de`.

The tests: `TestFrameRunsKeepTheirOwnState`, with four interrupt cases (`--home` and `--headless`, SIGINT to the terminal's group and SIGTERM to the process alone) and a case for a dead city's directory, plus `TestGameStop`, `TestContext`, `TestStartFeed` and `TestMakePrivateSweeps`.

The final soak, at load 30 to 43: 45 of 50 passes clean, and the 6 failing cases in the other 5 were all crashes outside the city's control, 4 runs that lost their X server (item 126) and 2 Mesa segfaults at teardown (item 125).
None of the clean exits left a directory.
Beside it, 1,980 runs shared one `TMPDIR`: 177 lost their X server and 21 segfaulted, and no directory was left for the next run.

**For Aria, a deviation from "Done when":** `-count=50` does not pass outright at load 30 on this machine, because of those two crashes, and the done-when was revised to count them and to require that each leaves nothing behind for the next run, which is what was soaked.
The sibling-group check in the interrupt cases was never mutated red, because the permission check refused the mutation; you accepted it as it stands.
