# 114. The private-state acceptance test fails under load and leaves a directory behind

**Open, in progress since 2026-10-18 in the session "item 114". Filed 2026-10-18 (r609), from what item 109 found. Nobody's call — a defect.**

`TestFrameRunsKeepTheirOwnState`, item 111's acceptance test for frame and `--home` runs keeping a private state directory, failed once in a full `make test` run in item 109's worktree and left a `botropolis-state-*` directory in the temporary directory; it passed four times in a row run alone.
So under load something — most likely the run exiting before its private directory's cleanup finishes, or the test reading the directory before the child has removed it — races.

A test that fails one time in many is found, not retried (item 104's flaky unstage was a real bug in `demo.Unstage`).
And a frame run that leaves its private state behind is the leak item 111 exists to prevent, so the fix may belong in `pkg/statedir`'s cleanup rather than in the test.

## Done when

The cause is named in this item, the test passes `-count=50` under `make test`'s load, and no run leaves a `botropolis-state-*` directory behind.

## Answered while building

- **A likely cause** (item 113's session, 2026-10-18): `pkg/render/run.go` calls `os.Exit(0)` from a goroutine as soon as Ebitengine's `Run` returns, which can beat the caller's deferred removal of the private state directory; the `--headless` case is the one seen failing. Confirm it, then make the exit wait for cleanup.
