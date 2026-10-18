# 114. The private-state acceptance test fails under load and leaves a directory behind

**Open, in progress since 2026-10-18 in the session "item 114". Filed 2026-10-18 (r609), from what item 109 found. Nobody's call — a defect.**

Depends on: nothing
Landed: slice 1 (`66da47e`, r618).

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
